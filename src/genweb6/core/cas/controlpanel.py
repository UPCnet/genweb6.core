# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from ftw.casauth.plugin import addCASAuthenticationPlugin
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from z3c.form import button
from zope import schema
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import Interface

from genweb6.core import _
from genweb6.core.cas import PLUGIN_CAS


class ICASSettings(Interface):
    """ Global CAS settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    enabled = schema.Bool(
        title=_(u"enabled"),
        description=_(u"help_enabled"),
        required=False,
        default=False,
    )

    url = schema.TextLine(
        title=_(u"cas_url"),
        description=_(u"help_cas_url"),
        required=False,
        default=u"",
    )

    app_name = schema.TextLine(
        title=_(u"app_name"),
        description=_(u"help_app_name"),
        required=False,
        default=u"genweb",
    )

    login_text_btn = schema.TextLine(
        title=_(u"login_text_btn"),
        description=_(u"help_login_text_btn"),
        required=False,
        default=u"",
    )


class CASSettingsForm(controlpanel.RegistryEditForm):

    schema = ICASSettings
    label = _(u'Identitat Digital Settings')

    def updateFields(self):
        super(CASSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(CASSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if data['enabled']:
            addPluginCAS(data['url'])
        else:
            deletePluginCAS()

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class CASSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CASSettingsForm


def addPluginCAS(url):
    portal = getSite()

    plugin = getattr(portal.acl_users, PLUGIN_CAS, None)
    if plugin:
        plugin.cas_server_url = url
    else:
        try:
            addCASAuthenticationPlugin(portal.acl_users, PLUGIN_CAS, title=PLUGIN_CAS, cas_server_url=url)
            plugin = portal.acl_users[PLUGIN_CAS]
            plugin.manage_activateInterfaces(['IAuthenticationPlugin', 'IChallengePlugin', 'IExtractionPlugin'])
        except:
            pass


def setupCAS(url, app_name, login_text_btn):
    registry = queryUtility(IRegistry)
    cas_settings = registry.forInterface(ICASSettings)
    cas_settings.enabled = True
    cas_settings.url = url
    cas_settings.app_name = app_name
    cas_settings.login_text_btn = login_text_btn

    addPluginCAS(url)


def deletePluginCAS():
    portal = getSite()

    try:
        portal.acl_users.manage_delObjects(PLUGIN_CAS)
    except:
        pass
