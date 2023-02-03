# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.component import queryUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget


themeVocabulary = SimpleVocabulary([
    SimpleTerm(value="light-theme", title=_(u'Clar')),
    # SimpleTerm(value="dark-theme", title=_(u'Fosc')),
    SimpleTerm(value="light-to-dark-theme", title=_(u'Clar a fosc'))])

mainHeroStyleVocabulary = SimpleVocabulary([
    SimpleTerm(value="text-hero", title=_(u'Només text')),
    SimpleTerm(value="image-hero", title=_(u'Conservadora')),
    SimpleTerm(value="pretty-image-hero", title=_(u'Innovadora')),
    SimpleTerm(value="full-pretty-image-hero", title=_(u'Innovadora a pantalla sencera'))])

contentHeroStyleVocabulary = SimpleVocabulary([
    SimpleTerm(value="text-hero", title=_(u'Només text')),
    SimpleTerm(value="image-hero", title=_(u'Conservadora'))])


class IHeaderSettings(model.Schema):

    model.fieldset('Configuracions', _(u'Configuracions'),
                   fields=['theme', 'main_hero_style', 'content_hero_style',
                           'html_title_ca', 'html_title_es', 'html_title_en',
                           'html_description_ca', 'html_description_es', 'html_description_en',
                           'hero_image', 'full_hero_image', 'hero_image_alt'])

    read_permission(theme='genweb.webmaster')
    write_permission(theme='genweb.manager')
    theme = schema.Choice(
        title=_(u'Tema'),
        required=True,
        vocabulary=themeVocabulary,
        default='light-to-dark-theme'
    )

    read_permission(main_hero_style='genweb.webmaster')
    write_permission(main_hero_style='genweb.manager')
    main_hero_style = schema.Choice(
        title=_(u'Tipus de hero de la pàgina principal'),
        required=True,
        vocabulary=mainHeroStyleVocabulary,
        default='image-hero'
    )

    read_permission(content_hero_style='genweb.webmaster')
    write_permission(content_hero_style='genweb.manager')
    content_hero_style = schema.Choice(
        title=_(u'Tipus de hero dintre dels continguts'),
        required=True,
        vocabulary=contentHeroStyleVocabulary,
        default='image-hero'
    )

    html_title_ca = schema.TextLine(
        title=_(u"html_title_ca",
                default=u"Títol del web amb HTML tags (negretes) [CA]"),
        description=_(u"help_html_title_ca",
                      default=u"Afegiu el títol del Genweb. Podeu incloure tags HTML"),
        required=False,
    )

    html_title_es = schema.TextLine(
        title=_(u"html_title_es",
                default=u"Títol del web amb HTML tags (negretes) [ES]"),
        description=_(u"help_html_title_es",
                      default=u"Afegiu el títol del Genweb. Podeu incloure tags HTML"),
        required=False,
    )

    html_title_en = schema.TextLine(
        title=_(u"html_title_en",
                default=u"Títol del web amb HTML tags (negretes) [EN]"),
        description=_(u"help_html_title_en",
                      default=u"Afegiu el títol del Genweb. Podeu incloure tags HTML."),
        required=False,
    )

    html_description_ca = schema.TextLine(
        title=_(u"Descripció del web amb HTML tags (negretes) [CA]"),
        description=_(u"Afegiu la descripció del Genweb. Podeu incloure tags HTML. Només es veurà visible amb el nou estil activat."),
        required=False,
    )

    html_description_es = schema.TextLine(
        title=_(u"Descripció del web amb HTML tags (negretes) [ES]"),
        description=_(u"Afegiu la descripció del Genweb. Podeu incloure tags HTML. Només es veurà visible amb el nou estil activat."),
        required=False,
    )

    html_description_en = schema.TextLine(
        title=_(u"Descripció del web amb HTML tags (negretes) [EN]"),
        description=_(u"Afegiu la descripció del Genweb. Podeu incloure tags HTML. Només es veurà visible amb el nou estil activat."),
        required=False,
    )

    directives.widget('hero_image', NamedImageFieldWidget)
    hero_image = schema.Bytes(
        title=_(u"Imatge principal conservadora"),
        description=_(u"És important pujar una imatge amb una resolució de 2000 x 180px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina si no hi ha una imatge principal innovadora."),
        required=False,
    )

    directives.widget('full_hero_image', NamedImageFieldWidget)
    full_hero_image = schema.Bytes(
        title=_(u"Imatge principal innovadora"),
        description=_(u"És important pujar una imatge amb una resolució de 2000 x 900px per el model de pantalla sencera o de 2000 x 650px. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina."),
        required=False,
    )

    hero_image_alt = schema.TextLine(
        title=_(u"hero_image_alt",
                default=u"Text alternatiu del hero image"),
        description=_(u"help_hero_image_alt",
                      default=u"Afegiu el text alternatiu (alt) del hero image."),
        required=False,
    )

    model.fieldset('Logo', _(u'Logo'),
                   fields=['fieldset_logo', 'fieldset_secundary_logo',
                           'logo', 'secundary_logo',
                           'logo_responsive', 'secundary_logo_responsive',
                           'logo_alt', 'secundary_logo_alt',
                           'logo_url', 'secundary_logo_url',
                           'logo_external_url', 'secundary_logo_external_url'])

    read_permission(fieldset_logo='genweb.manager')
    write_permission(fieldset_logo='genweb.manager')
    directives.widget('fieldset_logo', FieldsetFieldWidget)
    fieldset_logo = schema.Text(
        default=_(u'Logo principal'),
        required=False,
    )

    read_permission(fieldset_secundary_logo='genweb.manager')
    write_permission(fieldset_secundary_logo='genweb.manager')
    directives.widget('fieldset_secundary_logo', FieldsetFieldWidget)
    fieldset_secundary_logo = schema.Text(
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

    read_permission(secundary_logo='genweb.manager')
    write_permission(secundary_logo='genweb.manager')
    directives.widget('secundary_logo', NamedImageFieldWidget)
    secundary_logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Please upload an image"),
        required=False,
    )

    read_permission(logo_responsive='genweb.manager')
    write_permission(logo_responsive='genweb.manager')
    directives.widget('logo_responsive', NamedImageFieldWidget)
    logo_responsive = schema.Bytes(
        title=_(u"Logo petit"),
        description=_(u"Please upload an image"),
        required=False,
    )

    read_permission(secundary_logo_responsive='genweb.manager')
    write_permission(secundary_logo_responsive='genweb.manager')
    directives.widget('secundary_logo_responsive', NamedImageFieldWidget)
    secundary_logo_responsive = schema.Bytes(
        title=_(u"Logo petit"),
        description=_(u"Please upload an image"),
        required=False,
    )

    read_permission(logo_alt='genweb.manager')
    write_permission(logo_alt='genweb.manager')
    logo_alt = schema.TextLine(
        title=_(u"logo_alt",
                default=u"Text alternatiu del logo"),
        description=_(u"help_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,
    )

    read_permission(secundary_logo_alt='genweb.manager')
    write_permission(secundary_logo_alt='genweb.manager')
    secundary_logo_alt = schema.TextLine(
        title=_(u"logo_alt",
                default=u"Text alternatiu del logo"),
        description=_(u"help_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,
    )

    read_permission(logo_url='genweb.manager')
    write_permission(logo_url='genweb.manager')
    logo_url = schema.TextLine(
        title=_(u"logo_url",
                default=u"URL del logo"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    read_permission(secundary_logo_url='genweb.manager')
    write_permission(secundary_logo_url='genweb.manager')
    secundary_logo_url = schema.TextLine(
        title=_(u"logo_url",
                default=u"URL del logo"),
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

    secundary_logo_external_url = schema.Bool(
        title=_(u"logo_external_url",
                default=u"Es una URL externa?"),
        required=False,
    )

    model.fieldset('Altres', _(u'Altres'),
                   fields=['treu_menu_horitzontal', 'amaga_identificacio',
                           'idiomes_publicats', 'languages_link_to_root'])

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
        title=_(u"amaga_identificacio", default="Amaga de les eines l'enllaç d'identificació"),
        description=_(u"help_amaga_identificacio", default=u"Amaga de les eines l'enllaç d'identificació ..."),
        required=False,
        default=False,
    )

    read_permission(idiomes_publicats='genweb.manager')
    write_permission(idiomes_publicats='genweb.manager')
    idiomes_publicats = schema.List(
        title=_(u"idiomes_publicats",
                default=u"Idiomes publicats al web"),
        description=_(u"help_idiomes_publicats",
                      default=u"Aquests seran els idiomes publicats a la web, els idiomes no especificats no seran públics però seran visibles pels gestors (editors)."),
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.SupportedContentLanguages'),
        required=False,
        default=['ca']
    )

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

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class HeaderSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = HeaderSettingsForm


class GWHero(Download):

    def __init__(self, context, request):
        super(GWHero, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'hero_image', False):
            filename, data = b64decode_file(header_config.hero_image)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data


class GWFullHero(Download):

    def __init__(self, context, request):
        super(GWFullHero, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'full_hero_image', False):
            filename, data = b64decode_file(header_config.full_hero_image)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data


class GWLogo(Download):

    def __init__(self, context, request):
        super(GWLogo, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'logo', False):
            filename, data = b64decode_file(header_config.logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data


class GWLogoResponsive(Download):

    def __init__(self, context, request):
        super(GWLogoResponsive, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'logo_responsive', False):
            filename, data = b64decode_file(header_config.logo_responsive)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data


class GWSecundaryLogo(Download):

    def __init__(self, context, request):
        super(GWSecundaryLogo, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'secundary_logo', False):
            filename, data = b64decode_file(header_config.secundary_logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data


class GWSecundaryLogoResponsive(Download):

    def __init__(self, context, request):
        super(GWSecundaryLogoResponsive, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'secundary_logo_responsive', False):
            filename, data = b64decode_file(header_config.secundary_logo_responsive)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data
