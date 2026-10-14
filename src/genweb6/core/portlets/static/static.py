# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.portlet.static.static import AddForm as BaseAddForm
from plone.portlet.static.static import Assignment as BaseAssignment
from plone.portlet.static.static import EditForm as BaseEditForm
from plone.portlet.static.static import IStaticPortlet
from plone.portlet.static.static import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer

from genweb6.core import _


class IGwStaticPortlet(IStaticPortlet):
    """Static text portlet extended with optional title hiding."""

    hide_title = schema.Bool(
        title=_(u"Amaga el títol?"),
        description=_(
            u"Marqueu aquesta casella per amagar el títol del portlet quan "
            u"es mostra amb contorn."
        ),
        required=False,
        default=False,
    )

    directives.order_after(hide_title='header')


@implementer(IGwStaticPortlet)
class Assignment(BaseAssignment):
    """Portlet assignment with hide_title support."""

    hide_title = False

    def __init__(
        self,
        header="",
        text="",
        omit_border=False,
        footer="",
        more_url="",
        hide_title=False,
    ):
        super().__init__(
            header=header,
            text=text,
            omit_border=omit_border,
            footer=footer,
            more_url=more_url,
        )
        self.hide_title = hide_title


class Renderer(BaseRenderer):
    """Portlet renderer that can hide the visible title."""

    render = ViewPageTemplateFile('static.pt')

    def hide_title(self):
        return getattr(self.data, 'hide_title', False)


class AddForm(BaseAddForm):
    schema = IGwStaticPortlet

    def create(self, data):
        return Assignment(**data)


class EditForm(BaseEditForm):
    schema = IGwStaticPortlet

    def getContent(self):
        """Portlets creats abans de l'extensió no tenen hide_title."""
        content = self.context
        if not hasattr(content, 'hide_title'):
            content.hide_title = False
        return content
