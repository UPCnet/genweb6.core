# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.dexterity.interfaces import IDexteritySchema
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
from zope.ramcache import ram as ramcache
from zope.schema.interfaces import IField
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.purge import purge_varnish_paths


class IColoqiaControlpanelJSWidget(ITextWidget):
    pass


@implementer_only(IColoqiaControlpanelJSWidget)
class ColoqiaControlpanelJSWidget(TextWidget):

    klass = u'coloqia_controlpanel-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def ColoqiaControlpanelJSFieldWidget(field, request):
    return FieldWidget(field, ColoqiaControlpanelJSWidget(request))


coloqiaModeVocabulary = SimpleVocabulary([
    SimpleTerm(value="script", title=_(u'Script')),
    SimpleTerm(value="url", title=_(u'Obrir en una pestanya nova'))])


class IColoqiaSettings(model.Schema, IDexteritySchema):

    coloqia_enabled = schema.Bool(
        title=_(u'Activar Coloq.ia'),
        description=_(u'Marca per mostrar Coloq.ia a les vistes de visualització del web'),
        required=False,
        default=False,
    )

    coloqia_mode = schema.Choice(
        title=_(u'Mode de funcionament'),
        required=True,
        vocabulary=coloqiaModeVocabulary,
        default='script',
    )

    coloqia_script = schema.Text(
        title=_(u'Script de Coloq.ia'),
        description=_(u"Codi que s'insereix al body, fora del footer i per sota d'aquest."),
        required=False,
    )

    coloqia_url = schema.URI(
        title=_(u'URL de Coloq.ia'),
        description=_(u"Enllaç que s'obre en una pestanya nova en clicar la icona flotant de Coloq.ia."),
        required=False,
    )

    directives.widget('js', ColoqiaControlpanelJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)


class ColoqiaSettingsForm(controlpanel.RegistryEditForm):

    schema = IColoqiaSettings
    label = _(u'Coloq.ia Settings')

    def updateFields(self):
        super(ColoqiaSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(ColoqiaSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        ramcache.caches.clear()
        self.applyChanges(data)

        paths = []
        paths.append('/_purge_all')

        purge_varnish_paths(self, paths)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class ColoqiaSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ColoqiaSettingsForm
