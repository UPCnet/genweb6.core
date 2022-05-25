# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _

import logging

log = logging.getLogger('genweb6.upc')


class ICookiesSettings(model.Schema):

    disable = schema.Bool(
        title=_(u"Deshabilitar"),
        description=_(u"Deshabilitar el banner de les cookies"),
        required=False,
        default=True,
    )

    enable_alternative_text = schema.Bool(
        title=_(u"Habilita el texto alternativo"),
        description=_(u"Al marcar esta opción se pillara la información de los siguientes campos de texto."),
        required=False,
        default=False,
    )

    directives.widget('alternative_text_ca', WysiwygFieldWidget)
    alternative_text_ca = schema.Text(
        title=_(u"Catalán"),
        description=_(u""),
        required=False,
    )

    directives.widget('alternative_text_es', WysiwygFieldWidget)
    alternative_text_es = schema.Text(
        title=_(u"Español"),
        description=_(u""),
        required=False,
    )

    directives.widget('alternative_text_en', WysiwygFieldWidget)
    alternative_text_en = schema.Text(
        title=_(u"Inglés"),
        description=_(u""),
        required=False,
    )


class CookiesSettingsForm(controlpanel.RegistryEditForm):

    schema = ICookiesSettings
    label = _(u'Cookies Settings')

    def updateFields(self):
        super(CookiesSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(CookiesSettingsForm, self).updateWidgets()

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


class CookiesSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CookiesSettingsForm
