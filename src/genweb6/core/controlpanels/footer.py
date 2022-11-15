# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


class ICustomLinks(model.Schema):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    link = schema.TextLine(
        title=_(u'Link'),
        required=False,
    )


class IFooterSettings(model.Schema):

    show_image = schema.Bool(
        title=_(u"Mostrar imatge de fons al peu"),
        description=_(u"Al marcar aquesta opció es mostrarà la imatge principal configurada en la capçalera com a fons del peu."),
        required=False,
        default=False,
    )

    read_permission(signatura_ca='genweb.webmaster')
    write_permission(signatura_ca='genweb.manager')
    signatura_ca = schema.TextLine(
        title=_(u"signatura_ca", default=u"Signatura [CA]"),
        description=_(u"help_signatura_ca", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_es='genweb.webmaster')
    write_permission(signatura_es='genweb.manager')
    signatura_es = schema.TextLine(
        title=_(u"signatura_es", default=u"Signatura [ES]"),
        description=_(u"help_signatura_es", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_en='genweb.webmaster')
    write_permission(signatura_en='genweb.manager')
    signatura_en = schema.TextLine(
        title=_(u"signatura_en", default=u"Signatura [EN]"),
        description=_(u"help_signatura_en", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    model.fieldset('Links', _(u'Links'),
                   fields=['enable_links',
                           'enable_login', 'enable_register',
                           'title_links_ca', 'title_links_es', 'title_links_en',
                           'table_links_ca', 'table_links_es', 'table_links_en'])

    enable_links = schema.Bool(
        title=_(u"Mostrar enllaços al peu"),
        description=_(u"Al marcar aquesta opció es mostrarà els enllaços als continguts i els enllaços personalitzats"),
        required=False,
        default=False,
    )

    enable_login = schema.Bool(
        title=_(u"Mostrar enllaç al login"),
        description=_(u"Al marcar aquesta opció es mostrarà un enllaç al login en el apartat d'enllaços personalitats."),
        required=False,
        default=False,
    )

    read_permission(enable_register='genweb.manager')
    write_permission(enable_register='genweb.manager')
    enable_register = schema.Bool(
        title=_(u"Mostrar enllaç al registre"),
        description=_(u"Al marcar aquesta opció es mostrarà un enllaç al registre, només funcionarà si esta activat a part el autoregistre en la web"),
        required=False,
        default=False,
    )

    title_links_ca = schema.TextLine(
        title=_(u"Títol del apartat de enllaços personalitzats [CA]"),
        description=_(u"Per defecte: Administració"),
        required=False,
    )

    title_links_es = schema.TextLine(
        title=_(u"Títol del apartat de enllaços personalitzats [ES]"),
        description=_(u"Per defecte: Administración"),
        required=False,
    )

    title_links_en = schema.TextLine(
        title=_(u"Títol del apartat de enllaços personalitzats [EN]"),
        description=_(u"Per defecte: Administration"),
        required=False,
    )

    directives.widget(table_links_ca=DataGridFieldFactory)
    table_links_ca = schema.List(
        title=_(u'Enllaços [CA]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )

    directives.widget(table_links_es=DataGridFieldFactory)
    table_links_es = schema.List(
        title=_(u'Enllaços [ES]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )

    directives.widget(table_links_en=DataGridFieldFactory)
    table_links_en = schema.List(
        title=_(u'Enllaços [EN]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )


class FooterSettingsForm(controlpanel.RegistryEditForm):

    schema = IFooterSettings
    label = _(u'Footer Settings')

    def updateFields(self):
        super(FooterSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(FooterSettingsForm, self).updateWidgets()

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


class FooterSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FooterSettingsForm
