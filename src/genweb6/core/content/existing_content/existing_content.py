# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import getSecurityManager
from Products.Five.browser import BrowserView

from bs4 import BeautifulSoup
from plone import api
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.content import Container
from plone.supermodel import model
from pyquery import PyQuery as pq
from requests.exceptions import ReadTimeout
from requests.exceptions import RequestException
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant

from genweb6.core import GenwebMessageFactory as _
from genweb6.core.portlets.new_existing_content.new_existing_content import NewContentPortletJSFieldWidget
from genweb6.core.validations import validate_externalurl

import DateTime
import logging
import re
import requests

logger = logging.getLogger("genweb6.core")

class IExistingContent(model.Schema):

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

@implementer(IExistingContent)
class ExistingContent(Container):
    """ Implementación de ExistingContent """

class ExistingContentView(BrowserView):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.data = {}

    def check_configuration_error(self):

        pm = api.portal.get_tool(name='portal_membership')
        user = pm.getAuthenticatedMember()
        roles = user.getRoles()
        if ('WebMaster' in roles) or ('Manager' in roles):
            if self.context.content_or_url == 'INTERN' and not self.context.own_content:
                return _(u"Configura el contingut intern")
            if self.context.content_or_url == 'EXTERN' and not self.context.external_url:
                return _(u"Configura el contingut extern")
        return ""

    def get_catalog_content(self):
        """Obtiene contenido de un tipo de contenido usando el catálogo."""
        owncontent_obj = self.context.own_content
        if owncontent_obj and isinstance(owncontent_obj, RelationValue):
            owncontent_obj = owncontent_obj.to_object
            if not owncontent_obj:
                return ''

            sm = getSecurityManager()
            if sm.checkPermission('View', owncontent_obj):
                now = DateTime.DateTime()
                if owncontent_obj.effective_date and now < owncontent_obj.effective_date:
                    return ''
                if owncontent_obj.expiration_date and now > owncontent_obj.expiration_date:
                    return ''
            else:
                return ''

            if owncontent_obj.portal_type == 'Document' and self.context.element == '#content-core':
                logger.info(f"[{self.context.virtual_url_path()}] Existing internal document: {owncontent_obj.portal_type}")
                return owncontent_obj.text.raw
            else:
                clean_html = re.sub(r'[\n\r]?', r'', owncontent_obj())
                doc = pq(clean_html)
                if doc(self.context.element):
                    content = pq('<div/>').append(doc(self.context.element).outerHtml()).html(method='html')
                else:
                    content = _(u"ERROR. This element does not exist:") + " " + self.context.element

                soup = BeautifulSoup(clean_html, "html.parser")
                body = soup.find_all("body")
                if body:
                    class_body = body[0].get("class", [])
                    valid_class = [valid for valid in class_body if valid.startswith('template-') or valid.startswith('portaltype-')]
                    content = str('<div class="existing-content ' + ' '.join(valid_class) + '">' + content + '</div>')
                return content

        return ''

    def getHTML(self):
        """Obtiene contenido HTML del elemento especificado de una URL o tipo de contenido."""
        content = ''
        try:
            if self.context.content_or_url == 'INTERN':
                content = self.get_catalog_content()

            elif self.context.content_or_url == 'EXTERN':
                link_extern = self.context.external_url
                headers = {'Accept-Language': self.context.language}
                raw_html = requests.get(link_extern, headers=headers, verify=False, timeout=2)

                if not raw_html.text.strip():
                    content = _(u"ERROR. No content was received from the requested page.")
                else:
                    clean_html = re.sub(r'[\n\r]?', r'', raw_html.text)
                    doc = pq(clean_html)
                    if doc(self.context.element):
                        content = pq('<div/>').append(doc(self.context.element).outerHtml()).html(method='html')
                    else:
                        content = _(u"ERROR. This element does not exist:") + " " + self.context.element

                    soup = BeautifulSoup(clean_html, "html.parser")
                    body = soup.find_all("body")
                    if body:
                        class_body = body[0].get("class", [])
                        valid_class = [valid for valid in class_body if valid.startswith('template-') or valid.startswith('portaltype-')]
                        content = str('<div class="existing-content ' + ' '.join(valid_class) + '">' + content + '</div>')

            else:
                content = _(u"ERROR. Review the content configuration.")

        except ReadTimeout:
            content = _(u"ERROR. There was a timeout.")
        except RequestException:
            content = _(u"ERROR. This URL does not exist.")
        except Exception:
            content = _(u"ERROR. Charset undefined.")

        return content or ""

    def getClass(self):
        """Obtiene la clase del contenido, ahora como 'existing-content'."""
        return "existing-content"