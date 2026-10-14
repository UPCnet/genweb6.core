# -*- coding: utf-8 -*-
"""
Vista que exporta en JSON todos los grupos con permisos asignados directamente
(no por herencia) en contenidos del portal, así como los grupos con roles
globales en acl_users/portal_role_manager y @@usergroup-groupprefs.
"""
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from plone import api

import json
import logging
import os
import time

logger = logging.getLogger('genweb6.core.export_group_permissions')

# Grupos internos de Plone/Zope que no son de interés para la exportación
PLONE_BUILTIN_GROUPS = frozenset({
    'Administrators',
    'Reviewers',
    'Site Administrators',
    'AuthenticatedUsers',
    'Authenticated',
    'Anonymous',
    'Everyone',
})


class ExportGroupPermissionsView(BrowserView):
    """
    Exporta en JSON:
      1. Grupos con permisos asignados localmente (no heredados) en contenidos.
      2. Grupos con roles globales en acl_users/portal_role_manager.
      3. Grupos con roles globales visibles en @@usergroup-groupprefs.

    URL de acceso: @@export-group-permissions

    Estrategia para evitar LDAP SIZELIMIT:
    - NO se usa searchGroups() (lanza cn=* contra LDAP → SIZELIMIT).
    - Los principal_id se recogen de las fuentes locales (__ac_local_roles__
      y portal_role_manager._principal_roles) y luego se verifica cada uno
      individualmente con getGroupById(), que no hace búsquedas masivas.
    """

    def __call__(self):
        portal = api.portal.get()
        site_id = portal.getId()
        parent_id = portal.aq_parent.getId()
        if parent_id:
            filename = '{}-{}.json'.format(parent_id, site_id)
        else:
            filename = '{}.json'.format(site_id)

        data = self._build_export()
        payload = json.dumps(data, indent=2, ensure_ascii=False)

        # Guardar en disco en cfg.clienthome (var/instance/ en buildout),
        # igual que collective.exportimport cuando no hay directorio central.
        directory = getConfiguration().clienthome
        logger.info('Guardando en directorio: %s', directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(payload)
        logger.info('Fichero guardado en: %s', filepath)

        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="{}"'.format(filename),
        )
        return payload

    # ------------------------------------------------------------------
    # Helper: comprueba si un principal_id corresponde a un grupo
    # ------------------------------------------------------------------

    def _is_group(self, principal_id, acl_users, cache):
        """
        Devuelve True si principal_id es un grupo no interno de Plone.

        Usa getGroupById() sobre el ID concreto — no hace búsquedas
        masivas LDAP — y cachea el resultado para evitar llamadas repetidas.
        """
        if principal_id in cache:
            return cache[principal_id]
        if principal_id in PLONE_BUILTIN_GROUPS:
            cache[principal_id] = False
            return False
        try:
            result = acl_users.getGroupById(principal_id) is not None
        except Exception:
            result = False
        cache[principal_id] = result
        return result

    # ------------------------------------------------------------------
    # 1. Permisos locales en contenidos (sin herencia)
    # ------------------------------------------------------------------

    def _get_content_local_roles(self, acl_users, group_cache):
        """
        Recorre todos los objetos del catálogo y recupera los roles asignados
        directamente en cada objeto que pertenezcan a grupos.

        Usa get_local_roles() — la misma API que usa @@sharing — que devuelve
        solo los roles asignados explícitamente en el propio objeto, sin herencia.
        El filtro acl_users.getGroupById(pid) descarta usuarios individuales y
        grupos internos de Plone (ya excluidos por _is_group / PLONE_BUILTIN_GROUPS).
        """
        portal = api.portal.get()
        catalog = api.portal.get_tool('portal_catalog')
        results = []

        # Raíz del portal (no indexada en el catálogo)
        self._append_group_local_roles(portal, acl_users, group_cache, results)

        brains = catalog.unrestrictedSearchResults(path="/")
        total = len(brains)
        logger.info('  Total objetos en catálogo: %d', total)

        for idx, brain in enumerate(brains, start=1):
            if idx % 500 == 0 or idx == total:
                pct = round(idx * 500 / total, 1) if total else 500
                logger.info('  Progreso: %d/%d (%.1f%%)', idx, total, pct)
            try:
                obj = brain.getObject()
            except Exception as exc:
                logger.warning('  No se pudo obtener el objeto %s: %s', brain.getPath(), exc)
                continue
            self._append_group_local_roles(obj, acl_users, group_cache, results)

        return results

    def _append_group_local_roles(self, obj, acl_users, group_cache, results):
        """Extrae los roles locales de grupos de un objeto y los añade a results."""
        try:
            obj_path = '/'.join(obj.getPhysicalPath())
            local_roles = obj.get_local_roles()
        except Exception:
            return

        for pid, roles in local_roles:
            roles = [r for r in roles if r]
            if not roles:
                continue
            if not self._is_group(pid, acl_users, group_cache):
                continue
            results.append({
                'path': obj_path,
                'grupo': pid,
                'permisos_asignados': sorted(roles),
            })

    # ------------------------------------------------------------------
    # 2. Roles globales en portal_role_manager
    # ------------------------------------------------------------------

    def _get_portal_role_manager_roles(self, acl_users, group_cache):
        """
        Lee los roles globales asignados a grupos desde
        acl_users/portal_role_manager.

        Accede a _principal_roles directamente porque listRoleAssignments()
        no está disponible en todas las versiones del plugin.
        """
        results = []

        try:
            prm = acl_users['portal_role_manager']
        except (KeyError, AttributeError):
            logger.warning('No se encontró portal_role_manager en acl_users')
            return results

        # _principal_roles: {principal_id: {role_id: True/1, ...}}
        principal_roles = getattr(prm, '_principal_roles', {})
        if not principal_roles:
            # Fallback: iterar con getRolesForPrincipal si hay método disponible
            logger.warning('portal_role_manager._principal_roles está vacío o no existe')
            return results

        for principal_id, roles_raw in principal_roles.items():
            # _principal_roles puede ser {id: {role: True}} o {id: (role1, role2)}
            if isinstance(roles_raw, dict):
                roles = [r for r, active in roles_raw.items() if active]
            elif isinstance(roles_raw, (list, tuple)):
                roles = list(roles_raw)
            else:
                roles = []
            if not roles:
                continue
            if not self._is_group(principal_id, acl_users, group_cache):
                continue
            results.append({
                'path': 'acl_users/portal_role_manager/manage_roles',
                'grupo': principal_id,
                'permisos_asignados': sorted(roles),
            })

        return results

    # ------------------------------------------------------------------
    # 3. Roles globales visibles en @@usergroup-groupprefs
    # ------------------------------------------------------------------

    def _get_usergroup_groupprefs_roles(self, acl_users, group_cache):
        """
        Recupera los roles globales de cada grupo tal como los muestra
        @@usergroup-groupprefs: a través de group.getRoles() en acl_users.

        Solo itera sobre los principal_id ya conocidos como grupos (en
        group_cache) para evitar cualquier búsqueda masiva LDAP.
        """
        results = []

        for principal_id, is_group in group_cache.items():
            if not is_group:
                continue
            try:
                group_obj = acl_users.getGroupById(principal_id)
            except Exception:
                continue

            if group_obj is None:
                continue

            try:
                roles = list(group_obj.getRoles())
            except Exception:
                continue

            meaningful_roles = [r for r in roles if r not in ('Authenticated', 'Anonymous')]
            if not meaningful_roles:
                continue

            results.append({
                'path': '@@usergroup-groupprefs',
                'grupo': principal_id,
                'permisos_asignados': sorted(meaningful_roles),
            })

        return results

    # ------------------------------------------------------------------
    # Construcción del export completo
    # ------------------------------------------------------------------

    def _build_export(self):
        acl_users = api.portal.get().acl_users
        # Cache compartido: {principal_id: True/False}
        # Evita llamadas repetidas a getGroupById() para el mismo ID.
        group_cache = {}

        t_start = time.time()
        logger.info('=== export-group-permissions: inicio ===')

        t0 = time.time()
        logger.info('[1/3] Escaneando roles locales en contenidos...')
        content_entries = self._get_content_local_roles(acl_users, group_cache)
        logger.info('[1/3] Completado: %d entradas encontradas. (%.1fs)', len(content_entries), time.time() - t0)

        t0 = time.time()
        logger.info('[2/3] Leyendo portal_role_manager...')
        prm_entries = self._get_portal_role_manager_roles(acl_users, group_cache)
        logger.info('[2/3] Completado: %d entradas encontradas. (%.1fs)', len(prm_entries), time.time() - t0)

        t0 = time.time()
        logger.info('[3/3] Leyendo usergroup-groupprefs...')
        groupprefs_entries = self._get_usergroup_groupprefs_roles(acl_users, group_cache)
        logger.info('[3/3] Completado: %d entradas encontradas. (%.1fs)', len(groupprefs_entries), time.time() - t0)

        all_entries = content_entries + prm_entries + groupprefs_entries

        # Agrupa por (path, grupo) para evitar duplicados entre fuentes
        merged = {}
        for entry in all_entries:
            key = (entry['path'], entry['grupo'])
            if key not in merged:
                merged[key] = {
                    'path': entry['path'],
                    'grupo': entry['grupo'],
                    'permisos_asignados': set(entry['permisos_asignados']),
                }
            else:
                merged[key]['permisos_asignados'].update(entry['permisos_asignados'])

        output = [
            {
                'path': v['path'],
                'grupo': v['grupo'],
                'permisos_asignados': sorted(v['permisos_asignados']),
            }
            for v in merged.values()
        ]

        output.sort(key=lambda x: (x['path'], x['grupo']))

        logger.info('=== export-group-permissions: fin — %d entradas en total (%.1fs) ===', len(output), time.time() - t_start)
        return output
