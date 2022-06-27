# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


class IFooterSettings(model.Schema):

    read_permission(signatura_ca='genweb.superadmin')
    write_permission(signatura_ca='genweb.webmaster')
    signatura_ca = schema.TextLine(
        title=_(u"signatura_ca", default=u"Signatura [CA]"),
        description=_(u"help_signatura_ca", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_es='genweb.superadmin')
    write_permission(signatura_es='genweb.webmaster')
    signatura_es = schema.TextLine(
        title=_(u"signatura_es", default=u"Signatura [ES]"),
        description=_(u"help_signatura_es", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_en='genweb.superadmin')
    write_permission(signatura_en='genweb.webmaster')
    signatura_en = schema.TextLine(
        title=_(u"signatura_en", default=u"Signatura [EN]"),
        description=_(u"help_signatura_en", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )


class FooterSettingsForm(controlpanel.RegistryEditForm):

    schema = IFooterSettings
    label = _(u'Footer Settings')

    def updateFields(self):
        super(FooterSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(FooterSettingsForm, self).updateWidgets()

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


class FooterSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FooterSettingsForm
