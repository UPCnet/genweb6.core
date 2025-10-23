# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView

from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexteritySchema
from plone.supermodel import model
from z3c.form.browser.text import TextWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _

import secrets


class IAccordionTabsJSWidget(ITextWidget):
    pass


@implementer_only(IAccordionTabsJSWidget)
class AccordionTabsJSWidget(TextWidget):

    klass = u'accordion-tabs-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def AccordionTabsJSFieldWidget(field, request):
    return FieldWidget(field, AccordionTabsJSWidget(request))


typeTemplateVocabulary = SimpleVocabulary([
    SimpleTerm(value="--NOVALUE--", title=_(u'Selecciona una opció')),
    SimpleTerm(value="accordion", title=_(u'Acordió')),
    SimpleTerm(value="nav", title=_(u'Pestanyes'))])


contentVocabulary = SimpleVocabulary([
    SimpleTerm(value="--NOVALUE--", title=_(u'Selecciona una opció')),
    SimpleTerm(value="inside", title=_(u'Continguts de dintre d\'aquest directori')),
    SimpleTerm(value="collection", title=_(u'Col·lecció'))])


class IAccordionTabs(model.Schema, IDexteritySchema):

    type_template = schema.Choice(
        title=_(u'Tipus de plantilla'),
        required=True,
        vocabulary=typeTemplateVocabulary,
    )

    # Si se vuelve a mostrar esta opción poner el required en True
    directives.mode(content='hidden')
    content = schema.Choice(
        title=_(u'Continguts que alimenten la plantilla'),
        description=_(u'Podeu afegir continguts en aquest directori des del següent <a target="_blank" href="folder_contents">enllaç</a>'),
        required=False,
        vocabulary=contentVocabulary,
    )

    directives.widget(
        'collection',
        RelatedItemsFieldWidget,
        pattern_options={"selectableTypes": ["Collection"]},
    )

    directives.mode(collection='hidden')
    collection = RelationChoice(
        title=_(u"Cerca una col·lecció"),
        required=False,
        vocabulary="plone.app.vocabularies.Catalog",
    )

    accordion_open_multiple = schema.Bool(
        title=_(u'Habilitar l\'opció de poder obrir múltiples panells de l’acordió'),
        required=False,
    )

    accordion_open_first = schema.Bool(
        title=_(u'Obrir el primer panell de l’acordió per defecte'),
        required=False,
    )

    show_copy = schema.Bool(
        title=_(u'Mostrar un botó (Copiar HTML) que permeti copiar el codi html generat per a poder inserir-ho en una altre lloc.'),
        default=True,
        required=False,
    )

    directives.widget('js', AccordionTabsJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)


@implementer(IAccordionTabs)
class AccordionTabs(Container):

    @property
    def b_icon_expr(self):
        return "segmented-nav"

    def token(self):
        return 't' + secrets.token_hex(16)

    def elem_to_dict(self, index, first, elem):
        return {
            'index': index,
            'first': first,
            'id': elem.id.replace('.', '-'),
            'title': elem.title,
            'description': elem.description,
            'text': elem.text.output if elem.text else elem.description,
            'url': elem.absolute_url(),
            'image': elem.absolute_url() + '/@@images/image/preview' if getattr(elem, 'image', False) else ''}

    def contents(self):
        contents = []
        first = True
        index = 0

        sm = getSecurityManager()
        if self.content == 'collection':
            collection = self.collection.to_object
            for elem in collection.results():
                obj = elem.getObject()
                if sm.checkPermission('View', obj):
                    contents.append(self.elem_to_dict(index, first, obj))

                    index += 1
                    if first:
                        first = False
        else:
            for elem in self:
                elem = self[elem]
                if sm.checkPermission('View', elem):
                    contents.append(self.elem_to_dict(index, first, elem))

                    index += 1
                    if first:
                        first = False

        return contents


class View(BrowserView):
    pass
