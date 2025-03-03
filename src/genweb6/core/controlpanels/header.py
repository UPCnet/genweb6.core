# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.dexterity.interfaces import IDexteritySchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from plone.memoize import ram
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from time import time
from z3c.form import button
from zope import schema
from zope.component import queryUtility
from zope.interface import Invalid
from zope.ramcache import ram as ramcache
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget
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


themeVocabulary = SimpleVocabulary([
    SimpleTerm(value="light-theme", title=_(u'Clar')),
    # SimpleTerm(value="dark-theme", title=_(u'Fosc')),
    SimpleTerm(value="light-to-dark-theme", title=_(u'Clar a fosc'))])

mainHeroStyleVocabulary = SimpleVocabulary([
    SimpleTerm(value="text-hero", title=_(u'Només text')),
    SimpleTerm(value="image-hero", title=_(u'Conservadora')),
    SimpleTerm(value="pretty-image-hero", title=_(u'Innovadora amb títol en fons blau UPC')),
    SimpleTerm(value="pretty-image-black-hero", title=_(u'Innovadora amb títol negre')),
    SimpleTerm(value="full-pretty-image-hero", title=_(u'Innovadora a pantalla sencera'))])

contentHeroStyleVocabulary = SimpleVocabulary([
    SimpleTerm(value="text-hero", title=_(u'Només text')),
    SimpleTerm(value="image-hero", title=_(u'Conservadora'))])

positionTextVocabulary = SimpleVocabulary([
    SimpleTerm(value="left", title=_(u'Rodona a l’esquerra')),
    SimpleTerm(value="right", title=_(u'Rodona a la dreta')),
    SimpleTerm(value="down", title=_(u'Inferior'))])

class IHeaderSettings(model.Schema, IDexteritySchema):

    model.fieldset('Configuracions', _(u'Configuracions'),
                   fields=['main_hero_style', 'content_hero_style',
                           'fieldset_ca', 'fieldset_es', 'fieldset_en',
                           'html_title_ca', 'html_title_es', 'html_title_en',
                           'html_description_ca', 'html_description_es', 'html_description_en',
                           'full_hero_image', 'full_hero_image_es', 'full_hero_image_en',
                           'full_hero_image_alt_ca', 'full_hero_image_alt_es', 'full_hero_image_alt_en',
                           'full_hero_image_url_ca', 'full_hero_image_url_es', 'full_hero_image_url_en',
                           'full_hero_image_text_ca', 'full_hero_image_text_es', 'full_hero_image_text_en',
                           'full_hero_image_position_text', 'hero_image', 'theme'])

    main_hero_style = schema.Choice(
        title=_(u'Tipus d’imatge a les pàgines principals'),
        required=True,
        vocabulary=mainHeroStyleVocabulary,
        default='image-hero'
    )

    content_hero_style = schema.Choice(
        title=_(u'Tipus d’imatge als continguts'),
        required=True,
        vocabulary=contentHeroStyleVocabulary,
        default='image-hero'
    )

    directives.widget('fieldset_ca', FieldsetFieldWidget)
    fieldset_ca = schema.Text(
        default=_(u'Català'),
        required=False,
    )

    directives.widget('fieldset_es', FieldsetFieldWidget)
    fieldset_es = schema.Text(
        default=_(u'Castellà'),
        required=False,
    )

    directives.widget('fieldset_en', FieldsetFieldWidget)
    fieldset_en = schema.Text(
        default=_(u'Anglès'),
        required=False,
    )

    read_permission(html_title_ca='genweb.webmaster')
    write_permission(html_title_ca='genweb.manager')
    html_title_ca = schema.TextLine(
        title=_(u"html_title_ca", default=u"Títol del web"),
        required=False,
    )

    read_permission(html_title_es='genweb.webmaster')
    write_permission(html_title_es='genweb.manager')
    html_title_es = schema.TextLine(
        title=_(u"html_title_es", default=u"Títol del web"),
        required=False,
    )

    read_permission(html_title_en='genweb.webmaster')
    write_permission(html_title_en='genweb.manager')
    html_title_en = schema.TextLine(
        title=_(u"html_title_en", default=u"Títol del web"),
        required=False,
    )

    html_description_ca = schema.TextLine(
        title=_(u"Frase publicitària"),
        description=_(u"Es visualitza sota el títol del web als tipus de capçalera amb imatge hero"),
        required=False,)

    html_description_es = schema.TextLine(
        title=_(u"Frase publicitària"),
        description=_(u"Es visualitza sota el títol del web als tipus de capçalera amb imatge hero"),
        required=False,)

    html_description_en = schema.TextLine(
        title=_(u"Frase publicitària"),
        description=_(u"Es visualitza sota el títol del web als tipus de capçalera amb imatge hero"),
        required=False,)

    directives.widget('full_hero_image', NamedImageFieldWidget)
    full_hero_image = schema.Bytes(
        title=_(u"Imatge principal innovadora"),
        description=_(
            u"És important pujar una imatge amb una resolució de 2000 x 900px per el model de pantalla sencera o de 2000 x 500px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina."),
        required=False,)

    directives.widget('full_hero_image_es', NamedImageFieldWidget)
    full_hero_image_es = schema.Bytes(
        title=_(u"Imatge principal innovadora"),
        description=_(
            u"És important pujar una imatge amb una resolució de 2000 x 900px per el model de pantalla sencera o de 2000 x 500px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina."),
        required=False,)

    directives.widget('full_hero_image_en', NamedImageFieldWidget)
    full_hero_image_en = schema.Bytes(
        title=_(u"Imatge principal innovadora"),
        description=_(
            u"És important pujar una imatge amb una resolució de 2000 x 900px per el model de pantalla sencera o de 2000 x 500px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina."),
        required=False,)

    full_hero_image_alt_ca = schema.TextLine(
        title=_(u"Text alternatiu de la imatge"),
        description=_(u"Per accesibilitat cal descriure la imatge"),
        required=False,)

    full_hero_image_alt_es = schema.TextLine(
        title=_(u"Text alternatiu de la imatge"),
        description=_(u"Per accesibilitat cal descriure la imatge"),
        required=False,)

    full_hero_image_alt_en = schema.TextLine(
        title=_(u"Text alternatiu de la imatge"),
        description=_(u"Per accesibilitat cal descriure la imatge"),
        required=False,)

    full_hero_image_url_ca = schema.TextLine(
        title=_(u"Enllaç"),
        constraint=isURL,
        required=False,)

    full_hero_image_url_es = schema.TextLine(
        title=_(u"Enllaç"),
        constraint=isURL,
        required=False,)

    full_hero_image_url_en = schema.TextLine(
        title=_(u"Enllaç"),
        constraint=isURL,
        required=False,)

    full_hero_image_text_ca = schema.TextLine(
        title=_(u"Text de la imatge"),
        required=False,)

    full_hero_image_text_es = schema.TextLine(
        title=_(u"Text de la imatge"),
        required=False,)

    full_hero_image_text_en = schema.TextLine(
        title=_(u"Text de la imatge"),
        required=False,)

    full_hero_image_position_text = schema.Choice(
        title=_(u'Posició del text'),
        required=True,
        vocabulary=positionTextVocabulary,
        default='left')

    directives.widget('hero_image', NamedImageFieldWidget)
    hero_image = schema.Bytes(
        title=_(u"Imatge principal conservadora"),
        description=_(u"És important pujar una imatge amb una resolució de 2000 x 100px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina si no hi ha una imatge principal innovadora."),
        required=False,)

    theme = schema.Choice(
        title=_(u'Color de transició del menú quan fem scroll'),
        required=True,
        vocabulary=themeVocabulary,
        default='light-to-dark-theme'
    )

    model.fieldset('Logo', _(u'Logo'),
                   fields=['fieldset_logo', 'fieldset_secondary_logo',
                           'logo', 'secondary_logo',
                           'logo_alt', 'secondary_logo_alt',
                           'logo_alt_es', 'secondary_logo_alt_es',
                           'logo_alt_en', 'secondary_logo_alt_en',
                           'logo_url', 'secondary_logo_url',
                           'logo_url_es', 'secondary_logo_url_es',
                           'logo_url_en', 'secondary_logo_url_en',
                           'logo_external_url', 'secondary_logo_external_url'])

    read_permission(fieldset_logo='genweb.manager')
    write_permission(fieldset_logo='genweb.manager')
    directives.widget('fieldset_logo', FieldsetFieldWidget)
    fieldset_logo = schema.Text(
        default=_(u'Logo principal'),
        required=False,
    )

    read_permission(fieldset_secondary_logo='genweb.manager')
    write_permission(fieldset_secondary_logo='genweb.manager')
    directives.widget('fieldset_secondary_logo', FieldsetFieldWidget)
    fieldset_secondary_logo = schema.Text(
        default=_(u'Logo secundari'),
        required=False,
    )

    read_permission(logo='genweb.manager')
    write_permission(logo='genweb.manager')
    directives.widget('logo', NamedImageFieldWidget)
    logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Please upload an image"),
        required=False,
    )

    read_permission(secondary_logo='genweb.manager')
    write_permission(secondary_logo='genweb.manager')
    directives.widget('secondary_logo', NamedImageFieldWidget)
    secondary_logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Please upload an image"),
        required=False,
    )

    read_permission(logo_alt='genweb.manager')
    write_permission(logo_alt='genweb.manager')
    logo_alt = schema.TextLine(
        title=_(u"logo_alt", default=u"Text alternatiu del logo [CA]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,)


    read_permission(logo_alt_es='genweb.manager')
    write_permission(logo_alt_es='genweb.manager')
    logo_alt_es = schema.TextLine(
        title=_(u"logo_alt_es", default=u"Text alternatiu del logo [ES]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,)


    read_permission(logo_alt_en='genweb.manager')
    write_permission(logo_alt_en='genweb.manager')
    logo_alt_en = schema.TextLine(
        title=_(u"logo_alt_en", default=u"Text alternatiu del logo [EN]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera. "),
        required=False,)

    read_permission(secondary_logo_alt='genweb.manager')
    write_permission(secondary_logo_alt='genweb.manager')
    secondary_logo_alt = schema.TextLine(
        title=_(u"secondary_logo_alt", default=u"Text alternatiu del logo secundari [CA]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,)

    read_permission(secondary_logo_alt_es='genweb.manager')
    write_permission(secondary_logo_alt_es='genweb.manager')
    secondary_logo_alt_es = schema.TextLine(
        title=_(u"secondary_logo_alt_es", default=u"Text alternatiu del logo secundari [ES]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,)

    read_permission(secondary_logo_alt_en='genweb.manager')
    write_permission(secondary_logo_alt_en='genweb.manager')
    secondary_logo_alt_en = schema.TextLine(
        title=_(u"secondary_logo_alt_en", default=u"Text alternatiu del logo secundari [EN]"),
        description=_(
            u"help_logo_alt",
            default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,)

    read_permission(logo_url='genweb.manager')
    write_permission(logo_url='genweb.manager')
    logo_url = schema.TextLine(
        title=_(u"logo_url",
                default=u"URL del logo [CA]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(logo_url_es='genweb.manager')
    write_permission(logo_url_es='genweb.manager')
    logo_url_es = schema.TextLine(
        title=_(u"logo_url_es",
                default=u"URL del logo [ES]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(logo_url_en='genweb.manager')
    write_permission(logo_url_en='genweb.manager')
    logo_url_en = schema.TextLine(
        title=_(u"logo_url_en",
                default=u"URL del logo [EN]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )
    read_permission(secondary_logo_url='genweb.manager')
    write_permission(secondary_logo_url='genweb.manager')
    secondary_logo_url = schema.TextLine(
        title=_(u"secondary_logo_url",
                default=u"URL del logo secundari [CA]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(secondary_logo_url_es='genweb.manager')
    write_permission(secondary_logo_url_es='genweb.manager')
    secondary_logo_url_es = schema.TextLine(
        title=_(u"secondary_logo_url_es",
                default=u"URL del logo secundari [ES]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(secondary_logo_url_en='genweb.manager')
    write_permission(secondary_logo_url_en='genweb.manager')
    secondary_logo_url_en = schema.TextLine(
        title=_(u"secondary_logo_url_en",
                default=u"URL del logo secundari [EN]"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(logo_external_url='genweb.manager')
    write_permission(logo_external_url='genweb.manager')
    logo_external_url = schema.Bool(
        title=_(u"logo_external_url",
                default=u"Es una URL externa?"),
        required=False,
    )

    read_permission(secondary_logo_external_url='genweb.manager')
    write_permission(secondary_logo_external_url='genweb.manager')
    secondary_logo_external_url = schema.Bool(
        title=_(u"logo_external_url",
                default=u"Es una URL externa?"),
        required=False,
    )

    model.fieldset('Altres', _(u'Altres'),
                   fields=['treu_menu_horitzontal', 'amaga_identificacio',
                           'idiomes_publicats', 'languages_link_to_root',
                           'treu_icones_xarxes_socials'])

    read_permission(treu_menu_horitzontal='genweb.manager')
    write_permission(treu_menu_horitzontal='genweb.manager')
    treu_menu_horitzontal = schema.Bool(
        title=_(u"treu_menu_horitzontal",
                default="Treu el menú horitzontal"),
        description=_(u"help_treu_menu_horitzontal",
                      default=u"Treu el menú horitzontal ..."),
        required=False,
        default=False,
    )

    read_permission(amaga_identificacio='genweb.manager')
    write_permission(amaga_identificacio='genweb.manager')
    amaga_identificacio = schema.Bool(
        title=_(
            u"amaga_identificacio",
            default="Amaga de les eines l'enllaç d'identificació"),
        description=_(
            u"help_amaga_identificacio",
            default=u"Amaga de les eines l'enllaç d'identificació ..."),
        required=False, default=False,)

    read_permission(idiomes_publicats='genweb.manager')
    write_permission(idiomes_publicats='genweb.manager')
    idiomes_publicats = schema.List(
        title=_(u"idiomes_publicats", default=u"Idiomes publicats al web"),
        description=_(
            u"help_idiomes_publicats",
            default=u"Aquests seran els idiomes publicats a la web, els idiomes no especificats no seran públics però seran visibles pels gestors (editors)."),
        value_type=schema.Choice(
            vocabulary='plone.app.vocabularies.SupportedContentLanguages'),
        required=False, default=['ca'])

    read_permission(languages_link_to_root='genweb.manager')
    write_permission(languages_link_to_root='genweb.manager')
    languages_link_to_root = schema.Bool(
        title=_(u"languages_link_to_root",
                default=u"languages_link_to_root"),
        description=_(u"help_languages_link_to_root",
                      default=u"help_languages_link_to_root"),
        required=False,
        default=False,
    )

    read_permission(treu_icones_xarxes_socials='genweb.manager')
    write_permission(treu_icones_xarxes_socials='genweb.manager')
    treu_icones_xarxes_socials = schema.Bool(
        title=_(u"treu_icones_xarxes_socials"),
        description=_(u"help_treu_icones_xarxes_socials"),
        required=False,
        default=False,
    )


class HeaderSettingsForm(controlpanel.RegistryEditForm):

    schema = IHeaderSettings
    label = _(u'Header Settings')

    def updateFields(self):
        super(HeaderSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(HeaderSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        ramcache.caches.clear()

        paths = []
        paths.append('/@@gw-hero')
        paths.append('/@@gw-full-hero-ca')
        paths.append('/@@gw-full-hero-es')
        paths.append('/@@gw-full-hero-en')
        paths.append('/@@gw-logo')
        paths.append('/@@gw-secondary-logo')
        paths.append('/_purge_all')

        purge_varnish_paths(self, paths)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(
            self.context.absolute_url() + '/' + self.control_panel_view)


class HeaderSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = HeaderSettingsForm


class GWHero(Download):

    def __init__(self, context, request):
        super(GWHero, self).__init__(context, request)
        self.data = None
        self.filename = None

        filename, data = self.generate_hero_image()

        self.data = data
        self.filename = filename

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_hero_image(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'hero_image', False):
            filename, data = b64decode_file(header_config.hero_image)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data


class GWFullHeroCA(Download):

    def __init__(self, context, request):
        super(GWFullHeroCA, self).__init__(context, request)
        self.filename = None
        self.data = None

        filename, data = self.generate_full_hero_image()

        self.filename = filename
        self.data = data

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_full_hero_image(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'full_hero_image', False):
            filename, data = b64decode_file(header_config.full_hero_image)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data


class GWFullHeroES(Download):

    def __init__(self, context, request):
        super(GWFullHeroES, self).__init__(context, request)
        self.filename = None
        self.data = None

        filename, data = self.generate_full_hero_image()

        self.filename = filename
        self.data = data

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_full_hero_image(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'full_hero_image_es', False):
            filename, data = b64decode_file(header_config.full_hero_image_es)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data


class GWFullHeroEN(Download):

    def __init__(self, context, request):
        super(GWFullHeroEN, self).__init__(context, request)
        self.filename = None
        self.data = None

        filename, data = self.generate_full_hero_image()

        self.filename = filename
        self.data = data

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_full_hero_image(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'full_hero_image_en', False):
            filename, data = b64decode_file(header_config.full_hero_image_en)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data

class GWLogo(Download):

    def __init__(self, context, request):
        super(GWLogo, self).__init__(context, request)
        self.filename = None
        self.data = None

        filename, data = self.generate_logo()

        self.filename = filename
        self.data = data

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_logo(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'logo', False):
            filename, data = b64decode_file(header_config.logo)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data


class GWSecundaryLogo(Download):

    def __init__(self, context, request):
        super(GWSecundaryLogo, self).__init__(context, request)
        self.filename = None
        self.data = None

        filename, data = self.generate_secondary_logo()

        self.filename = filename
        self.data = data

    #@ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate_secondary_logo(self):
        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'secondary_logo', False):
            filename, data = b64decode_file(header_config.secondary_logo)
            data = NamedImage(data=data, filename=filename)

        return filename, data

    def _getFile(self):
        return self.data
