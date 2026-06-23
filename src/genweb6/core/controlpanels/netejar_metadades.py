# -*- coding: utf-8 -*-
from zope.interface import Invalid
from zope import schema
from plone.supermodel import model
from plone.app.registry.browser import controlpanel
from zope.ramcache import ram
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from plone.dexterity.interfaces import IDexteritySchema

from genweb6.core import _
from genweb6.core.purge import purge_varnish_paths
from plone import api
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def get_metadades_current_username():
    user = api.user.get_current()
    if user is None:
        return 'system'
    username = user.getId()
    if username in ('Anonymous User', 'anonymous'):
        return 'system'
    return username


def log_metadades_cleanup(title, success, status='', url=None, username=None):
    username = username or get_metadades_current_username()
    date = datetime.now().isoformat(timespec='seconds')
    if url:
        logger.info(
            "[METADADES] date=%s user=%s title=%s success=%s status=%s url=%s",
            date,
            username,
            title,
            success,
            status,
            url,
        )
    else:
        logger.info(
            "[METADADES] date=%s user=%s title=%s success=%s status=%s",
            date,
            username,
            title,
            success,
            status,
        )


def isURL(value):
    """Check if the input is a valid URL."""
    url_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    if not url_regex.match(value):
        raise Invalid(_(u"El valor introduït no és un URL vàlid."))
    return True


class IMetadadesSettings(model.Schema, IDexteritySchema):
    """Configuració per l'api de metadades i actualització d'indicadors"""

    api_url = schema.URI(
        title=u"URL del servei d'anonimització",
        constraint=isURL,
        required=True
    )

    api_key = schema.TextLine(
        title=u"Clau API",
        required=True,
    )

    indicadors_api_url = schema.URI(
        title=u"URL base del servei d'indicadors",
        constraint=isURL,
        required=True
    )

    indicadors_api_key = schema.TextLine(
        title=u"Clau API del servei d'indicadors",
        required=True,
    )

    indicadors_servei_id = schema.TextLine(
        title=u"ID del servei per Indicadors",
        required=True,
    )

    indicadors_categoria_id = schema.TextLine(
        title=u"ID de l'indicador a actualitzar",
        required=True,
    )


class MetadadesSettingslForm(controlpanel.RegistryEditForm):
    schema = IMetadadesSettings
    label = u"Configuració Neteja de Metadades"
    description = u"Defineix la URL, la clau API i els paràmetres del servei d'indicadors."

    def updateFields(self):
        super(MetadadesSettingslForm, self).updateFields()

    def updateWidgets(self):
        super(MetadadesSettingslForm, self).updateWidgets()
    
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


class MetadadesControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MetadadesSettingslForm