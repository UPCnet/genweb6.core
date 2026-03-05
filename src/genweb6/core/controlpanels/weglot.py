# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.dexterity.interfaces import IDexteritySchema
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.ramcache import ram

from genweb6.core import _


class IWeglotSettings(model.Schema, IDexteritySchema):
    """Settings for Weglot translation widget."""

    weglot_enabled = schema.Bool(
        title=_(u'Activar Weglot'),
        description=_(u'Inclou el script de Weglot per a la traducció del lloc.'),
        required=False,
        default=False,
    )

    weglot_api_key = schema.TextLine(
        title=_(u'API Key de Weglot'),
        description=_(u'Clau API necessària per connectar amb Weglot (ex: wg_xxxxxxxxxxxxxxxxxx).'),
        required=False,
    )


class WeglotSettingsForm(controlpanel.RegistryEditForm):

    schema = IWeglotSettings
    label = _(u'Weglot')

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        ram.caches.clear()

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(
            self.context.absolute_url() + '/' + self.control_panel_view
        )


class WeglotSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = WeglotSettingsForm
