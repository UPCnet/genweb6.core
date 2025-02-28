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
      "seofields", _("SEO"), fields=["seo_robots"],
    )

    seo_robots = schema.Choice(
        title=_("Metatag Robots"),
        description=_(
            "seo_robots_help",
            default=(
                "Select options that hint search engines how "
                "to treat this content. Typically listings are to "
                "navigate the site, but add little to no value in its "
                "own and should be set to 'noindex, follow'. In some "
                "cases you want a listing to be indexed. E.g. when "
                "publishing a Top 10 recipes list with extra content "
                "above and below the list, in which case you would use "
                "'index,follow'."
            ),
        ),
        vocabulary=seoRobotsVocabulary,
        required=False,
    )

alsoProvides(ISeo, IFormFieldProvider)


@implementer(ISeo)
class Seo(object):
    adapts(ISeo)

    def __init__(self, context):
        self.context = context

    def _set_seo_robots(self, value):
        self.context.seo_robots = value

    def _get_seo_robots(self):
        return getattr(self.context, 'seo_robots', None)

    seo_robots = property(_get_seo_robots, _set_seo_robots)
