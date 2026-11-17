# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin
from plone.app.content.browser.vocabulary import PERMISSIONS
from plone.app.registry.browser import controlpanel
from plone.app.vocabularies.principals import PrincipalsVocabulary
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.dexterity.interfaces import IDexteritySchema
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
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
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implementer_only
from zope.component.hooks import getSite
from zope.ramcache import ram as ramcache
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IField
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.purge import purge_varnish_paths

import logging

logger = logging.getLogger(__name__)


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


COLOQIA_GROUPS_VOCABULARY = 'genweb6.core.ColoqiaGroups'
COLOQIA_GROUPS_MIN_CHARS = 3
COLOQIA_GROUPS_MAX_RESULTS = 10

# Mateix permís que el panell de control (genweb.manager) per consultar el
# vocabulari via @@getVocabulary (si no, a l'arrel del lloc es denega).
PERMISSIONS[COLOQIA_GROUPS_VOCABULARY] = 'Genweb: Manager Users'


@implementer(IVocabularyFactory)
class ColoqiaGroupsVocabularyFactory(object):
    """Grups reals (LDAP i locals) per al camp coloqia_groups.

    plone.app.vocabularies.Groups cerca per 'title', atribut que els grups de
    LDAP no tenen. Aquí:
    - Als plugins LDAP es cerca directament pel seu atribut d'id (cn=*text*).
      No es fa servir id=text perquè, si el text és l'id exacte d'un grup en
      cache, el plugin retorna només aquest grup (UPCnet.Plone amagaria
      UPCnet.Plone.Admins).
    - A la resta de plugins (grups locals de Plone) per id i per títol.
    - No es limita la cerca: s'ordena (exacte, comença per, conté) i després
      es talla a COLOQIA_GROUPS_MAX_RESULTS. Si es limités la cerca, el tall
      el faria l'LDAP en el seu ordre i es podrien perdre els més rellevants.
    Sense text o amb menys de COLOQIA_GROUPS_MIN_CHARS no es cerca res
    (evitem cn=* -> SIZELIMIT).

    Els valors ja desats es resolen igualment amb getGroupById (via
    PrincipalsVocabulary), i això fa que la validació del Choice només
    accepti grups existents.
    """

    def search(self, acl_users, query):
        found = {}
        plugins = acl_users.plugins.listPlugins(IGroupEnumerationPlugin)
        for plugin_id, plugin in plugins:
            groupid_attr = getattr(aq_base(plugin), 'groupid_attr', None)
            searches = ([{groupid_attr: query}] if groupid_attr
                        else [{'id': query}, {'title': query}])
            for criteria in searches:
                try:
                    results = plugin.enumerateGroups(**criteria) or ()
                except Exception:
                    logger.exception(
                        'Coloq.ia: error cercant grups a %s', plugin_id)
                    continue
                for info in results:
                    if info.get('id'):
                        found.setdefault(info['id'], info)
        return found

    def __call__(self, context, query=''):
        query = str(query or '').strip()
        terms = []
        if len(query) >= COLOQIA_GROUPS_MIN_CHARS:
            acl_users = getToolByName(getSite(), 'acl_users')
            found = self.search(acl_users, query)
            q = query.lower()

            def rank(group_id):
                gid = group_id.lower()
                return (gid != q, not gid.startswith(q), gid)

            for group_id in sorted(found, key=rank)[:COLOQIA_GROUPS_MAX_RESULTS]:
                title = found[group_id].get('title') or group_id
                if title != group_id:
                    title = '{} ({})'.format(title, group_id)
                terms.append(SimpleTerm(group_id, group_id, title))
        vocabulary = PrincipalsVocabulary(terms)
        vocabulary.principal_source = 'group'
        return vocabulary


ColoqiaGroupsVocabulary = ColoqiaGroupsVocabularyFactory()


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

    directives.widget(
        'coloqia_groups',
        AjaxSelectFieldWidget,
        vocabulary=COLOQIA_GROUPS_VOCABULARY,
        pattern_options={'minimumInputLength': COLOQIA_GROUPS_MIN_CHARS},
    )
    coloqia_groups = schema.List(
        title=_(u'Grups amb accés'),
        description=_(u"Si s'indica algun grup, Coloq.ia només es mostrarà als usuaris que pertanyin a algun d'aquests grups. Si es deixa buit, es mostrarà a tothom."),
        value_type=schema.Choice(vocabulary=COLOQIA_GROUPS_VOCABULARY),
        required=False,
        default=[],
        missing_value=[],
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


class ColoqiaRegistryUpdate(BrowserView):
    """Registra al registry els camps de IColoqiaSettings que falten (p. ex.
    coloqia_groups) i actualitza la definició dels existents, sense
    reinstal·lar el paquet. Conserva els valors existents que siguin vàlids.
    Es pot executar més d'un cop: @@coloqia-update-registry
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.response.setHeader('Content-Type', 'text/plain')

        registry = getUtility(IRegistry)
        prefix = IColoqiaSettings.__identifier__ + '.'
        missing = [name for name in IColoqiaSettings.names()
                   if prefix + name not in registry.records]
        # Sempre es re-registra: crea els camps que falten i actualitza la
        # definició dels existents (p. ex. coloqia_groups TextLine -> Choice)
        # conservant els valors que continuïn sent vàlids.
        registry.registerInterface(IColoqiaSettings)
        if missing:
            return 'Registry: registered ' + ', '.join(missing)
        return 'Registry: fields updated, nothing missing'
