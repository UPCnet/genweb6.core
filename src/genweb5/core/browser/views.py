# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.contentprovider import interfaces
from zope.interface import implementer

from genweb5.core import GenwebMessageFactory as _
from genweb5.core.adapters import IImportant
from genweb5.core.portlets.manage_portlets.manager import ISpanStorage
from genweb5.core.interfaces import IHomePage
from genweb5.core.interfaces import IHomePageView
from genweb5.core.utils import pref_lang


class GetDXDocumentText(BrowserView):

    def __call__(self):
        return self.context.text.output


class TemplateList(BrowserView):
    """ Override of the default way of obtaining the TinyMCE template list """

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/javascript')
        registry = queryUtility(IRegistry)
        templates = {}

        if registry is not None:
            templateDirectories = registry.get(
                'collective.tinymcetemplates.templateLocations', None)
            if templateDirectories:

                portal_catalog = api.portal.get_tool('portal_catalog')
                portal_path = '/'.join(api.portal.get().getPhysicalPath())
                absolute_url = api.portal.get().absolute_url()
                paths = []
                for p in templateDirectories:
                    if p.startswith('/'):
                        p = p[1:]
                    paths.append('%s/%s' % (portal_path, p,))

                templates['1. DESTACATS'] = [['Destacat', absolute_url + '/templates/destacat/genweb.get.dxdocument.text', 'Text destacat.'],
                                             ['Destacat color', absolute_url + '/templates/destacat-color/genweb.get.dxdocument.text',
                                                 'Destacat amb text m\xc3\xa9s gran i color.'],
                                             ['Destacat contorn', absolute_url + '/templates/destacat-contorn/genweb.get.dxdocument.text', 'Destacat amb text petit.'],
                                             ['Pou', absolute_url + '/templates/pou/genweb.get.dxdocument.text',
                                                 'Contenidor de pou per encabir elements i limitar-los visualment.'],
                                             ['Pou degradat', absolute_url + '/templates/pou-degradat/genweb.get.dxdocument.text',
                                                 'Contenidor de pou per encabir elements i limitar-los visualment amb fons degradat.'],
                                             ['Caixa', absolute_url + '/templates/caixa/genweb.get.dxdocument.text',
                                                 'Contenidor de caixa per encabir elements i limitar-los visualment.'],
                                             ['Caixa degradat', absolute_url + '/templates/caixa-degradat/genweb.get.dxdocument.text', 'Contenidor de caixa per encabir elements i limitar-los visualment amb fons degradat.']]

                templates['2. COLUMNES'] = [['2 columnes de text', absolute_url + '/templates/2-columnes-de-text/genweb.get.dxdocument.text', "A cada columna s'hi poden afegir altres plantilles."],
                                            ['3 columnes de text', absolute_url + '/templates/3-columnes-de-text/genweb.get.dxdocument.text',
                                                "A cada columna s'hi poden afegir altres plantilles."],
                                            ['4 columnes de text', absolute_url + '/templates/4-columnes-de-text/genweb.get.dxdocument.text',
                                                "A cada columna s'hi poden afegir altres plantilles."],
                                            ['2/3 vs 1/3 columnes de text', absolute_url + '/templates/2-3-vs-1-3-columnes-de-text/genweb.get.dxdocument.text',
                                                "A cada columna s'hi poden afegir altres plantilles."],
                                            ['3/4 vs 1/4 columnes de text', absolute_url + '/templates/3-4-vs-1-4-columnes-de-text/genweb.get.dxdocument.text',
                                                "A cada columna s'hi poden afegir altres plantilles."],
                                            ['Combinacions de columnes', absolute_url + '/templates/combinacions-de-columnes/genweb.get.dxdocument.text', "Podeu fer d'1 a 4 columnes i fusionar-les entre elles. Elimineu les combinacions que no us interessin i treballeu amb el columnat que us agradi m\xc3\xa9s."]]

                templates['3. CONTINGUTS (TEXT, BOTONS, BÀNERS, LLISTATS)'] = [['Llistat \xc3\xadndex', absolute_url + '/templates/llistat-index/genweb.get.dxdocument.text', '\xc3\x8dndex de continguts.'],
                                                                               ['Llistat enlla\xc3\xa7os', absolute_url + '/templates/llistat-enllacos/genweb.get.dxdocument.text',
                                                                                   "Per afegir un llistat d'enlla\xc3\xa7os relacionats."],
                                                                               ['Llistat destacat', absolute_url + '/templates/llistat-destacat/genweb.get.dxdocument.text',
                                                                                   "Per afegir un llistat d'enlla\xc3\xa7os destacats."],
                                                                               ['Text amb tots els titulars', absolute_url + '/templates/text-amb-tots-els-titulars/genweb.get.dxdocument.text',
                                                                                   'Com utilitzar la jerarquia de t\xc3\xadtols. \xc3\x89s important respectar aquesta jerarquia si volem ser accessibles i millorar el nostre posicionament a Internet.'],
                                                                               ['Text amb video', absolute_url + '/templates/text-amb-video/genweb.get.dxdocument.text',
                                                                                   "Per inserir-hi el vostre v\xc3\xaddeo heu d'accedir al codi html de la p\xc3\xa0gina i substituir l'enlla\xc3\xa7 al v\xc3\xaddeo."],
                                                                               ['Assenyalar enlla\xc3\xa7os', absolute_url + '/templates/assenyalar-enllacos/genweb.get.dxdocument.text',
                                                                                   "Classes que es poden afegir als enlla\xc3\xa7os per indicar el tipus d'element enlla\xc3\xa7at."],
                                                                               ['Bot\xc3\xb3 ample blau', absolute_url + '/templates/boto-ample-blau/genweb.get.dxdocument.text',
                                                                                   "Bot\xc3\xb3 standard blau que ocupa el 100% de l'ample del contenidor"],
                                                                               ['Bot\xc3\xb3 ample gris', absolute_url + '/templates/boto-ample-gris/genweb.get.dxdocument.text',
                                                                                   "Bot\xc3\xb3 standard gris que ocupa el 100% de l'ample del contenidor"],
                                                                               ['Bot\xc3\xb3 blau', absolute_url + '/templates/boto-blau/genweb.get.dxdocument.text', 'Bot\xc3\xb3 standard blau'],
                                                                               ['Bot\xc3\xb3', absolute_url + '/templates/boto/genweb.get.dxdocument.text', 'Bot\xc3\xb3 standard gris']]

                templates['4. TAULES'] = [['Taula', absolute_url + '/templates/taula/genweb.get.dxdocument.text', 'Taula sense estils.'],
                                          ['Taula colors destacats', absolute_url + '/templates/taula-colors-destacats/genweb.get.dxdocument.text', 'Taula amb colors destacats.'],
                                          ['Taula de registres per files', absolute_url + '/templates/taula-de-registres-per-files/genweb.get.dxdocument.text',
                                              'Per definir una taula de registres estructurada per columnes. Es pot ampliar en files i columnes.'],
                                          ['Taula amb estils', absolute_url + '/templates/taula-amb-estils/genweb.get.dxdocument.text',
                                              'Una taula amb vora, destacat ombrejat en passar per sobre amb el ratol\xc3\xad i diferenciaci\xc3\xb3 de columnes en diferents colors.'],
                                          ['Taula amb files destacades', absolute_url + '/templates/taula-amb-files-destacades/genweb.get.dxdocument.text', 'Una taula amb vora, diferenciaci\xc3\xb3 de primera fila i columna.']]

                templates['5. COMPOSICIONS'] = [['Columna de suport', absolute_url + '/templates/columna-de-suport/genweb.get.dxdocument.text', 'Afegiu enlla\xc3\xa7os i contingut de suport a la columna de la dreta.'],
                                                ['Calendari', absolute_url + '/templates/calendari/genweb.get.dxdocument.text',
                                                    "Per representar gr\xc3\xa0ficament els esdeveniments o activitats d'un mes determinat. Es pot representar tot un any afegint successivament un mes darrera l'altre."],
                                                ['Fitxa', absolute_url + '/templates/fitxa/genweb.get.dxdocument.text',
                                                    'Contenidor de fitxa.'],
                                                ['\xc3\x80lbum de fotografies', absolute_url + '/templates/album-de-fotografies/genweb.get.dxdocument.text',
                                                    'Crea un \xc3\xa0lbum amb les miniatures de fotografies.'],
                                                ["Imatge alineada a l'esquerra amb text ", absolute_url + '/templates/imatge-alineada-a-lesquerra-amb-text/genweb.get.dxdocument.text', "Imatge alineada a l'esquerra amb text."],
                                                ['Imatge alineada a la dreta amb text ', absolute_url + '/templates/imatge-alineada-a-la-dreta-amb-text/genweb.get.dxdocument.text', 'Imatge alineada a la dreta amb text.'],
                                                ['Imatge amb text lateral superposat', absolute_url + '/templates/imatge-amb-text-lateral-superposat/genweb.get.dxdocument.text',
                                                    'Imatge damunt la qual hi apareix un text superposat.'],
                                                ['Imatge amb text superposat clar', absolute_url + '/templates/imatge-amb-text-superposat-clar/genweb.get.dxdocument.text',
                                                    'Imatge amb text superposat en un bloc inferior clar amb text fosc'],
                                                ['Imatge amb text superposat fosc', absolute_url + '/templates/imatge-amb-text-superposat-fosc/genweb.get.dxdocument.text', 'Imatge amb text superposat en un bloc inferior fosc amb text blanc']]

                templates['6. AVANÇADES'] = [["Carousel d'imatges", absolute_url + '/templates/carousel-dimatges/genweb.get.dxdocument.text', "Carousel d'imatges navegables."],
                                             ['Zoom imatge', absolute_url + '/templates/zoom-imatge/genweb.get.dxdocument.text', "Imatge que s'amplia."],
                                             ['Pestanyes', absolute_url + '/templates/pestanyes/genweb.get.dxdocument.text',
                                                 'Contingut segmentat per pestanyes amb un altre estil.'],
                                             ['Pestanyes caixa', absolute_url + '/templates/pestanyes-caixa/genweb.get.dxdocument.text',
                                                 'Contingut segmentat per pestanyes.'],
                                             ['Acordi\xc3\xb3', absolute_url + '/templates/acordio/genweb.get.dxdocument.text', "Acordi\xc3\xb3 d'opcions."]]

                results = portal_catalog.searchResults(Language='',
                                                       path=paths[1],
                                                       object_provides=IDocument.__identifier__,
                                                       sort_on='getObjPositionInParent')

                templates['7. PRÒPIES'] = []
                for r in results:
                    templates['7. PRÒPIES'].append(
                        [r.Title, '%s/genweb.get.dxdocument.text' % r.getURL(), r.Description])

                qi = api.portal.get_tool(name='portal_quickinstaller')
                if qi.isProductInstalled('genweb.robtheme'):
                    templates['1. DESTACATS'] += [['Rob Theme - Caixa amb llista - fons gris', absolute_url + '/templates/rob-theme-caixa-amb-llista-fons-gris/genweb.get.dxdocument.text', ''],
                                                  ['Rob Theme - Caixa amb llista - fons verd', absolute_url + '/templates/rob-theme-caixa-amb-llista-fons-verd/genweb.get.dxdocument.text', ''],
                                                  ['Rob Theme - Frase destacada', absolute_url + '/templates/rob-theme-frase-destacada/genweb.get.dxdocument.text', ''],
                                                  ['Rob Theme - Destacat amb imatge', absolute_url + '/templates/rob-theme-destacat-amb-imatge/genweb.get.dxdocument.text', '']]

                    templates['3. CONTINGUTS (TEXT, BOTONS, BÀNERS, LLISTATS)'] += [['Rob Theme - B\xc3\xa0ner gris amb icona Info', absolute_url + '/templates/rob-theme-baner-gris-amb-icona-info/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner blau amb icona Info', absolute_url + '/templates/rob-theme-baner-blau-amb-icona-info/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner blau', absolute_url + '/templates/rob-theme-baner-blau/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner gris', absolute_url + '/templates/rob-theme-baner-gris/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner vermell danger', absolute_url + '/templates/rob-theme-baner-vermell-danger/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner groc warning', absolute_url + '/templates/rob-theme-baner-groc-warning/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner verd success', absolute_url + '/templates/rob-theme-baner-verd-success/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - B\xc3\xa0ner amb imatge de fons', absolute_url + '/templates/rob-theme-baner-amb-imatge-de-fons/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - Llista amb subllista', absolute_url + '/templates/rob-theme-llista-amb-subllista/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - Llistat opcions amb icones lletres - 2 col', absolute_url + '/templates/rob-theme-llistat-opcions-amb-icones-lletres-2-col/genweb.get.dxdocument.text', ''],
                                                                                    ['Rob Theme - Conjunt imatge amb llista opcions - 3 col', absolute_url + '/templates/rob-theme-conjunt-imatge-amb-llista-opcions-3-col/genweb.get.dxdocument.text', '']]

                    templates['5. COMPOSICIONS'] += [['Rob Theme - Columna de suport', absolute_url + '/templates/rob-theme-columna-de-suport/genweb.get.dxdocument.text', ''],
                                                     ['Rob Theme - Destacat amb dades num\xc3\xa8riques', absolute_url + '/templates/rob-theme-destacat-amb-dades-numeriques/genweb.get.dxdocument.text', ''],
                                                     ['Rob Theme - Graella d\'imatges amb enllaços', absolute_url + '/templates/rob-theme-graella-dimatges-amb-enllacos/genweb.get.dxdocument.text', '']]

                    templates['6. AVANÇADES'] += [['Rob Theme - Acordi\xc3\xb3', absolute_url + '/templates/rob-theme-acordio/genweb.get.dxdocument.text', '']]

        return u'var tinyMCETemplateList = %s;' % templates


class gwToggleIsImportant(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_important = IImportant(context).is_important
        if is_important:
            IImportant(context).is_important = False
            confirm = _(u'L\'element s\'ha desmarcat com important')
        else:
            IImportant(context).is_important = True
            confirm = _(u'L\'element s\'ha marcat com important')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class HomePageBase(BrowserView):

    """
    Base methods for ease the extension of the genweb homePage view. Just
    define a new class inheriting from this one and redefine the basic
    grokkers like:

    Overriding the one in this module (homePage) with a more specific
    interface.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portlet_container = self.getPortletContainer()

    def getPortletContainer(self):
        context = aq_inner(self.context)
        container = context

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if INavigationRoot.providedBy(self.context):
            pc = api.portal.get_tool(name='portal_catalog')
            # Add the use case of mixin types of IHomepages. The main ones of a
            # non PAM-enabled site and the possible inner ones.
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      portal_type='Document',
                                      Language=pref_lang())
            if result:
                # Return the object without forcing a getObject()
                container = getattr(context, result[0].id, context)

        return container

    def renderProviderByName(self, provider_name):
        provider = queryMultiAdapter(
            (self.portlet_container, self.request, self),
            interfaces.IContentProvider, provider_name)

        provider.update()

        return provider.render()

    def getSpanValueForManager(self, manager):
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((self.portlet_container, portletManager), ISpanStorage)
        span = spanstorage.span
        if span:
            return span
        else:
            return '4'

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.portlet_container
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible

    def is_visible(self):
        """ This method lookup for the physical welcome page and checks if the
            user has the permission to view it. If it doesn't raises an
            unauthorized (login)
        """
        portal = api.portal.get()
        pc = api.portal.get_tool('portal_catalog')
        result = pc.unrestrictedSearchResults(object_provides=IHomePage.__identifier__,
                                              Language=pref_lang())
        if result:
            portal.restrictedTraverse(result[0].getPath())
            return True
        else:
            return False


@implementer(IHomePageView)
class homePage(HomePageBase):
    """ This is the special view for the homepage containing support for the
        portlet managers provided by the package genweb.portlets.
        It's restrained to IGenwebTheme layer to prevent it will interfere with
        the one defined in the Genweb legacy theme (v3.5).
    """
    pass


@implementer(IHomePageView)
class subHomePage(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass


@implementer(IHomePageView)
class SubhomeView(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass
