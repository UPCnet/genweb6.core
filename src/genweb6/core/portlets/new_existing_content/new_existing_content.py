# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bs4 import BeautifulSoup
from plone import api
from plone.app.portlets.portlets import base
from plone.autoform import directives
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from pyquery import PyQuery as pq
from requests.exceptions import ReadTimeout
from requests.exceptions import RequestException
from z3c.form.browser.text import TextWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.widget import FieldWidget
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.interfaces import IField
from zope.site import hooks

from genweb6.core import GenwebMessageFactory as _

import DateTime
import re
import requests


class NotAnExternalLink(schema.ValidationError):
    __doc__ = _(u"This is an inner link")


def validate_externalurl(value):
    root_url = hooks.getSite().absolute_url()
    link_extern = value.lower()

    if root_url.startswith("http://"):
        root_url = root_url[7:]
    elif root_url.startswith("https://"):
        root_url = root_url[8:]

    if link_extern.startswith("http://"):
        link_extern = link_extern[7:]
    elif link_extern.startswith("https://"):
        link_extern = link_extern[8:]

    isInnerLink = link_extern.startswith(root_url)
    if isInnerLink:
        raise NotAnExternalLink(value)
    return not isInnerLink


class INewContentPortletJSWidget(ITextWidget):
    pass


@implementer_only(INewContentPortletJSWidget)
class NewContentPortletJSWidget(TextWidget):

    klass = u'new_existing_content-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def NewContentPortletJSFieldWidget(field, request):
    return FieldWidget(field, NewContentPortletJSWidget(request))


class INewContentPortlet(IPortletDataProvider):
    """A portlet which can render an existing content
    """

    ptitle = schema.TextLine(
        title=_(u"Títol del portlet"),
        description=_(u"help_static_content_title_ca"),
        required=False,
        default=_(u"")
    )

    show_title = schema.Bool(
        title=_(u"Mostra el títol?"),
        description=_(
            u"Marqueu aquesta casella si voleu que es mostri el títol del portlet"),
        required=False,
        default=True,
    )

    hide_footer = schema.Bool(
        title=_(u"Omet el contorn del portlet"),
        description=_(
            u"Marqueu aquesta casella si es desitja que el text mostrat a dalt sigui visualitzat sense la capçalera, el contorn o el peu estàndard"),
        required=False,
        default=False,
    )

    content_or_url = schema.Choice(
        title=(u"Tipus de contingut"),
        description=(u"Escull el tipus de contingut que vols"),
        required=True,
        values=['EXTERN', 'INTERN']
    )

    external_url = schema.URI(
        title=_(u"EXTERN: URL de la pàgina a mostrar"),
        description=_(u"help_static_content_url_ca"),
        required=False,
        constraint=validate_externalurl,
    )

    own_content = RelationChoice(
        title=_(u"INTERN: Existing content",
                default=u"INTERN: Existing content"),
        description=_(u'help_existing_content',
                      default=u"You may search for and choose an existing content"),
        required=False,
        vocabulary='plone.app.vocabularies.Catalog',
    )

    element = schema.TextLine(
        title=_(u"Element de la pàgina a mostrar, per defecte #content-core"),
        description=_(u"help_static_content_element_ca"),
        required=True,
        default=_(u"#content-core")
    )

    directives.widget('js', NewContentPortletJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)

    @invariant
    def validate_isFull(data):
        if data.content_or_url == 'INTERN' and not data.own_content:
            raise Invalid(_(u"Falta seleccionar el contingut intern"))
        elif data.content_or_url == 'EXTERN' and not data.external_url:
            raise Invalid(_(u"Falta l'enllaç extern"))


@implementer(INewContentPortlet)
class Assignment (base.Assignment):

    def __init__(self, ptitle=u"", content_or_url='EXTERN', external_url='#', own_content=None, element='#content-core', show_title=True, hide_footer=False, js=u""):
        self.ptitle = ptitle
        self.show_title = show_title
        self.hide_footer = hide_footer
        self.content_or_url = content_or_url
        self.external_url = external_url
        self.element = element
        self.own_content = own_content
        self.js = js

    @property
    def title(self):
        return self.ptitle or _(u"Existing Content")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('new_existing_content.pt')

    def check_configuration_error(self):
        pm = api.portal.get_tool(name='portal_membership')
        user = pm.getAuthenticatedMember()
        roles = user.getRoles()
        if ('WebMaster' in roles) or ('Manager' in roles):
            if self.data.content_or_url == 'INTERN' and not self.data.own_content.to_path:
                return _(u"Configura el contingut intern")

            if self.data.content_or_url == 'EXTERN' and not self.data.external_url:
                return _(u"Configura el contingut extern")

        return None

    @memoize
    def get_catalog_content(self):
        """ Fem una consulta al catalog, en comptes de fer un PyQuery """
        owncontent_obj = self.data.own_content
        if owncontent_obj and isinstance(owncontent_obj, RelationValue):
            owncontent_obj = owncontent_obj.to_object

        if owncontent_obj:
            pw = api.portal.get_tool('portal_workflow')
            review_state = pw.getInfoFor(owncontent_obj, 'review_state')
            if review_state in ['published', 'intranet']:
                return owncontent_obj

        return _(u"Configura el contingut intern")


    def checkContentIsPublic(self):
        try:
            if self.data.content_or_url == 'INTERN':
                content = self.get_catalog_content()
                if not content.expiration_date:
                    return True

                now = DateTime.DateTime()
                return now >= content.effective_date and now <= content.expiration_date
            else:
                return True
        except:
            return False

    def getHTML(self):
        """ Agafa contingut de 'Element' de la 'URL', paràmetres definits per l'usuari
            Avisa si hi ha problemes en la URL o si no troba Element.
        """
        content = ''
        try:
            # CONTINGUT INTERN #
            if self.data.content_or_url == 'INTERN':
                # link intern, search through the catalog
                raw_html = self.get_catalog_content()()
                clean_html = re.sub(r'[\n\r]?', r'', raw_html)
                doc = pq(clean_html)
                if doc(self.data.element):
                    content = pq('<div/>').append(doc(self.data.element).outerHtml()).html(method='html')
                else:
                    content = _(u"ERROR. This element does not exist:") + " " + self.data.element

            # CONTENIDO EXTERNO #
            elif self.data.content_or_url == 'EXTERN':
                # link extern, pyreq
                link_extern = self.data.external_url
                headers = {'Accept-Language': self.context.language}
                raw_html = requests.get(link_extern, headers=headers, verify=False, timeout=5)
                clean_html = re.sub(r'[\n\r]?', r'', raw_html.text)
                doc = pq(clean_html)
                if doc(self.data.element):
                    content = pq('<div/>').append(doc(self.data.element).outerHtml()).html(method='html')
                else:
                    content = _(u"ERROR. This element does not exist:") + " " + self.data.element

            # PORTLET MALAMENT CONFIGURAT #
            else:
                content = _(u"ERROR. Review the portlet configuration.")

        except ReadTimeout:
            content = _(u"ERROR. There was a timeout.")
        except RequestException:
            content = _(u"ERROR. This URL does not exist")
        except:
            content = _(u"ERROR. Charset undefined")

        soup = BeautifulSoup(clean_html, "html.parser")
        body = soup.find_all("body")
        if body:
            class_body = body[0].get("class", [])
            valid_class = [valid for valid in class_body if valid.startswith('template-') or valid.startswith('portaltype-')]
            content = str('<div class="existing-content ' + ' '.join(valid_class) + '">' + content + '</div>')

        return content

    def getTitle(self):
        return self.data.ptitle

    def showTitle(self):
        return self.data.show_title

    def getClass(self):
        if self.data.hide_footer:
            return 'existing_content_portlet_no_border'
        else:
            return 'existing_content_portlet'


class AddForm(base.AddForm):
    schema = INewContentPortlet
    label = _(u"Afegeix portlet de contingut existent")
    description = _(
        u"Aquest portlet mostra contingut ja existent en URL específica.")

    def create(self, data):
        # s'invoca despres de __init__ en clicar Desa
        assignment = Assignment(**data)
        return assignment


class EditForm(base.EditForm):
    schema = INewContentPortlet
    label = _(u"Edita portlet de contingut existent")
    description = _(
        u"Aquest portlet mostra contingut ja existent en URL específica.")
