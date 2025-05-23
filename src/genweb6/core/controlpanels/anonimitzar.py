from zope.interface import Interface
from zope import schema
from plone.supermodel import model
from plone.autoform import directives as form
from plone.app.registry.browser import controlpanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.ramcache import ram
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from plone.dexterity.interfaces import IDexteritySchema
from zope.interface import Invalid

from genweb6.core import _
from genweb6.core.purge import purge_varnish_paths

import re

def isURL(value):
    """Check if the input is a valid URL."""
    url_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    if not url_regex.match(value):
        raise Invalid(_(u"El valor introduït no és un URL vàlid."))
    return True

class IAnonimitzarSettings(model.Schema, IDexteritySchema):
    """Configuració per l'eina d'anonimització"""

    api_url = schema.URI(
        title=u"URL del servei d'anonimització",
        constraint=isURL,
        required=True
    )

    api_key = schema.TextLine(
        title=u"Clau API",
        required=True,
    )


class AnonimitzarSettingslForm(controlpanel.RegistryEditForm):
    schema = IAnonimitzarSettings
    label = u"Configuració Anonimitzar PDF"
    description = u"Defineix la URL i la clau API per l'eina d'anonimització."

    def updateFields(self):
        super(AnonimitzarSettingslForm, self).updateFields()

    def updateWidgets(self):
        super(AnonimitzarSettingslForm, self).updateWidgets()
    
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

class AnonimitzarControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AnonimitzarSettingslForm