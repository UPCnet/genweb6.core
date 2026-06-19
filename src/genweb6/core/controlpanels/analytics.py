# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.dexterity.interfaces import IDexteritySchema
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


class IGA4RSSAnalyticsSettings(model.Schema, IDexteritySchema):
    """Registry settings for server-side GA4 RSS tracking."""

    enabled = schema.Bool(
        title=_(u'Activar seguiment RSS a GA4'),
        description=_(u'Envia un esdeveniment rss_view a GA4 en cada accés a /RSS o /rss.xml'),
        required=False,
        default=False,
    )

    measurement_id = schema.TextLine(
        title=_(u'GA4 Measurement ID'),
        description=_(u'Identificador del flux de dades (p. ex. G-XXXXXXXX). Si es deixa buit, es prova d\'extreure del camp webstats_js del lloc.'),
        required=False,
        default='',
    )

    api_secret = schema.TextLine(
        title=_(u'GA4 Measurement Protocol API secret'),
        description=_(u'Secret creat a GA4 Admin > Fluxos de dades > Measurement Protocol.'),
        required=False,
    )


class AnalyticsSettingsForm(controlpanel.RegistryEditForm):

    schema = IGA4RSSAnalyticsSettings
    label = _(u'Analytics RSS (GA4)')

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_('Changes saved'), 'info')
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_('Changes canceled.'), 'info')
        self.request.response.redirect(
            self.context.absolute_url() + '/' + self.control_panel_view
        )


class AnalyticsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AnalyticsSettingsForm
