# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
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


class IInteractiveTemplateContentJSWidget(ITextWidget):
    pass


@implementer_only(IInteractiveTemplateContentJSWidget)
class InteractiveTemplateContentJSWidget(TextWidget):

    klass = u'interactive_template_content-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def InteractiveTemplateContentJSFieldWidget(field, request):
    return FieldWidget(field, InteractiveTemplateContentJSWidget(request))


typeTemplateVocabulary = SimpleVocabulary([
    SimpleTerm(value="--NOVALUE--", title=_(u'Selecciona una opció')),
    SimpleTerm(value="accordion", title=_(u'Acordió')),
    SimpleTerm(value="nav", title=_(u'Pestanyes')),
    SimpleTerm(value="carousel", title=_(u'Carousel')),
    SimpleTerm(value="imatge-slide", title=_(u'Slider d\'imatges')),
    SimpleTerm(value="modal", title=_(u'Modal'))])


contentVocabulary = SimpleVocabulary([
    SimpleTerm(value="--NOVALUE--", title=_(u'Selecciona una opció')),
    SimpleTerm(value="inside", title=_(u'Continguts de dintre d\'aquest directori')),
    SimpleTerm(value="collection", title=_(u'Col·lecció'))])


carouselTypeVocabulary = SimpleVocabulary([
    SimpleTerm(value="simple", title=_(u'Simple')),
    SimpleTerm(value="complex", title=_(u'Complex'))])


modalTypeBtnVocabulary = SimpleVocabulary([
    SimpleTerm(value="primary", title='Primary'),
    SimpleTerm(value="secondary", title='Secondary'),
    SimpleTerm(value="success", title='Success'),
    SimpleTerm(value="danger", title='Danger'),
    SimpleTerm(value="warning", title='Warning'),
    SimpleTerm(value="info", title='Info'),
    SimpleTerm(value="light", title='Light'),
    SimpleTerm(value="dark", title='Dark'),
    SimpleTerm(value="outline-primary", title='Outline Primary'),
    SimpleTerm(value="outline-secondary", title='Outline Secondary'),
    SimpleTerm(value="outline-success", title='Outline Success'),
    SimpleTerm(value="outline-danger", title='Outline Danger'),
    SimpleTerm(value="outline-warning", title='Outline Warning'),
    SimpleTerm(value="outline-info", title='Outline Info'),
    SimpleTerm(value="outline-light", title='Outline Light'),
    SimpleTerm(value="outline-dark", title='Outline Dark')])


class IInteractiveTemplate(model.Schema):

    type_template = schema.Choice(
        title=_(u'Tipus de plantilla'),
        required=True,
        vocabulary=typeTemplateVocabulary,
    )

    content = schema.Choice(
        title=_(u'Continguts que alimenten la plantilla'),
        description=_(u'Podeu afegir continguts en aquest directori des del següent <a target="_blank" href="folder_contents">enllaç</a>'),
        required=True,
        vocabulary=contentVocabulary,
    )

    directives.widget(
        'collection',
        RelatedItemsFieldWidget,
        pattern_options={"selectableTypes": ["Collection"]},
    )

    collection = RelationChoice(
        title=_(u"Cerca una col·lecció"),
        required=False,
        vocabulary="plone.app.vocabularies.Catalog",
    )

    accordion_open_multiple = schema.Bool(
        title=_(u'Habilitar l\'opció de poder obrir variis acordió de la mateixa agrupació'),
        required=False,
    )

    accordion_open_first = schema.Bool(
        title=_(u'Obrir el primer acordió per defecte'),
        required=False,
    )

    carousel_type = schema.Choice(
        title=_(u'Tipus de carousel'),
        required=True,
        vocabulary=carouselTypeVocabulary,
        default="simple"
    )

    carousel_show_title = schema.Bool(
        title=_(u'Mostrar títol'),
        default=True,
        required=False,
    )

    carousel_show_description = schema.Bool(
        title=_(u'Mostrar descripció'),
        default=True,
        required=False,
    )

    carousel_auto = schema.Bool(
        title=_(u'Iniciar automàticament (No recomenable segons la accesibilitat web)'),
        required=False,
    )

    carousel_time = schema.Int(
        title=_(u'Temps en cambiar al següent element automàticament en segons (5 - 30)'),
        description=_(u''),
        min=5,
        max=30,
        default=10,
    )

    slide_size = schema.Int(
        title=_(u'Alçada de les imatges en px (40 - 400)'),
        min=40,
        max=400,
        default=80,
    )

    slide_time = schema.Int(
        title=_(u'Temps en recorrer totes les imatges en segons (5 - 120)'),
        min=5,
        max=120,
        default=30,
    )

    modal_type_btn = schema.Choice(
        title=_(u'Tipus de botó'),
        required=True,
        vocabulary=modalTypeBtnVocabulary,
        default="primary"
    )

    show_copy = schema.Bool(
        title=_(u'Mostrar botó per copiar el HTML de la plantilla'),
        default=True,
        required=False,
    )

    directives.widget('js', InteractiveTemplateContentJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)


@implementer(IInteractiveTemplate)
class InteractiveTemplate(Container):

    @property
    def b_icon_expr(self):
        return "bootstrap"

    def token(self):
        return 't' + secrets.token_hex(16)

    def elem_to_dict(self, index, first, elem):
        result = {
            'index': index,
            'first': first,
            'id': elem.id.replace('.', '-'),
            'title': elem.title,
            'description': elem.description,
            'text': elem.text.output if elem.text else elem.description,
            'url': elem.absolute_url()}

        if self.type_template != 'carousel':
            result.update({'image': elem.absolute_url() + '/@@images/image/preview' if getattr(elem, 'image', False) else ''})
        else:
            result.update({'image': elem.absolute_url() + '/@@images/image/preview' if getattr(elem, 'image', False) else '++theme++genweb6.theme/img/sample/default_image_sm.png'})

        return result

    def contents(self):
        contents = []
        first = True
        index = 0

        if self.content == 'inside':
            for elem in self:
                elem = self[elem]
                contents.append(self.elem_to_dict(index, first, elem))

                index += 1
                if first:
                    first = False

        elif self.content == 'collection':
            collection = self.collection.to_object
            for elem in collection.results():
                contents.append(self.elem_to_dict(index, first, elem.getObject()))

                index += 1
                if first:
                    first = False

        if self.type_template != 'imatge-slide':
            return contents
        else:
            return contents + contents


class View(BrowserView):
    pass
