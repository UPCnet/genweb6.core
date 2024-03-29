# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import IUserAdderPlugin

from plone.base.interfaces import IUserGroupsSettingsSchema
from zope.component import getAdapter

from plone import api
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import alsoProvides

import os
import logging
import pkg_resources

try:
    pkg_resources.get_distribution('Products.PloneLDAP')
except pkg_resources.DistributionNotFound:
    HAS_LDAP = False
else:
    HAS_LDAP = True
    from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
    from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder


logger = logging.getLogger(__name__)


LDAP_PASSWORD = os.environ.get('ldapbindpasswd', '')


def setSetupLDAPUPC():
    try:
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(getRequest(), IDisableCSRFProtection)
    except:
        pass

    portal = getSite()

    if HAS_LDAP:
        try:
            # Delete the ldapUPC if exists
            if getattr(portal.acl_users, 'ldapUPC', None):
                portal.acl_users.manage_delObjects('ldapUPC')

            # Delete the ldapexterns if exists
            if getattr(portal.acl_users, 'ldapexterns', None):
                portal.acl_users.manage_delObjects('ldapexterns')

            manage_addPloneLDAPMultiPlugin(
                portal.acl_users, 'ldapUPC', title='ldapUPC',
                LDAP_server='ldap.upc.edu', login_attr='cn', uid_attr='cn',
                users_base='ou=Users,dc=upc,dc=edu', users_scope=2,
                roles='Authenticated', groups_base='ou=Groups,dc=upc,dc=edu',
                groups_scope=2, binduid='cn=ldap.serveis,ou=users,dc=upc,dc=edu',
                bindpwd=LDAP_PASSWORD, binduid_usage=1, rdn_attr='cn', local_groups=0,
                use_ssl=1, encryption='SSHA', read_only=True)

            portal.acl_users.ldapUPC.acl_users.manage_edit(
                'ldapUPC', 'cn', 'cn', 'ou=Users,dc=upc,dc=edu', 2, 'Authenticated',
                'ou=Groups,dc=upc,dc=edu', 2, 'cn=ldap.serveis,ou=users,dc=upc,dc=edu',
                LDAP_PASSWORD, 1, 'cn', 'top,person', 0, 0, 'SSHA', 1, '')

            plugin = portal.acl_users['ldapUPC']

            plugin.manage_activateInterfaces(['IGroupEnumerationPlugin',
                                              'IGroupsPlugin',
                                              'IGroupIntrospection',
                                              'IAuthenticationPlugin',
                                              'IUserEnumerationPlugin'])

            # Comentem la linia per a que no afegeixi
            # LDAPUserFolder.manage_addServer(portal.acl_users.ldapUPC.acl_users, 'ldap.upc.edu', '636', use_ssl=1)

            LDAPUserFolder.manage_deleteLDAPSchemaItems(
                portal.acl_users.ldapUPC.acl_users, ldap_names=['sn'], REQUEST=None)

            LDAPUserFolder.manage_addLDAPSchemaItem(
                portal.acl_users.ldapUPC.acl_users, ldap_name='sn',
                friendly_name='Last Name', public_name='name')

            # Move the ldapUPC to the top of the active plugins.
            # Otherwise member.getProperty('email') won't work properly.
            # from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
            # portal.acl_users.plugins.movePluginsUp(IPropertiesPlugin, ['ldapUPC'])
            # portal.acl_users.plugins.manage_movePluginsUp('IPropertiesPlugin', ['ldapUPC'], context.REQUEST.RESPONSE)

            getAdapter(portal, IUserGroupsSettingsSchema).set_many_groups(True)
            getAdapter(portal, IUserGroupsSettingsSchema).set_many_users(True)

        except:
            logger.debug(
                'Something bad happened and the LDAP has not been created properly')

        try:
            plugin = portal.acl_users['ldapUPC']
            plugin.ZCacheable_setManagerId('RAMCache')

            portal_role_manager = portal.acl_users['portal_role_manager']
            portal_role_manager.assignRolesToPrincipal(['Manager'], 'UPC.Plone.Admins')
            portal_role_manager.assignRolesToPrincipal(
                ['Manager'], 'UPCnet.Plone.Admins')
            portal_role_manager.assignRolesToPrincipal(['Manager'], 'UPCnet.ATIC')

        except:
            logger.debug(
                'Something bad happened and the LDAP has not been configured properly')

    else:
        logger.debug(
            'You do not have LDAP libraries in your current buildout configuration. POSOK.')

        # try:
        # Fora el sistema de cookies que fan buscar al LDAP cn=*
        #     portal.acl_users.manage_delObjects('credentials_cookie_auth')
        # except:
        #     pass


class setupLDAPUPC(BrowserView):
    """
Configura el LDAP UPC
    """

    def __call__(self):
        setSetupLDAPUPC()


class setupLDAPExterns(BrowserView):
    """
Configura el LDAPExterns

Paràmetre:
- branch
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(getRequest(), IDisableCSRFProtection)
        except:
            pass

        if 'branch' not in self.request.form:
            raise ValueError("Mandatory parameter 'branch' was not specified")
        else:
            branch = self.request.form['branch']

            portal = getSite()

            # Delete the LDAPUPC if exists
            if getattr(portal.acl_users, 'ldapUPC', None):
                portal.acl_users.manage_delObjects('ldapUPC')

            # Delete the ldapexterns if exists
            if getattr(portal.acl_users, 'ldapexterns', None):
                portal.acl_users.manage_delObjects('ldapexterns')

            # try:
            manage_addPloneLDAPMultiPlugin(
                portal.acl_users, 'ldapexterns', title='ldapexterns',
                LDAP_server='ldap.upcnet.es', login_attr='cn', uid_attr='cn',
                users_base='ou=users,ou=' + branch + ',dc=upcnet,dc=es', users_scope=2,
                roles='Authenticated', groups_base='ou=groups,ou=' + branch +
                ',dc=upcnet,dc=es', groups_scope=2, binduid='cn=ldap,ou=' + branch +
                ',dc=upcnet,dc=es', bindpwd=LDAP_PASSWORD, binduid_usage=1,
                rdn_attr='cn', local_groups=0, use_ssl=1, encryption='SSHA',
                read_only=True)

            portal.acl_users.ldapexterns.acl_users.manage_edit(
                'ldapexterns', 'cn', 'cn', 'ou=users,ou=upcnet,dc=upcnet,dc=es', 2,
                'Authenticated,Member', 'ou=groups,ou=upcnet,dc=upcnet,dc=es', 2,
                'cn=ldap,ou=upcnet,dc=upcnet,dc=es', LDAP_PASSWORD, 1, 'cn',
                'top,person,inetOrgPerson', 0, 0, 'SSHA', 0, '')

            plugin = portal.acl_users['ldapexterns']

            # Activate plugins (all)
            plugin.manage_activateInterfaces(['IAuthenticationPlugin',
                                              'ICredentialsResetPlugin',
                                              'IGroupEnumerationPlugin',
                                              'IGroupIntrospection',
                                              'IGroupManagement',
                                              'IGroupsPlugin',
                                              'IUserAdderPlugin',
                                              'IUserEnumerationPlugin',
                                              'IUserManagement',
                                              'IPropertiesPlugin',
                                              'IRoleEnumerationPlugin',
                                              'IRolesPlugin'])

            # Redefine some schema properties
            LDAPUserFolder.manage_deleteLDAPSchemaItems(
                portal.acl_users.ldapexterns.acl_users, ldap_names=['sn'], REQUEST=None)

            LDAPUserFolder.manage_deleteLDAPSchemaItems(
                portal.acl_users.ldapexterns.acl_users, ldap_names=['cn'], REQUEST=None)

            LDAPUserFolder.manage_addLDAPSchemaItem(
                portal.acl_users.ldapexterns.acl_users, ldap_name='sn',
                friendly_name='Last Name', public_name='fullname')

            LDAPUserFolder.manage_addLDAPSchemaItem(
                portal.acl_users.ldapexterns.acl_users, ldap_name='cn',
                friendly_name='Canonical Name')

            # Update the preference of the plugins
            portal.acl_users.plugins.movePluginsUp(IUserAdderPlugin, ['ldapexterns'])
            portal.acl_users.plugins.movePluginsUp(IGroupManagement, ['ldapexterns'])

            # Add LDAP plugin cache
            plugin = portal.acl_users['ldapexterns']
            plugin.ZCacheable_setManagerId('RAMCache')

            # Configuracion por defecto de los grupos de LDAP de externs
            groups_query = u'(&(objectClass=groupOfUniqueNames))'
            user_groups_query = u'(&(objectClass=groupOfUniqueNames)(uniqueMember=%s))'

            api.portal.set_registry_record(
                'genweb6.controlpanel.core.IGenwebCoreControlPanelSettings.groups_query',
                groups_query)

            api.portal.set_registry_record(
                'genweb6.controlpanel.core.IGenwebCoreControlPanelSettings.user_groups_query',
                user_groups_query)

            return 'Done. groupOfUniqueNames in LDAP Controlpanel Search'


class setupLDAP(BrowserView):
    """
Configura un LDAP básic

Paràmetres:
- ldap_name
- ldap_server
- branch_name
- base_dn
- branch_admin_cn
- branch_admin_password
- allow_manage_users
    """

    def __call__(self):
        request = getRequest()

        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(request, IDisableCSRFProtection)
        except:
            pass

        portal = getSite()
        ldap_name = request.form.get('ldap_name', 'ldap')
        ldap_server = request.form.get('ldap_server')
        branch_name = request.form.get('branch_name')
        base_dn = request.form.get('base_dn')
        branch_admin_cn = request.form.get('branch_admin_cn')
        branch_admin_password = request.form.get('branch_admin_password')
        allow_manage_users = request.form.get('allow_manage_users', False)

        users_base = 'ou=users,ou={},{}'.format(branch_name, base_dn)
        groups_base = 'ou=groups,ou={},{}'.format(branch_name, base_dn)
        bind_uid = 'cn={},ou={},{}'.format(branch_admin_cn, branch_name, base_dn)

        # Delete the ldapUPC if exists
        if getattr(portal.acl_users, 'ldapUPC', None):
            portal.acl_users.manage_delObjects('ldapUPC')

        # Delete the ldapexterns if exists
        if getattr(portal.acl_users, 'ldapexterns', None):
            portal.acl_users.manage_delObjects('ldapexterns')

        # Delete if exists
        if getattr(portal.acl_users, ldap_name, None):
            portal.acl_users.manage_delObjects(ldap_name)

        manage_addPloneLDAPMultiPlugin(
            portal.acl_users, ldap_name,
            title=ldap_name, LDAP_server=ldap_server, login_attr='cn', uid_attr='cn',
            users_base=users_base, users_scope=2, roles='Authenticated',
            groups_base=groups_base, groups_scope=2,
            binduid=bind_uid, bindpwd=branch_admin_password, binduid_usage=1,
            rdn_attr='cn', local_groups=0, use_ssl=1, encryption='SSHA', read_only=True)

        ldap_acl_users = getattr(portal.acl_users, ldap_name).acl_users

        ldap_acl_users.manage_edit(
            ldap_name, 'cn', 'cn', users_base, 2, 'Authenticated,Member',
            groups_base, 2, bind_uid, branch_admin_password, 1, 'cn',
            'top,person,inetOrgPerson', 0, 0, 'SSHA', 0, '')

        plugin = portal.acl_users[ldap_name]

        active_plugins = ['IAuthenticationPlugin',
                          'ICredentialsResetPlugin',
                          'IGroupEnumerationPlugin',
                          'IGroupIntrospection',
                          'IGroupManagement',
                          'IGroupsPlugin',
                          'IPropertiesPlugin',
                          'IRoleEnumerationPlugin',
                          'IRolesPlugin',
                          'IUserAdderPlugin',
                          'IUserEnumerationPlugin']

        if allow_manage_users:
            active_plugins.append('IUserManagement')

        plugin.manage_activateInterfaces(active_plugins)

        # Redefine some schema properties
        LDAPUserFolder.manage_deleteLDAPSchemaItems(
            ldap_acl_users, ldap_names=['sn'], REQUEST=None)

        LDAPUserFolder.manage_deleteLDAPSchemaItems(
            ldap_acl_users, ldap_names=['cn'], REQUEST=None)

        LDAPUserFolder.manage_addLDAPSchemaItem(
            ldap_acl_users, ldap_name='sn', friendly_name='Last Name',
            public_name='fullname')

        LDAPUserFolder.manage_addLDAPSchemaItem(
            ldap_acl_users, ldap_name='cn', friendly_name='Canonical Name')

        # Update the preference of the plugins
        portal.acl_users.plugins.movePluginsUp(IUserAdderPlugin, [ldap_name])
        portal.acl_users.plugins.movePluginsUp(IGroupManagement, [ldap_name])

        # Add LDAP plugin cache
        plugin = portal.acl_users[ldap_name]
        plugin.ZCacheable_setManagerId('RAMCache')
        return 'Done.'
