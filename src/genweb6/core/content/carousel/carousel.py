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

contentVocabulary = SimpleVocabulary([
    SimpleTerm(value="--NOVALUE--", title=_(u'Selecciona una opció')),
    SimpleTerm(value="inside", title=_(u'Continguts de dintre d\'aquest directori')),
    SimpleTerm(value="collection", title=_(u'Col·lecció'))])

carouselTypeVocabulary = SimpleVocabulary([
    SimpleTerm(value="simple", title=_(u'Carrusel amb una imatge en pantalla')),
    SimpleTerm(value="complex", title=_(u'Carrusel amb quatre imatges en pantalla, en dispositius mòbils es redueix a una'))])


class ICarouselJSWidget(ITextWidget):
    pass


@implementer_only(ICarouselJSWidget)
class CarouselJSWidget(TextWidget):

    klass = u'carousel-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def CarouselJSFieldWidget(field, request):
    return FieldWidget(field, CarouselJSWidget(request))


class ICarousel(model.Schema):

    carousel_type = schema.Choice(
        title=_(u'Tipus de carousel'),
        required=True,
        vocabulary=carouselTypeVocabulary,
        default="simple"
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

    carousel_show_title = schema.Bool(
        title=_(u'Mostrar títol'),
        default=False,
        required=False,
    )

    carousel_show_description = schema.Bool(
        title=_(u'Mostrar descripció'),
        default=False,
        required=False,
    )

    carousel_enable_auto_proportions = schema.Bool(
        title=_(u'Forçar les proporcions de les imatges'),
        required=False,
    )

    show_copy = schema.Bool(
        title=_(u'Mostrar un botó (Copiar HTML) que permeti copiar el codi html generat per a poder inserir-ho en una altre lloc.'),
        default=True,
        required=False,
    )

    directives.widget('js', CarouselJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)


@implementer(ICarousel)
class Carousel(Container):

    @property
    def b_icon_expr(self):
        return "images"

    def token(self):
        return 't' + secrets.token_hex(16)

    def elem_to_dict(self, index, first, elem):
        result = {
            'index': index,
            'first': first,
            'id': elem.id.replace('.', '-'),
            'title': elem.title,
            'description': elem.description,
            'url': elem.absolute_url() + '/view'}

        if self.carousel_type == 'complex':
            result.update({'image': elem.absolute_url() + '/@@images/image/preview' if getattr(elem, 'image', False) else '++theme++genweb6.theme/img/sample/default_image.webp'})
        else:
            result.update({'image': elem.absolute_url() + '/@@images/image/huge' if getattr(elem, 'image', False) else '++theme++genweb6.theme/img/sample/default_image.webp'})

        return result

    def contents(self):
        contents = []
        first = True
        index = 0

        if self.content == 'collection':
            collection = self.collection.to_object
            for elem in collection.results():
                contents.append(self.elem_to_dict(index, first, elem.getObject()))

                index += 1
                if first:
                    first = False
        else:
            for elem in self:
                elem = self[elem]
                contents.append(self.elem_to_dict(index, first, elem))

                index += 1
                if first:
                    first = False

        return contents


class View(BrowserView):
    pass
