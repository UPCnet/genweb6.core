# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView

from plone import api
from plone.subrequest import subrequest
from urllib.parse import urlencode
from zope.interface import alsoProvides

import json
import pkg_resources

try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


def listPloneSites(zope):
    """
Llista els plonesites disponibles
    """

    out = []
    for item in zope.values():
        if IFolder.providedBy(item) and not IPloneSiteRoot.providedBy(item):
            for site in item.values():
                if IPloneSiteRoot.providedBy(site):
                    out.append(site)
        elif IPloneSiteRoot.providedBy(item):
            out.append(item)
    return out


class list_plone_sites(BrowserView):
    """
Retorna una llista amb els plonesites disponibles en aquest Zope
    """

    def __call__(self):
        context = aq_inner(self.context)
        out = []
        for item in context.values():
            if IPloneSiteRoot.providedBy(item):
                out.append(item.id)
            elif IFolder.providedBy(item):
                for site in item.values():
                    if IPloneSiteRoot.providedBy(site):
                        out.append(item.id + '/' + site.id)
        return json.dumps(out)


class get_flavour_sites(BrowserView):
    """
Retorna l'última capa instal·lada per a cada plonesite
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        portal_skins = api.portal.get_tool(name='portal_skins')
        for plonesite in plonesites:
            out[plonesite.id] = portal_skins.getDefaultSkin()
        return json.dumps(out)


class get_languages_sites(BrowserView):
    """
Retorna els idiomes soportats per a cada lloc
    """
    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        portal_languages = api.portal.get_tool(name='portal_languages')
        for plonesite in plonesites:
            out[plonesite.id] = portal_languages.getSupportedLanguages()
        return json.dumps(out)


class get_default_language_sites(BrowserView):
    """
Retorna l'idioma predeterminat per a cada lloc
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        portal_languages = api.portal.get_tool(name='portal_languages')
        for plonesite in plonesites:
            out[plonesite.id] = portal_languages.getDefaultLanguage()
        return json.dumps(out)


class get_default_wfsites(BrowserView):
    """
Retorna el workflow predeterminat per a cada lloc
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        portal_workflow = api.portal.get_tool(name='portal_workflow')
        for plonesite in plonesites:
            out[plonesite.id] = portal_workflow.getDefaultChain()
        return json.dumps(out)


class bulk_action(BrowserView):
    """
Executeu una vista en totes les instancies

Paràmetre:
- view: vista a executar
- exclude_sites: sites a excluir, ex: Plone
    """

    def __call__(self):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        context = aq_inner(self.context)
        args = self.request.form
        view_name = self.request.form['view']
        exclude_sites = self.request.form.get('exclude_sites', '').split(',')
        plonesites = listPloneSites(context)
        output = []
        for plonesite in plonesites:
            if plonesite.id not in exclude_sites:
                print('======================')
                print('Executing view in {}'.format(plonesite.id))
                print('======================')
                quoted_args = urlencode(args)
                response = subrequest(
                    '/'.join(plonesite.getPhysicalPath()) + '/{}?{}'.format(view_name, quoted_args))
                output.append(
                    """<br/>-- Executed view {} in site {} --""".format(view_name, plonesite.id))
                output.append(response.getBody())
        return '\n'.join(output)


class nsp_bulk_action(BrowserView):
    """
Executeu una vista en totes les instancies, utilitzat només
en cas que alguna cosa no funcioni fent una subrequest!

Paràmetre:
- view: vista a executar
    """

    def __call__(self):
        context = aq_inner(self.context)
        args = self.request.form
        view_name = self.request.form['view']
        plonesites = listPloneSites(context)
        output = []
        for plonesite in plonesites:
            view = plonesite.restrictedTraverse(view_name)
            view.render(plonesite, **args)
            output.append('Executed view {} in site {}'.format(
                view_name, plonesite.id))
        return '\n'.join(output)


class list_ldap_info(BrowserView):
    """
Llista l'informació del LDAP de cada plonesite
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        acl_users = api.portal.get_tool(name='acl_users')
        for plonesite in plonesites:
            try:
                out[plonesite.id] = acl_users.ldapUPC.acl_users.getServers()
            except:
                print("Plonesite %s doesn't have a valid ldapUPC instance." %
                      plonesite.id)
        return json.dumps(out)
