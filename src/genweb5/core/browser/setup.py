# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import IUserAdderPlugin

from plone import api
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import Interface

from genweb5.core.interfaces import IHomePage

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

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DXCT = False
else:
    HAS_DXCT = True
    from plone.dexterity.utils import createContentInContainer


logger = logging.getLogger(__name__)


LDAP_PASSWORD = os.environ.get('ldapbindpasswd', '')


class setupDX(BrowserView):
    """ Setup View that fixes p.a.ct front-page
    """

    def __call__(self):
        if HAS_DXCT:
            portal = getSite()
            pl = getToolByName(portal, 'portal_languages')
            if getattr(portal, 'front-page', False):
                portal.manage_delObjects('front-page')
                frontpage = createContentInContainer(
                    portal, 'Document', title=u"front-page", checkConstraints=False)
                alsoProvides(frontpage, IHomePage)
                frontpage.exclude_from_nav = True
                frontpage.language = pl.getDefaultLanguage()
                frontpage.reindexObject()
            # Set the default page to the homepage view
            portal.setDefaultPage('homepage')
            return self.request.response.redirect(portal.absolute_url())
        else:
            return 'This site has no p.a.contenttypes installed.'


class setupLDAPUPC(BrowserView):
    """ Configure LDAPUPC for Plone instance """

    def __call__(self):
        portal = getSite()

        if HAS_LDAP:
            try:
                manage_addPloneLDAPMultiPlugin(portal.acl_users, 'ldapUPC',
                                               title='ldapUPC', use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
                                               users_base='ou=Users,dc=upc,dc=edu', users_scope=2,
                                               roles='Authenticated', groups_base='ou=Groups,dc=upc,dc=edu',
                                               groups_scope=2, read_only=True, binduid='cn=ldap.serveis,ou=users,dc=upc,dc=edu', bindpwd=LDAP_PASSWORD,
                                               rdn_attr='cn', LDAP_server='ldap.upc.edu', encryption='SSHA')
                portal.acl_users.ldapUPC.acl_users.manage_edit('ldapUPC', 'cn', 'cn', 'ou=Users,dc=upc,dc=edu', 2, 'Authenticated',
                                                               'ou=Groups,dc=upc,dc=edu', 2, 'cn=ldap.serveis,ou=users,dc=upc,dc=edu', LDAP_PASSWORD, 1, 'cn',
                                                               'top,person', 0, 0, 'SSHA', 1, '')
                plugin = portal.acl_users['ldapUPC']

                plugin.manage_activateInterfaces(
                    ['IGroupEnumerationPlugin', 'IGroupsPlugin', 'IGroupIntrospection', 'IAuthenticationPlugin', 'IUserEnumerationPlugin'])
                # Comentem la linia per a que no afegeixi
                # LDAPUserFolder.manage_addServer(portal.acl_users.ldapUPC.acl_users, 'ldap.upc.edu', '636', use_ssl=1)

                LDAPUserFolder.manage_deleteLDAPSchemaItems(
                    portal.acl_users.ldapUPC.acl_users, ldap_names=['sn'], REQUEST=None)
                LDAPUserFolder.manage_addLDAPSchemaItem(
                    portal.acl_users.ldapUPC.acl_users, ldap_name='sn', friendly_name='Last Name', public_name='name')

                # Move the ldapUPC to the top of the active plugins.
                # Otherwise member.getProperty('email') won't work properly.
                # from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
                # portal.acl_users.plugins.movePluginsUp(IPropertiesPlugin, ['ldapUPC'])
                # portal.acl_users.plugins.manage_movePluginsUp('IPropertiesPlugin', ['ldapUPC'], context.REQUEST.RESPONSE)

            except:
                logger.debug(
                    'Something bad happened and the LDAP has not been created properly')

            try:
                plugin = portal.acl_users['ldapUPC']
                plugin.ZCacheable_setManagerId('RAMCache')

                portal_role_manager = portal.acl_users['portal_role_manager']
                portal_role_manager.assignRolesToPrincipal(
                    ['Manager'], 'UPC.Plone.Admins')
                portal_role_manager.assignRolesToPrincipal(
                    ['Manager'], 'UPCnet.Plone.Admins')
                portal_role_manager.assignRolesToPrincipal(
                    ['Manager'], 'UPCnet.ATIC')

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


class setupLDAPExterns(BrowserView):
    """ Configure LDAPExterns for Plone instance """

    def __call__(self):

        if 'branch' not in self.request.form:
            raise ValueError("Mandatory parameter 'branch' was not specified")
        else:
            branch = self.request.form['branch']

            portal = getSite()

            # Delete the LDAPUPC if exists
            if getattr(portal.acl_users, 'ldapUPC', None):
                portal.acl_users.manage_delObjects('ldapUPC')

            # try:
            manage_addPloneLDAPMultiPlugin(portal.acl_users, 'ldapexterns',
                                           title='ldapexterns', use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
                                           users_base='ou=users,ou=' + branch + ',dc=upcnet,dc=es', users_scope=2,
                                           roles='Authenticated,Member', groups_base='ou=groups,ou=' + branch + ',dc=upcnet,dc=es',
                                           groups_scope=2, read_only=True, binduid='cn=ldap,ou=' + branch + ',dc=upcnet,dc=es', bindpwd=LDAP_PASSWORD,
                                           rdn_attr='cn', LDAP_server='ldap.upcnet.es', encryption='SSHA')

            portal.acl_users.ldapexterns.acl_users.manage_edit('ldapexterns', 'cn', 'cn', 'ou=users,ou=' + branch + ',dc=upcnet,dc=es', 2, 'Authenticated,Member',
                                                               'ou=groups,ou=' + branch + ',dc=upcnet,dc=es', 2, 'cn=ldap,ou='
                                                               + branch + ',dc=upcnet,dc=es', LDAP_PASSWORD, 1, 'cn',
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
                portal.acl_users.ldapexterns.acl_users, ldap_name='sn', friendly_name='Last Name', public_name='fullname')
            LDAPUserFolder.manage_addLDAPSchemaItem(
                portal.acl_users.ldapexterns.acl_users, ldap_name='cn', friendly_name='Canonical Name')

            # Update the preference of the plugins
            portal.acl_users.plugins.movePluginsUp(
                IUserAdderPlugin, ['ldapexterns'])
            portal.acl_users.plugins.movePluginsUp(
                IGroupManagement, ['ldapexterns'])

            # Add LDAP plugin cache
            plugin = portal.acl_users['ldapexterns']
            plugin.ZCacheable_setManagerId('RAMCache')

            # Configuracion por defecto de los grupos de LDAP de externs
            groups_query = u'(&(objectClass=groupOfUniqueNames))'
            user_groups_query = u'(&(objectClass=groupOfUniqueNames)(uniqueMember=%s))'
            api.portal.set_registry_record(
                'genweb5.controlpanel.core.IGenwebCoreControlPanelSettings.groups_query', groups_query)
            api.portal.set_registry_record(
                'genweb5.controlpanel.core.IGenwebCoreControlPanelSettings.user_groups_query', user_groups_query)

            return 'Done. groupOfUniqueNames in LDAP Controlpanel Search'


class setupLDAP(BrowserView):
    """ Configure basic LDAP for Plone instance """

    def __call__(self):
        portal = getSite()
        ldap_name = self.request.form.get('ldap_name', 'ldap')
        ldap_server = self.request.form.get('ldap_server')
        branch_name = self.request.form.get('branch_name')
        base_dn = self.request.form.get('base_dn')
        branch_admin_cn = self.request.form.get('branch_admin_cn')
        branch_admin_password = self.request.form.get('branch_admin_password')
        allow_manage_users = self.request.form.get('allow_manage_users', False)

        users_base = 'ou=users,ou={},{}'.format(branch_name, base_dn)
        groups_base = 'ou=groups,ou={},{}'.format(branch_name, base_dn)
        bind_uid = 'cn={},ou={},{}'.format(
            branch_admin_cn, branch_name, base_dn)

        # Delete if exists
        if getattr(portal.acl_users, ldap_name, None):
            portal.acl_users.manage_delObjects('ldapUPC')

        manage_addPloneLDAPMultiPlugin(
            portal.acl_users, ldap_name,
            use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
            rdn_attr='cn', encryption='SSHA', read_only=True,
            roles='Authenticated,Member', groups_scope=2, users_scope=2,
            title=ldap_name,
            LDAP_server=ldap_server,
            users_base=users_base,
            groups_base=groups_base,
            binduid=bind_uid,
            bindpwd=branch_admin_password)

        ldap_acl_users = getattr(portal.acl_users, ldap_name).acl_users
        ldap_acl_users.manage_edit(
            ldap_name, 'cn', 'cn', users_base, 2, 'Authenticated,Member',
            groups_base, 2, bind_uid, branch_admin_password, 1, 'cn',
            'top,person,inetOrgPerson', 0, 0, 'SSHA', 0, '')

        plugin = portal.acl_users[ldap_name]

        active_plugins = [
            'IAuthenticationPlugin', 'ICredentialsResetPlugin', 'IGroupEnumerationPlugin',
            'IGroupIntrospection', 'IGroupManagement', 'IGroupsPlugin',
            'IPropertiesPlugin', 'IRoleEnumerationPlugin', 'IRolesPlugin',
            'IUserAdderPlugin', 'IUserEnumerationPlugin']

        if allow_manage_users:
            active_plugins.append('IUserManagement')

        plugin.manage_activateInterfaces(active_plugins)

        # Redefine some schema properties

        LDAPUserFolder.manage_deleteLDAPSchemaItems(
            ldap_acl_users, ldap_names=['sn'], REQUEST=None)
        LDAPUserFolder.manage_deleteLDAPSchemaItems(
            ldap_acl_users, ldap_names=['cn'], REQUEST=None)
        LDAPUserFolder.manage_addLDAPSchemaItem(
            ldap_acl_users, ldap_name='sn', friendly_name='Last Name', public_name='fullname')
        LDAPUserFolder.manage_addLDAPSchemaItem(
            ldap_acl_users, ldap_name='cn', friendly_name='Canonical Name')

        # Update the preference of the plugins
        portal.acl_users.plugins.movePluginsUp(IUserAdderPlugin, [ldap_name])
        portal.acl_users.plugins.movePluginsUp(IGroupManagement, [ldap_name])

        # Add LDAP plugin cache
        plugin = portal.acl_users[ldap_name]
        plugin.ZCacheable_setManagerId('RAMCache')
        return 'Done.'
