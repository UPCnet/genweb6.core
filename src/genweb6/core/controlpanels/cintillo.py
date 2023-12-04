# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.ramcache import ram

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget
from genweb6.core.purge import purge_varnish_paths

class ICintilloSettings(model.Schema):

    active = schema.Bool(
        title=_(u"Publica el avis"),
        required=False
    )

    background_color = schema.TextLine(
        title=_(u"Color de fons de l'avís"),
        description=_(u"Introdueix el codi de color. Ex: #CC3300"),
        required=False
    )

    font_color = schema.TextLine(
        title=_(u"Color de la font de l'avís"),
        description=_(u"Introdueix el codi de color. Ex: #FFFFFF"),
        required=False
    )

    icon = schema.TextLine(
        title=_(u"Icona"),
        description=_(u"Icona que es mostrarà al costat del títol, podeu trobar tots els identificadors en el <a href='https://icons.getbootstrap.com/' target='_blank'>següent enllaç</a>. Ex: bi-exclamation-diamond"),
        required=False
    )

    directives.widget('fieldset_ca', FieldsetFieldWidget)
    fieldset_ca = schema.Text(
        default=_(u'Català'),
        required=False,
    )

    title_ca = schema.TextLine(
        title=_(u"Títol del l'avís"),
        required=False
    )

    text_ca = schema.Text(
        title=_(u"Text per l'avís"),
        description=_(u"Permet introduir el text que es veurà a l'avís"),
        required=False
    )

    directives.widget('fieldset_es', FieldsetFieldWidget)
    fieldset_es = schema.Text(
        default=_(u'Castellà'),
        required=False,
    )

    title_es = schema.TextLine(
        title=_(u"Títol del l'avís"),
        required=False
    )

    text_es = schema.Text(
        title=_(u"Text per l'avís"),
        description=_(u"Permet introduir el text que es veurà a l'avís"),
        required=False
    )

    directives.widget('fieldset_en', FieldsetFieldWidget)
    fieldset_en = schema.Text(
        default=_(u'Àngles'),
        required=False,
    )

    title_en = schema.TextLine(
        title=_(u"Títol del l'avís"),
        required=False
    )

    text_en = schema.Text(
        title=_(u"Text per l'avís"),
        description=_(u"Permet introduir el text que es veurà a l'avís"),
        required=False
    )


class CintilloSettingsForm(controlpanel.RegistryEditForm):

    schema = ICintilloSettings
    label = _(u'Cintillo Settings')

    def updateFields(self):
        super(CintilloSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(CintilloSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        ram.caches.clear()

        paths = []
        paths.append('/_purge_all')

        purge_varnish_paths(self, paths)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class CintilloSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CintilloSettingsForm
