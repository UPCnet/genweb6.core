# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


class ILoginSettings(model.Schema):

    change_password_url = schema.TextLine(
        title=_(u"URL Canvi de contrasenya"),
        required=False,
        default="",
    )


class LoginSettingsForm(controlpanel.RegistryEditForm):

    schema = ILoginSettings
    label = _(u'Login Settings')

    def updateFields(self):
        super(LoginSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(LoginSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class LoginSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LoginSettingsForm
