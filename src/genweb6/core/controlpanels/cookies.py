# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from z3c.form import button
from z3c.form.browser.text import TextWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField

from genweb6.core import _


class ICookiesSettingsPreviewWidget(ITextWidget):
    pass


@implementer_only(ICookiesSettingsPreviewWidget)
class CookiesSettingsPreviewWidget(TextWidget):

    klass = u'cookies_settings-preview-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def CookiesSettingsPreviewFieldWidget(field, request):
    return FieldWidget(field, CookiesSettingsPreviewWidget(request))


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

    directives.widget('preview', CookiesSettingsPreviewWidget)
    preview = schema.Text(title=_(u""), required=False)


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
