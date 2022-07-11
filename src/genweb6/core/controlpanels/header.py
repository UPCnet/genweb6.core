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

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget


class IHeaderSettings(model.Schema):

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

    read_permission(logo='genweb.superadmin')
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

    read_permission(logo_responsive='genweb.superadmin')
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

    read_permission(logo_alt='genweb.superadmin')
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

    read_permission(logo_url='genweb.superadmin')
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

    read_permission(logo_external_url='genweb.superadmin')
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
                   fields=['treu_menu_horitzontal', 'amaga_identificacio'])

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
