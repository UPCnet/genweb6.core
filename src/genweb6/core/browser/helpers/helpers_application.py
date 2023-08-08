# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView

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


class ping(BrowserView):
    """
    Vista de comoditat per al programari de monitorització.
    """

    def __call__(self):
        return '1'


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
                registry_tool = getToolByName(item, "portal_registry")
                defaultLanguage = registry_tool['plone.default_language']
                out.append({'site': item.id, 'lang': defaultLanguage})
            elif IFolder.providedBy(item):
                for site in item.values():
                    if IPloneSiteRoot.providedBy(site):
                        registry_tool = getToolByName(site, "portal_registry")
                        defaultLanguage = registry_tool['plone.default_language']
                        out.append({'site': item.id + '/' + site.id,
                                    'lang': defaultLanguage})
        return json.dumps(out)


class get_flavour_sites(BrowserView):
    """
    Retorna l'última capa instal·lada per a cada plonesite
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_skins = getToolByName(plonesite, 'portal_skins')
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
        for plonesite in plonesites:
            registry_tool = getToolByName(plonesite, "portal_registry")
            supportedLanguages = registry_tool['plone.available_languages']
            out[plonesite.id] = supportedLanguages
        return json.dumps(out)


class get_default_language_sites(BrowserView):
    """
    Retorna l'idioma predeterminat per a cada lloc
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            registry_tool = getToolByName(plonesite, "portal_registry")
            defaultLanguage = registry_tool['plone.default_language']
            out[plonesite.id] = defaultLanguage
        return json.dumps(out)


class get_default_wfsites(BrowserView):
    """
    Retorna el workflow predeterminat per a cada lloc
    """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_workflow = getToolByName(plonesite, 'portal_workflow')
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
                result = response.getBody()
                output.append(result
                              if isinstance(result, bytes) else result)

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
        for plonesite in plonesites:
            acl_users = getToolByName(plonesite, 'acl_users')
            try:
                out[plonesite.id] = acl_users.ldapUPC.acl_users.getServers()
            except:
                print("Plonesite %s doesn't have a valid ldapUPC instance." %
                      plonesite.id)
        return json.dumps(out)
