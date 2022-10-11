# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
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

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget


class IHeaderSettings(model.Schema):

    new_style = schema.Bool(
        title=_(u"Activar el nou estil"),
        required=False,
        default=False,
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
        title=_(u"Imatge principal"),
        description=_(u"És important pujar una imatge amb una resolució de ???, en el cas d'utilitzar el nou estil de Genweb la resolució haurà de ser de ???. Aquesta imatge, a part, es farà servir per al fons del peu de pàgina."),
        required=False,
    )

    write_permission(logo_alt='genweb.webmaster')
    hero_image_alt = schema.TextLine(
        title=_(u"hero_image_alt",
                default=u"Text alternatiu del hero image"),
        description=_(u"help_hero_image_alt",
                      default=u"Afegiu el text alternatiu (alt) del hero image."),
        required=False,
    )

    meta_author = schema.TextLine(
        title=_(u'Meta author tag content'),
        description=_(u'Contingut de la etiqueta meta \"author\"'),
        required=False,
        default=u'UPC. Universitat Politècnica de Catalunya'
    )

    model.fieldset('Logo', _(u'Logo'),
                   fields=['fieldset_logo', 'fieldset_secundary_logo',
                           'logo', 'secundary_logo',
                           'logo_responsive', 'secundary_logo_responsive',
                           'logo_alt', 'secundary_logo_alt',
                           'logo_url', 'secundary_logo_url',
                           'logo_external_url', 'secundary_logo_external_url'])

    directives.widget('fieldset_logo', FieldsetFieldWidget)
    fieldset_logo = schema.Text(
        default=_(u'Logo principal'),
        required=False,
    )

    directives.widget('fieldset_secundary_logo', FieldsetFieldWidget)
    fieldset_secundary_logo = schema.Text(
        default=_(u'Logo secundari'),
        required=False,
    )

    write_permission(logo='genweb.webmaster')
    directives.widget('logo', NamedImageFieldWidget)
    logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Please upload an image"),
        required=False,
    )

    directives.widget('secundary_logo', NamedImageFieldWidget)
    secundary_logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Please upload an image"),
        required=False,
    )

    write_permission(logo_responsive='genweb.webmaster')
    directives.widget('logo_responsive', NamedImageFieldWidget)
    logo_responsive = schema.Bytes(
        title=_(u"Logo petit"),
        description=_(u"Please upload an image"),
        required=False,
    )

    directives.widget('secundary_logo_responsive', NamedImageFieldWidget)
    secundary_logo_responsive = schema.Bytes(
        title=_(u"Logo petit"),
        description=_(u"Please upload an image"),
        required=False,
    )

    write_permission(logo_alt='genweb.webmaster')
    logo_alt = schema.TextLine(
        title=_(u"logo_alt",
                default=u"Text alternatiu del logo"),
        description=_(u"help_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,
    )

    secundary_logo_alt = schema.TextLine(
        title=_(u"logo_alt",
                default=u"Text alternatiu del logo"),
        description=_(u"help_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo de la capçalera."),
        required=False,
    )

    write_permission(logo_url='genweb.webmaster')
    logo_url = schema.TextLine(
        title=_(u"logo_url",
                default=u"URL del logo"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    secundary_logo_url = schema.TextLine(
        title=_(u"logo_url",
                default=u"URL del logo"),
        description=_(u"help_logo_url",
                      default=u"Afegiu l'URL del logo."),
        required=False,
    )

    write_permission(logo_external_url='genweb.webmaster')
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

    model.fieldset('Logo dret', _(u'Logo dret'),
                   fields=['right_logo_enabled', 'right_logo', 'right_logo_alt'])

    right_logo_enabled = schema.Bool(
        title=_(u"right_logo_enabled",
                default=u"Mostrar logo dret"),
        description=_(u"help_right_logo_enabled",
                      default=u"Mostra o no el logo dret de la capçalera."),
        required=False,
        default=False,
    )

    directives.widget('right_logo', NamedImageFieldWidget)
    right_logo = schema.Bytes(
        title=_(u"Logo dret"),
        description=_(u"Please upload an image"),
        required=False,
    )

    right_logo_alt = schema.TextLine(
        title=_(u"right_logo_alt",
                default=u"Text alternatiu del logo dret"),
        description=_(u"help_right_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo dret de la capçalera."),
        required=False,
    )

    model.fieldset('Altres', _(u'Altres'),
                   fields=['treu_menu_horitzontal', 'amaga_identificacio',
                           'idiomes_publicats', 'languages_link_to_root'])

    treu_menu_horitzontal = schema.Bool(
        title=_(u"treu_menu_horitzontal",
                default="Treu el menú horitzontal"),
        description=_(u"help_treu_menu_horitzontal",
                      default=u"Treu el menú horitzontal ..."),
        required=False,
        default=False,
    )

    amaga_identificacio = schema.Bool(
        title=_(u"amaga_identificacio", default="Amaga de les eines l'enllaç d'identificació"),
        description=_(u"help_amaga_identificacio", default=u"Amaga de les eines l'enllaç d'identificació ..."),
        required=False,
        default=False,
    )

    idiomes_publicats = schema.List(
        title=_(u"idiomes_publicats",
                default=u"Idiomes publicats al web"),
        description=_(u"help_idiomes_publicats",
                      default=u"Aquests seran els idiomes publicats a la web, els idiomes no especificats no seran públics però seran visibles pels gestors (editors)."),
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.SupportedContentLanguages'),
        required=False,
        default=['ca']
    )

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


class GWRightLogo(Download):

    def __init__(self, context, request):
        super(GWRightLogo, self).__init__(context, request)
        self.filename = None
        self.data = None

        registry = queryUtility(IRegistry)
        header_config = registry.forInterface(IHeaderSettings)

        if getattr(header_config, 'right_logo', False):
            filename, data = b64decode_file(header_config.right_logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def _getFile(self):
        return self.data
