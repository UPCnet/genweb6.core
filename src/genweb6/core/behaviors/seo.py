# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexteritySchema
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _


seoRobotsVocabulary = SimpleVocabulary([
    SimpleTerm(value="index, nofollow", title=_(u'index, nofollow')),
    SimpleTerm(value="noindex, follow", title=_(u'noindex, follow')),
    SimpleTerm(value="index, follow", title=_(u'index, follow')),
    SimpleTerm(value="noindex", title=_(u'noindex')),
    SimpleTerm(value="noindex, nofollow", title=_(u'noindex, nofollow'))])


class ISeo(model.Schema, IDexteritySchema):
    """Add open in new window field to link content
    """

    model.fieldset(
      "seofields", _("SEO"), fields=["seo_title", "seo_description", "seo_robots"],
    )

    seo_title = schema.TextLine(
        title=_("SEO Title"),
        description=_("S'utilitza al títol de la secció 'head' de la pàgina web"),
        required=False,
    )

    seo_description = schema.Text(
        title=_("SEO Description"),
        description=_("S'utilitza a la descripció de la secció 'head' de la pàgina web"),
        required=False,
    )

    seo_robots = schema.Choice(
        title=_("Metatag Robots"),
        description=_("<ul><li><span class='fw-bold'>No value (per defecte):</span> Els motors de cerca indexen la pàgina i segueixen els enllaços (comportament per defecte).</li><li><span class='fw-bold'>index, nofollow:</span> Indexa la pàgina, però no segueix els enllaços que conté.</li><li><span class='fw-bold'>noindex, follow:</span> No indexa la pàgina, però sí que segueix els enllaços.</li><li><span class='fw-bold'>index, follow:</span> Indexa la pàgina i segueix els enllaços (equivalent a no especificar res).</li><li><span class='fw-bold'>noindex:</span> No indexa la pàgina i no segueix els enllaços.</li><li><span class='fw-bold'>noindex, nofollow:</span> No indexa la pàgina ni segueix els enllaços.</li></ul>"),
        vocabulary=seoRobotsVocabulary,
        required=False,
    )

alsoProvides(ISeo, IFormFieldProvider)


@implementer(ISeo)
class Seo(object):
    adapts(ISeo)

    def __init__(self, context):
        self.context = context

    def _set_seo_title(self, value):
        self.context.seo_title = value

    def _get_seo_title(self):
        return getattr(self.context, 'seo_title', None)

    seo_title = property(_get_seo_title, _set_seo_title)

    def _set_seo_description(self, value):
        self.context.seo_description = value

    def _get_seo_description(self):
        return getattr(self.context, 'seo_description', None)

    seo_description = property(_get_seo_description, _set_seo_description)

    def _set_seo_robots(self, value):
        self.context.seo_robots = value

    def _get_seo_robots(self):
        return getattr(self.context, 'seo_robots', None)

    seo_robots = property(_get_seo_robots, _set_seo_robots)
