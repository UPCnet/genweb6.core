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
from zope.ramcache import ram
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.widgets import FieldsetFieldWidget


themeVocabulary = SimpleVocabulary([
    SimpleTerm(value="light-theme", title=_(u'Clar')),
    SimpleTerm(value="dark-theme", title=_(u'Fosc')),
    SimpleTerm(value="image-theme", title=_(u'Imatge capçalera'))])


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

    theme = schema.Choice(
        title=_(u'Tema'),
        required=True,
        vocabulary=themeVocabulary,
        default='dark-theme'
    )

    directives.widget('fieldset_menu', FieldsetFieldWidget)
    fieldset_menu = schema.Text(
        default=_(u'Menú al peu'),
        required=False,
    )

    enable_links = schema.Bool(
        title=_(u"Mostrar enllaços al peu"),
        description=_(u"Al marcar aquesta opció es mostrarà els enllaços als continguts i els enllaços personalitzats"),
        required=False,
        default=True,
    )

    complete_custom_links = schema.Bool(
        title=_(u"Costumizar completament els enllaços"),
        description=_(u"Al marcar aquesta opció es mostrarà la pàgina de enllaços personalitzats al peu, la pàgina ha d'estar publicada."),
        required=False,
        default=False,
    )

    directives.widget('fieldset_links', FieldsetFieldWidget)
    fieldset_links = schema.Text(
        default=_(u'Enllaços al peu'),
        required=False,
    )

    # enable_login = schema.Bool(
    #     title=_(u"Mostrar enllaç al login"),
    #     description=_(u"Al marcar aquesta opció es mostrarà un enllaç al login en el apartat d'enllaços personalitats."),
    #     required=False,
    #     default=False,
    # )

    # read_permission(enable_register='genweb.manager')
    # write_permission(enable_register='genweb.manager')
    # enable_register = schema.Bool(
    #     title=_(u"Mostrar enllaç al registre"),
    #     description=_(u"Al marcar aquesta opció es mostrarà un enllaç al registre, només funcionarà si esta activat a part el autoregistre en la web"),
    #     required=False,
    #     default=False,
    # )

    title_links_ca = schema.TextLine(
        title=_(u"Nom de l’apartat [CA]"),
        description=_(u"Per defecte: Enllaços"),
        required=False,
    )

    title_links_es = schema.TextLine(
        title=_(u"Nom de l’apartat [ES]"),
        description=_(u"Per defecte: Enlaces"),
        required=False,
    )

    title_links_en = schema.TextLine(
        title=_(u"Nom de l’apartat [EN]"),
        description=_(u"Per defecte: Links"),
        required=False,
    )

    directives.widget(table_links_ca=DataGridFieldFactory)
    table_links_ca = schema.List(
        title=_(u'Llista d’enllaços [CA]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )

    directives.widget(table_links_es=DataGridFieldFactory)
    table_links_es = schema.List(
        title=_(u'Llista d’enllaços [ES]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )

    directives.widget(table_links_en=DataGridFieldFactory)
    table_links_en = schema.List(
        title=_(u'Llista d’enllaços [EN]'),
        value_type=DictRow(schema=ICustomLinks),
        required=False,
    )

    read_permission(fieldset_signatura='genweb.manager')
    write_permission(fieldset_signatura='genweb.manager')
    directives.widget('fieldset_signatura', FieldsetFieldWidget)
    fieldset_signatura = schema.Text(
        default=_(u'Signatura'),
        required=False,
    )

    read_permission(signatura_ca='genweb.manager')
    write_permission(signatura_ca='genweb.manager')
    signatura_ca = schema.TextLine(
        title=_(u"signatura_ca", default=u"Signatura [CA]"),
        description=_(u"help_signatura_ca", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_es='genweb.manager')
    write_permission(signatura_es='genweb.manager')
    signatura_es = schema.TextLine(
        title=_(u"signatura_es", default=u"Signatura [ES]"),
        description=_(u"help_signatura_es", default=u"És el literal que apareix al peu de pàgina."),
        required=False,
    )

    read_permission(signatura_en='genweb.manager')
    write_permission(signatura_en='genweb.manager')
    signatura_en = schema.TextLine(
        title=_(u"signatura_en", default=u"Signatura [EN]"),
        description=_(u"help_signatura_en", default=u"És el literal que apareix al peu de pàgina."),
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

        ram.caches.clear()
        self.applyChanges(data)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class FooterSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FooterSettingsForm
