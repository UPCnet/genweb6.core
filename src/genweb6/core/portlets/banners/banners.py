# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer

from genweb6.core import _
from genweb6.core import utils


def validate_count(value):
    if value < 1 or value > 10:
        raise Invalid(_(u'El número de banners debe estar entre 1 y 10.'))
    return True

class IBannersPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=False)

    count = schema.Int(
        title=_(u'Number of banners to display'),
        description=_(u'How many banners to list.'),
        required=True,
        default=7,
        constraint=validate_count)


@implementer(IBannersPortlet)
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    def __init__(self, count=7, state=('published', )):
        self.count = count
        # self.state = state

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Genweb banners")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('banners.pt')

    def portal_url(self):
        return self.portal().absolute_url()

    def portal(self):
        return api.portal.get()

    def getBanners(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        limit = self.data.count
        lang = utils.pref_lang()
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        path = f'{root_path}/{lang}/banners-{lang}'

        return catalog.searchResults(portal_type='Banner',
                                     review_state=['published', 'intranet'],
                                     path=path,
                                     sort_on='getObjPositionInParent',
                                     sort_limit=limit)[:limit]

    def getAltAndTitle(self, altortitle, open_in_new_window):
        """ Funcio que extreu idioma actiu i afegeix al alt i al title de les imatges del banner
            el literal Obriu l'enllac en una finestra nova.
        """
        if open_in_new_window:
            return '%s, %s' % (altortitle, self.portal().translate(_('obrir_link_finestra_nova')))
        else:
            return '%s' % (altortitle)


class AddForm(base.AddForm):
    schema = IBannersPortlet
    label = _(u"Add banners portlet")
    description = _(u"This portlet displays the site banners.")

    def create(self, data):
        return Assignment(count=data.get('count', 7), state=data.get('state', ('published',)))


class EditForm(base.EditForm):
    schema = IBannersPortlet
    label = _(u"Edit banners portlet")
    description = _(u"This portlet displays the site banners.")
