# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import timedelta
from plone import api
from plone.app.event.base import localized_now
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from urllib.parse import parse_qs
from z3c.relationfield.relation import create_relation
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides

from genweb6.core import utils
from genweb6.core.portlets.manage_portlets.manager import ISpanStorage
from genweb6.core.interfaces import IEventFolder
from genweb6.core.interfaces import IHomePage
from genweb6.core.interfaces import INewsFolder
from genweb6.core.interfaces import IProtectedContent

import logging
import pkg_resources

NEWS_QUERY = [{'i': u'portal_type', 'o': u'plone.app.querystring.operation.selection.any', 'v': [u'News Item', u'Link']},
              {'i': u'review_state', 'o': u'plone.app.querystring.operation.selection.any', 'v': [u'published', u'intranet']},
              {'i': u'path', 'o': u'plone.app.querystring.operation.string.relativePath', 'v': u'..'}]
QUERY_SORT_ON = u'effective'
EVENT_QUERY = [{'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.any', 'v': [u'Event']},
               {'i': 'start', 'o': 'plone.app.querystring.operation.date.afterToday', 'v': ''},
               {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.any', 'v': [u'published', u'intranet']}]


class setup(BrowserView):

    render = ViewPageTemplateFile("views_templates/setup_view.pt")

    def __call__(self):
        base_url = "%s/@@setup-view" % str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        qs = self.request.get('QUERY_STRING', None)

        if qs is not None:
            query = parse_qs(qs)

            if 'createcontent' in query:
                logger = logging.getLogger('Genweb: Executing setup-view on site -')
                logger.info('%s' % self.context.id)
                self.apply_default_language_settings()
                # if not api.portal.get_registry_record(name='genweb.hidden_settings.languages_applied'):
                #     self.apply_default_language_settings()
                #     api.portal.set_registry_record('genweb.hidden_settings.languages_applied', True)
                self.setup_multilingual()
                self.createContent()
                self.request.response.redirect(base_url)
                # self.setGenwebProperties()

            if 'createcontentmigration' in query:
                logger = logging.getLogger('Genweb: Executing setup-view on site -')
                logger.info('%s' % self.context.id)
                self.createContentMigration()
                self.request.response.redirect(base_url)

            if 'createexamples' in query:
                logger = logging.getLogger('Genweb: Executing setup-view Examples on site -')
                logger.info('%s' % self.context.id)
                self.createExampleContent()
                self.request.response.redirect(base_url)

            return self.render()

    def contentStatus(self):
        objects = [(u'Notícies', [('noticies', 'ca'), ('noticias', 'es'), ('news', 'en')]),
                   ('Esdeveniments', [('esdeveniments', 'ca'), ('eventos', 'es'), ('events', 'en')]),
                   ('Banners', [('banners-ca', 'ca'), ('banners-es', 'es'), ('banners-en', 'en')]),
                   ('LogosFooter', [('logosfooter-ca', 'ca'), ('logosfooter-es', 'es'), ('logosfooter-en', 'en')]),
                   ('Homepage', [('benvingut', 'ca'), ('bienvenido', 'es'), ('welcome', 'en')]),
                   ('Plantilles', [('plantilles', 'root')]),
                   ]

        result = []
        portal = api.portal.get()

        for o in objects:
            tr = [o[0]]
            for td, lang in o[1]:
                if lang == 'root':
                    tr.append(getattr(portal, td, False) and 'Creat' or 'No existeix')
                else:
                    if getattr(portal, lang, False):
                        tr.append(getattr(portal[lang], td, False) and 'Creat' or 'No existeix')
                    else:
                        tr.append('No existeix')
            result.append(tr)
        return result

    def apply_default_language_settings(self):
        registry = getUtility(IRegistry)
        registry["plone.available_languages"] = ['ca', 'es', 'en']

    def setup_multilingual(self):
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.context, False)

    def createContentMigration(self):
        portal = api.portal.get()
        portal_ca = portal['ca']
        portal_en = portal['en']
        portal_es = portal['es']

        welcome = portal_en['welcome']
        bienvenido = portal_es['bienvenido']
        benvingut = portal_ca['benvingut']

        self.link_translations([(benvingut, 'ca'), (bienvenido, 'es'), (welcome, 'en')])

        alsoProvides(portal_ca, IHomePage)
        alsoProvides(portal_en, IHomePage)
        alsoProvides(portal_es, IHomePage)

        alsoProvides(benvingut, IHomePage)
        alsoProvides(bienvenido, IHomePage)
        alsoProvides(welcome, IHomePage)

        benvingut.exclude_from_nav = True
        bienvenido.exclude_from_nav = True
        welcome.exclude_from_nav = True

        benvingut.reindexObject()
        bienvenido.reindexObject()
        welcome.reindexObject()

        portal_en.setLayout('homepage')
        portal_es.setLayout('homepage')
        portal_ca.setLayout('homepage')

        portal_en.reindexObject()
        portal_es.reindexObject()
        portal_ca.reindexObject()

        links_string_ca = u"""Editeu a la pàgina "Enllaços personalitzats", que trobareu a l’arrel de català, els vostres enllaços del peu personalitzats."""
        links_string_es = u"""Editad en la página "Enlaces personalizados", que encontraréis en la raíz de español, vuestros enlaces del pie personalizados."""
        links_string_en = u"""Customize your links footer on page "custom links"."""

        # Create default custom contact form info objects
        if not getattr(portal_en, 'customizedlinks', False):
            customizedlinks = self.create_content(portal_en, 'Document', 'customizedlinks', title='customizedlinks', publish=False)
            customizedlinks.title = u'Custom links'
            customizedlinks.text = RichTextValue(links_string_ca, 'text/html', 'text/x-html-safe')
        if not getattr(portal_es, 'enlacespersonalizados', False):
            enlacespersonalizados = self.create_content(portal_es, 'Document', 'enlacespersonalizados', title='enlacespersonalizados', publish=False)
            enlacespersonalizados.title = u'Enlaces personalizados'
            enlacespersonalizados.text = RichTextValue(links_string_es, 'text/html', 'text/x-html-safe')
        if not getattr(portal_ca, 'enllacospersonalitzats', False):
            enllacospersonalitzats = self.create_content(portal_ca, 'Document', 'enllacospersonalitzats', title='enllacospersonalitzats', publish=False)
            enllacospersonalitzats.title = u'Enllaços personalitzats'
            enllacospersonalitzats.text = RichTextValue(links_string_en, 'text/html', 'text/x-html-safe')

        customizedlinks = portal_en['customizedlinks']
        enlacespersonalizados = portal_es['enlacespersonalizados']
        enllacospersonalitzats = portal_ca['enllacospersonalitzats']

        self.link_translations([(enllacospersonalitzats, 'ca'), (enlacespersonalizados, 'es'), (customizedlinks, 'en')])

        customizedlinks.exclude_from_nav = True
        enlacespersonalizados.exclude_from_nav = True
        enllacospersonalitzats.exclude_from_nav = True

        alsoProvides(portal_ca, IProtectedContent)
        alsoProvides(portal_en, IProtectedContent)
        alsoProvides(portal_es, IProtectedContent)

        alsoProvides(benvingut, IProtectedContent)
        alsoProvides(bienvenido, IProtectedContent)
        alsoProvides(welcome, IProtectedContent)

        if getattr(portal_ca, 'noticies', False):
            noticies = portal_ca['noticies']
            alsoProvides(noticies, IProtectedContent)

            if getattr(noticies, 'aggregator', False):
                alsoProvides(noticies['aggregator'], IProtectedContent)

        if getattr(portal_es, 'noticias', False):
            noticias = portal_es['noticias']
            alsoProvides(noticias, IProtectedContent)

            if getattr(noticias, 'aggregator', False):
                alsoProvides(noticias['aggregator'], IProtectedContent)

        if getattr(portal_en, 'news', False):
            news = portal_en['news']
            alsoProvides(news, IProtectedContent)

            if getattr(news, 'aggregator', False):
                alsoProvides(news['aggregator'], IProtectedContent)

        if getattr(portal_ca, 'esdeveniments', False):
            esdeveniments = portal_ca['esdeveniments']
            alsoProvides(esdeveniments, IProtectedContent)

            if getattr(esdeveniments, 'aggregator', False):
                alsoProvides(esdeveniments['aggregator'], IProtectedContent)

        if getattr(portal_es, 'eventos', False):
            eventos = portal_es['eventos']
            alsoProvides(eventos, IProtectedContent)

            if getattr(eventos, 'aggregator', False):
                alsoProvides(eventos['aggregator'], IProtectedContent)

        if getattr(portal_en, 'events', False):
            events = portal_en['events']
            alsoProvides(events, IProtectedContent)

            if getattr(events, 'aggregator', False):
                alsoProvides(events['aggregator'], IProtectedContent)

        if getattr(portal_ca, 'banners-ca', False):
            alsoProvides(portal_ca['banners-ca'], IProtectedContent)

        if getattr(portal_es, 'banners-en', False):
            alsoProvides(portal_es['banners-en'], IProtectedContent)

        if getattr(portal_en, 'banners-es', False):
            alsoProvides(portal_en['banners-es'], IProtectedContent)

        if getattr(portal_ca, 'logosfooter-ca', False):
            alsoProvides(portal_ca['logosfooter-ca'], IProtectedContent)

        if getattr(portal_es, 'logosfooter-es', False):
            alsoProvides(portal_es['logosfooter-es'], IProtectedContent)

        if getattr(portal_en, 'logosfooter-en', False):
            alsoProvides(portal_en['logosfooter-en'], IProtectedContent)

        if getattr(portal_ca, 'contactepersonalitzat', False):
            alsoProvides(portal_ca['contactepersonalitzat'], IProtectedContent)

        if getattr(portal_es, 'contactopersonalizado', False):
            alsoProvides(portal_es['contactopersonalizado'], IProtectedContent)

        if getattr(portal_en, 'customizedcontact', False):
            alsoProvides(portal_en['customizedcontact'], IProtectedContent)

        alsoProvides(enllacospersonalitzats, IProtectedContent)
        alsoProvides(enlacespersonalizados, IProtectedContent)
        alsoProvides(customizedlinks, IProtectedContent)

        if getattr(portal_ca, 'shared', False):
            alsoProvides(portal_ca['shared'], IProtectedContent)

        if getattr(portal_es, 'shared', False):
            alsoProvides(portal_es['shared'], IProtectedContent)

        if getattr(portal_en, 'shared', False):
            alsoProvides(portal_en['shared'], IProtectedContent)

        if getattr(portal, 'plantilles', False):
            alsoProvides(portal['plantilles'], IProtectedContent)

    def createContent(self):
        """ Method that creates all the default content """
        portal = api.portal.get()
        portal_ca = portal['ca']
        portal_en = portal['en']
        portal_es = portal['es']

        # Let's configure mail
        mail = IMailSchema(portal)
        mail.smtp_host = u'localhost'
        if mail.email_from_address in ('noreply@upc.edu', 'no-reply@upcnet.es'):
            mail.email_from_name = "Administrador del Genweb"
            mail.email_from_address = "noreply@upc.edu"

        # Get rid of the original page
        if getattr(portal_en, 'front-page', False):
            api.content.delete(obj=portal['front-page'])

        # Hide 'Members' folder
        if getattr(portal, 'Members', False):
            api.content.delete(obj=portal['Members'])

        # Rename the original 'news' and 'events' folders for using it at the setup
        if getattr(portal, 'news', False):
            api.content.delete(obj=portal['news'])
            # api.content.rename(obj=portal['news'], new_id='news_setup')
        if getattr(portal, 'events', False):
            api.content.delete(obj=portal['events'])
            # api.content.rename(obj=portal['events'], new_id='events_setup')

        # Remove LFI Media folder
        if getattr(portal_ca, 'media', False):
            api.content.delete(obj=portal_ca['media'])
        if getattr(portal_es, 'media', False):
            api.content.delete(obj=portal_es['media'])
        if getattr(portal_en, 'media', False):
            api.content.delete(obj=portal_en['media'])

        # Setup portal news folder
        news = self.create_content(portal_en, 'Folder', 'news', title='News', description=u'Site news')
        noticias = self.create_content(portal_es, 'Folder', 'noticias', title='Noticias', description=u'Noticias del sitio')
        noticies = self.create_content(portal_ca, 'Folder', 'noticies', title='Notícies', description=u'Notícies del lloc')
        self.link_translations([(news, 'en'), (noticias, 'es'), (noticies, 'ca')])

        news.exclude_from_nav = True
        noticias.exclude_from_nav = True
        noticies.exclude_from_nav = True

        # Create the aggregator
        col_news = self.create_content(news, 'Collection', 'aggregator', title='aggregator', description=u'Site news')
        col_news.title = 'News'
        col_news.query = NEWS_QUERY
        col_news.sort_on = QUERY_SORT_ON

        col_news.reindexObject()

        col_noticias = self.create_content(noticias, 'Collection', 'aggregator', title='aggregator', description=u'Notícias del sitio')
        col_noticias.title = 'Noticias'
        col_noticias.query = NEWS_QUERY
        col_noticias.sort_on = QUERY_SORT_ON

        col_noticias.reindexObject()

        col_noticies = self.create_content(noticies, 'Collection', 'aggregator', title='aggregator', description=u'Notícies del lloc')
        col_noticies.title = 'Notícies'
        col_noticies.query = NEWS_QUERY
        col_noticies.sort_on = QUERY_SORT_ON

        col_noticies.reindexObject()

        # Set layout for news folders
        news.setDefaultPage('aggregator')
        noticias.setDefaultPage('aggregator')
        noticies.setDefaultPage('aggregator')

        self.link_translations([(col_news, 'en'), (col_noticias, 'es'), (col_noticies, 'ca')])

        self.constrain_content_types(news, ('News Item', 'Folder', 'Image', 'Link'))
        self.constrain_content_types(noticias, ('News Item', 'Folder', 'Image', 'Link'))
        self.constrain_content_types(noticies, ('News Item', 'Folder', 'Image', 'Link'))

        # Setup portal events folder
        events = self.create_content(portal_en, 'Folder', 'events', title='Events', description=u'Site events')
        eventos = self.create_content(portal_es, 'Folder', 'eventos', title='Eventos', description=u'Eventos del sitio')
        esdeveniments = self.create_content(portal_ca, 'Folder', 'esdeveniments', title='Esdeveniments', description=u'Esdeveniments del lloc')
        self.link_translations([(events, 'en'), (eventos, 'es'), (esdeveniments, 'ca')])

        events.exclude_from_nav = True
        eventos.exclude_from_nav = True
        esdeveniments.exclude_from_nav = True

        # Create the aggregator
        # original_col_events = original_events['aggregator']
        col_events = self.create_content(events, 'Collection', 'aggregator', title='aggregator', description=u'Site events')
        col_events.title = 'Events'
        col_events.query = EVENT_QUERY
        col_events.sort_on = QUERY_SORT_ON

        col_events.reindexObject()

        col_eventos = self.create_content(eventos, 'Collection', 'aggregator', title='aggregator', description=u'Eventos del sitio')
        col_eventos.title = 'Eventos'
        col_eventos.query = EVENT_QUERY
        col_eventos.sort_on = QUERY_SORT_ON

        col_eventos.reindexObject()

        col_esdeveniments = self.create_content(esdeveniments, 'Collection', 'aggregator', title='aggregator', description=u'Esdeveniments del lloc')
        col_esdeveniments.title = 'Esdeveniments'
        col_esdeveniments.query = EVENT_QUERY
        col_esdeveniments.sort_on = QUERY_SORT_ON

        col_esdeveniments.reindexObject()

        # Set layout for news folders
        events.setDefaultPage('aggregator')
        eventos.setDefaultPage('aggregator')
        esdeveniments.setDefaultPage('aggregator')

        self.link_translations([(col_events, 'en'), (col_eventos, 'es'), (col_esdeveniments, 'ca')])

        self.constrain_content_types(events, ('Event', 'Folder', 'Image'))
        self.constrain_content_types(eventos, ('Event', 'Folder', 'Image'))
        self.constrain_content_types(esdeveniments, ('Event', 'Folder', 'Image'))

        # Create banners folders
        banners_en = self.create_content(portal_en, 'BannerContainer', 'banners-en', title='banners-en', description=u'English Banners')
        banners_en.title = 'Banners'
        banners_es = self.create_content(portal_es, 'BannerContainer', 'banners-es', title='banners-es', description=u'Banners en Español')
        banners_es.title = 'Banners'
        banners_ca = self.create_content(portal_ca, 'BannerContainer', 'banners-ca', title='banners-ca', description=u'Banners en Català')
        banners_ca.title = 'Banners'
        self.link_translations([(banners_ca, 'ca'), (banners_es, 'es'), (banners_en, 'en')])

        banners_en.exclude_from_nav = True
        banners_es.exclude_from_nav = True
        banners_ca.exclude_from_nav = True

        banners_en.reindexObject()
        banners_es.reindexObject()
        banners_ca.reindexObject()

        # Create logosfooter folders
        logosfooter_en = self.create_content(portal_en, 'Logos_Container', 'logosfooter-en', title='logosfooter-en', description=u'English footer logos')
        logosfooter_en.title = 'Footer Logos'
        logosfooter_es = self.create_content(portal_es, 'Logos_Container', 'logosfooter-es', title='logosfooter-es', description=u'Logos en español del pie de página')
        logosfooter_es.title = 'Logos pie'
        logosfooter_ca = self.create_content(portal_ca, 'Logos_Container', 'logosfooter-ca', title='logosfooter-ca', description=u'Logos en català del peu de pàgina')
        logosfooter_ca.title = 'Logos peu'
        self.link_translations([(logosfooter_ca, 'ca'), (logosfooter_es, 'es'), (logosfooter_en, 'en')])

        logosfooter_en.exclude_from_nav = True
        logosfooter_es.exclude_from_nav = True
        logosfooter_ca.exclude_from_nav = True

        logosfooter_en.reindexObject()
        logosfooter_es.reindexObject()
        logosfooter_ca.reindexObject()

        # welcome pages
        welcome_string_ca = u"""<div class="box">
            <div>
            <div class="destacatBandejat">
            <p class="xxl" style="text-align: center; ">Contingut de la pàgina "Benvingut"</p>
            </div>
            <p> </p>
            </div>
            <div>Personalitzeu aquest contingut a la pàgina "Benvingut" que trobareu a l'arrel del vostre web.</div>
            <div>
            <ul class="list list-highlighted">
            <li><a class="external-link" href="http://genweb.upc.edu/ca/documentacio" target="_blank" title="">Documentació Genweb v4</a></li>
            </ul>
            </div>
            <p> </p>
            <p> </p>
            </div>
            """

        welcome_string_es = u"""<div class="box">
            <div>
            <div class="destacatBandejat">
            <p class="xxl" style="text-align: center; "><span>Contenido de la página "Bienvenido"</span></p>
            </div>
            <p> </p>
            </div>
            <div>Personalizad este contenido en la página "Bienvenido" que encontraréis en la raíz del árbol de navegación en castellano.</div>
            <p> </p>
            <p> </p>
            </div> """

        welcome_string_en = u"""<div class="box">
            <div>
            <div class="destacatBandejat">
            <p class="xxl" style="text-align: center; "><span>"Welcome" page content</span></p>
            </div>
            <p> </p>
            <p>Update on page "Welcome" the content you want in your website home page.</p>
            </div>
            <p> </p>
            <p> </p>
            </div> """

        if not getattr(portal_en, 'welcome', False):
            welcome = self.create_content(portal_en, 'Document', 'welcome', title='Welcome')
            welcome.text = RichTextValue(welcome_string_en, 'text/html', 'text/x-html-safe')
        if not getattr(portal_es, 'bienvenido', False):
            bienvenido = self.create_content(portal_es, 'Document', 'bienvenido', title='Bienvenido')
            bienvenido.text = RichTextValue(welcome_string_es, 'text/html', 'text/x-html-safe')
        if not getattr(portal_ca, 'benvingut', False):
            benvingut = self.create_content(portal_ca, 'Document', 'benvingut', title='Benvingut')
            benvingut.text = RichTextValue(welcome_string_ca, 'text/html', 'text/x-html-safe')

        welcome = portal_en['welcome']
        bienvenido = portal_es['bienvenido']
        benvingut = portal_ca['benvingut']

        self.link_translations([(benvingut, 'ca'), (bienvenido, 'es'), (welcome, 'en')])

        # Mark all homes with IHomePage marker interface
        alsoProvides(portal_ca, IHomePage)
        alsoProvides(portal_en, IHomePage)
        alsoProvides(portal_es, IHomePage)

        alsoProvides(benvingut, IHomePage)
        alsoProvides(bienvenido, IHomePage)
        alsoProvides(welcome, IHomePage)

        benvingut.exclude_from_nav = True
        bienvenido.exclude_from_nav = True
        welcome.exclude_from_nav = True

        # Reindex them to update object_provides index
        benvingut.reindexObject()
        bienvenido.reindexObject()
        welcome.reindexObject()

        # Set the default pages to the homepage view
        portal_en.setLayout('homepage')
        portal_es.setLayout('homepage')
        portal_ca.setLayout('homepage')

        contact_string_ca = u"""Editeu a la pàgina "Contacte personalitzat", que trobareu a l’arrel de català, les vostres dades personalitzades de contacte."""
        contact_string_es = u"""Editad en la página "Contacto personalizado", que encontraréis en la raíz de español, vuestros datos personalizados de contacto."""
        contact_string_en = u"""Customize your contact details on page "custom contact"."""

        # Create default custom contact form info objects
        if not getattr(portal_en, 'customizedcontact', False):
            customizedcontact = self.create_content(portal_en, 'Document', 'customizedcontact', title='customizedcontact', publish=False)
            customizedcontact.title = u'Custom contact'
            customizedcontact.text = RichTextValue(contact_string_en, 'text/html', 'text/x-html-safe')
        if not getattr(portal_es, 'contactopersonalizado', False):
            contactopersonalizado = self.create_content(portal_es, 'Document', 'contactopersonalizado', title='contactopersonalizado', publish=False)
            contactopersonalizado.title = u'Contacto personalizado'
            contactopersonalizado.text = RichTextValue(contact_string_es, 'text/html', 'text/x-html-safe')
        if not getattr(portal_ca, 'contactepersonalitzat', False):
            contactepersonalitzat = self.create_content(portal_ca, 'Document', 'contactepersonalitzat', title='contactepersonalitzat', publish=False)
            contactepersonalitzat.title = u'Contacte personalitzat'
            contactepersonalitzat.text = RichTextValue(contact_string_ca, 'text/html', 'text/x-html-safe')

        customizedcontact = portal_en['customizedcontact']
        contactopersonalizado = portal_es['contactopersonalizado']
        contactepersonalitzat = portal_ca['contactepersonalitzat']

        self.link_translations([(contactepersonalitzat, 'ca'), (contactopersonalizado, 'es'), (customizedcontact, 'en')])

        customizedcontact.exclude_from_nav = True
        contactopersonalizado.exclude_from_nav = True
        contactepersonalitzat.exclude_from_nav = True

        links_string_ca = u"""Editeu a la pàgina "Enllaços personalitzats", que trobareu a l’arrel de català, els vostres enllaços del peu personalitzats."""
        links_string_es = u"""Editad en la página "Enlaces personalizados", que encontraréis en la raíz de español, vuestros enlaces del pie personalizados."""
        links_string_en = u"""Customize your links footer on page "custom links"."""

        # Create default custom contact form info objects
        if not getattr(portal_en, 'customizedlinks', False):
            customizedlinks = self.create_content(portal_en, 'Document', 'customizedlinks', title='customizedlinks', publish=False)
            customizedlinks.title = u'Custom links'
            customizedlinks.text = RichTextValue(links_string_ca, 'text/html', 'text/x-html-safe')
        if not getattr(portal_es, 'enlacespersonalizados', False):
            enlacespersonalizados = self.create_content(portal_es, 'Document', 'enlacespersonalizados', title='enlacespersonalizados', publish=False)
            enlacespersonalizados.title = u'Enlaces personalizados'
            enlacespersonalizados.text = RichTextValue(links_string_es, 'text/html', 'text/x-html-safe')
        if not getattr(portal_ca, 'enllacospersonalitzats', False):
            enllacospersonalitzats = self.create_content(portal_ca, 'Document', 'enllacospersonalitzats', title='enllacospersonalitzats', publish=False)
            enllacospersonalitzats.title = u'Enllaços personalitzats'
            enllacospersonalitzats.text = RichTextValue(links_string_en, 'text/html', 'text/x-html-safe')

        customizedlinks = portal_en['customizedlinks']
        enlacespersonalizados = portal_es['enlacespersonalizados']
        enllacospersonalitzats = portal_ca['enllacospersonalitzats']

        self.link_translations([(enllacospersonalitzats, 'ca'), (enlacespersonalizados, 'es'), (customizedlinks, 'en')])

        customizedlinks.exclude_from_nav = True
        enlacespersonalizados.exclude_from_nav = True
        enllacospersonalitzats.exclude_from_nav = True

        # Templates TinyMCE
        plantilles = self.create_content(portal, 'Folder', 'plantilles', title='Plantilles', description='En aquesta carpeta podeu posar les plantilles per ser usades a l\'editor.')
        plantilles.exclude_from_nav = True
        api.content.transition(obj=plantilles, transition='retracttointranet')
        api.content.transition(obj=plantilles, transition='publish')
        plantilles.reindexObject()

        # Create the shared folders for files and images
        compartits = self.create_content(portal_ca, 'LIF', 'shared', title='shared', description='En aquesta carpeta podeu posar els fitxers i imatges que siguin compartits per tots o alguns idiomes.')
        compartits.title = 'Fitxers compartits'
        shared = self.create_content(portal_en, 'LIF', 'shared', title='shared', description='En aquesta carpeta podeu posar els fitxers i imatges que siguin compartits per tots o alguns idiomes.')
        shared.title = 'Shared files'
        compartidos = self.create_content(portal_es, 'LIF', 'shared', title='shared', description='En aquesta carpeta podeu posar els fitxers i imatges que siguin compartits per tots o alguns idiomes.')
        compartidos.title = 'Ficheros compartidos'
        self.constrain_content_types(compartits, ('File', 'Folder', 'Image'))
        self.constrain_content_types(shared, ('File', 'Folder', 'Image'))
        self.constrain_content_types(compartidos, ('File', 'Folder', 'Image'))

        compartits.exclude_from_nav = True
        shared.exclude_from_nav = True
        compartidos.exclude_from_nav = True

        compartits.reindexObject()
        shared.reindexObject()
        compartidos.reindexObject()

        # Mark all protected content with the protected marker interface
        alsoProvides(portal_ca, IProtectedContent)
        alsoProvides(portal_en, IProtectedContent)
        alsoProvides(portal_es, IProtectedContent)

        alsoProvides(benvingut, IProtectedContent)
        alsoProvides(bienvenido, IProtectedContent)
        alsoProvides(welcome, IProtectedContent)

        alsoProvides(noticies, IProtectedContent)
        alsoProvides(noticias, IProtectedContent)
        alsoProvides(news, IProtectedContent)

        alsoProvides(col_noticies, IProtectedContent)
        alsoProvides(col_noticias, IProtectedContent)
        alsoProvides(col_news, IProtectedContent)

        alsoProvides(esdeveniments, IProtectedContent)
        alsoProvides(eventos, IProtectedContent)
        alsoProvides(events, IProtectedContent)

        alsoProvides(col_esdeveniments, IProtectedContent)
        alsoProvides(col_eventos, IProtectedContent)
        alsoProvides(col_events, IProtectedContent)

        alsoProvides(banners_ca, IProtectedContent)
        alsoProvides(banners_en, IProtectedContent)
        alsoProvides(banners_es, IProtectedContent)

        alsoProvides(logosfooter_ca, IProtectedContent)
        alsoProvides(logosfooter_es, IProtectedContent)
        alsoProvides(logosfooter_en, IProtectedContent)

        alsoProvides(customizedcontact, IProtectedContent)
        alsoProvides(contactopersonalizado, IProtectedContent)
        alsoProvides(contactepersonalitzat, IProtectedContent)

        alsoProvides(customizedlinks, IProtectedContent)
        alsoProvides(enlacespersonalizados, IProtectedContent)
        alsoProvides(enllacospersonalitzats, IProtectedContent)

        alsoProvides(shared, IProtectedContent)
        alsoProvides(compartidos, IProtectedContent)
        alsoProvides(compartits, IProtectedContent)

        alsoProvides(plantilles, IProtectedContent)

        # Mark also the special folders
        alsoProvides(noticies, INewsFolder)
        alsoProvides(noticias, INewsFolder)
        alsoProvides(news, INewsFolder)

        alsoProvides(esdeveniments, IEventFolder)
        alsoProvides(eventos, IEventFolder)
        alsoProvides(events, IEventFolder)

        # transaction.commit()
        pc = api.portal.get_tool('portal_catalog')
        pc.clearFindAndRebuild()

        # Put navigation portlets in place
        target_manager_en = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal_en)
        target_manager_en_assignments = getMultiAdapter((portal_en, target_manager_en), IPortletAssignmentMapping)
        target_manager_es = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal_es)
        target_manager_es_assignments = getMultiAdapter((portal_es, target_manager_es), IPortletAssignmentMapping)
        target_manager_ca = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal_ca)
        target_manager_ca_assignments = getMultiAdapter((portal_ca, target_manager_ca), IPortletAssignmentMapping)

        from plone.app.portlets.portlets.navigation import Assignment as navigationAssignment
        if 'navigation' not in target_manager_en_assignments:
            target_manager_en_assignments['navigation'] = navigationAssignment(topLevel=2, bottomLevel=0, no_icons=True, no_thumbs=True)
        if 'navigation' not in target_manager_es_assignments:
            target_manager_es_assignments['navigation'] = navigationAssignment(topLevel=2, bottomLevel=0, no_icons=True, no_thumbs=True)
        if 'navigation' not in target_manager_ca_assignments:
            target_manager_ca_assignments['navigation'] = navigationAssignment(topLevel=2, bottomLevel=0, no_icons=True, no_thumbs=True)

        # Blacklist the left column on:
        # portal_ca['noticies'] and portal_ca['esdeveniments'],
        # portal_es['noticias'] and portal_es['eventos'],
        # portal_en['news'] and portal_en['events']
        left_manager = queryUtility(IPortletManager, name=u'plone.leftcolumn')
        blacklist_ca = getMultiAdapter((portal_ca['noticies'], left_manager), ILocalPortletAssignmentManager)
        blacklist_ca.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_ca = getMultiAdapter((portal_ca['esdeveniments'], left_manager), ILocalPortletAssignmentManager)
        blacklist_ca.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_es = getMultiAdapter((portal_es['noticias'], left_manager), ILocalPortletAssignmentManager)
        blacklist_es.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_es = getMultiAdapter((portal_es['eventos'], left_manager), ILocalPortletAssignmentManager)
        blacklist_es.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_en = getMultiAdapter((portal_en['news'], left_manager), ILocalPortletAssignmentManager)
        blacklist_en.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_en = getMultiAdapter((portal_en['events'], left_manager), ILocalPortletAssignmentManager)
        blacklist_en.setBlacklistStatus(CONTEXT_CATEGORY, True)

        # Delete default Navigation portlet on root
        target_manager_root = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal)
        target_manager_root_assignments = getMultiAdapter((portal, target_manager_root), IPortletAssignmentMapping)
        if 'navigation' in target_manager_root_assignments:
            del target_manager_root_assignments['navigation']
        return True

    def createExampleContent(self):
        portal = api.portal.get()

        folder_ca = portal['ca']
        pagina_mostra_ca = self.create_content(folder_ca, 'Document', 'pagina-principal-mostra', title='Pàgina principal mostra', exclude_from_nav=True)

        pagebody_sample = """
<div>
<div class="box">
<h2 class="align-center"><span class="fa fa-quote-left"></span> <strong>Genweb 6</strong>, el nou disseny per al teu genweb <span class="fa fa-quote-right"></span></h2>
</div>
</div>
<p> </p>
<p> </p>
<div class="row">
<div class="col-md-6"><a class="link-bannerblau external-link" href="https://genweb.upc.edu/ca" target="_blank"><span class="btntitolblau">Genweb 6</span><br /><span class="btnsubtitolblau">El generador de webs UPC</span></a>
<p> </p>
<a class="link-bannerdanger external-link" href="https://genweb.upc.edu/ca/genweb-4/portfolio" target="_blank"><span class="btntitoldanger">Exemples de Genweb. Portfolio</span><br /><span class="btnsubtitoldanger">Per inspirar-vos</span></a></div>
<div class="col-md-6"><a class="link-bannersuccess external-link" href="https://genweb.upc.edu/ca/documentacio" target="_blank"> <span class="btntitolsuccess">Documentació Genweb</span><br /><span class="btnsubtitolsuccess">Tot el que necessites saber</span></a>
<p> </p>
<a class="link-bannerwarning external-link" href="https://youtube.com/playlist?list=PLf-YeP3BONET2sMB_ZcZpe7I0NUVtksBz" target="_blank"><span class="btntitolwarning">Videotutorials Genweb</span><br />Canal de l'Àrea TIC</a></div>
</div>"""

        pagina_mostra_ca.text = RichTextValue(pagebody_sample, 'text/html', 'text/x-html-safe')
        pagina_mostra_ca.reindexObject()

        egglocation = pkg_resources.get_distribution('genweb6.theme').location
        newsimg_sample = open('{}/genweb6/theme/theme/img/sample/news_sample_2.jpg'.format(egglocation), 'rb').read()

        noticies = portal['ca']['noticies']
        for i in range(1, 4):
            noticia_mostra_ca = self.create_content(noticies,
                                                    'News Item',
                                                    'noticia-de-mostra-' + str(i),
                                                    title='Notícia de mostra ' + str(i),
                                                    image=NamedBlobImage(data=newsimg_sample,
                                                                         filename=u'news_sample.jpg',
                                                                         contentType=u'image/jpeg'),
                                                    description='Descripció notícia')

            noticia_mostra_ca.text = RichTextValue("Contingut notícia", 'text/html', 'text/x-html-safe')
            noticia_mostra_ca.reindexObject()

        esdeveniments = portal['ca']['esdeveniments']
        now = localized_now().replace(minute=0, second=0, microsecond=0)
        far = now + timedelta(days=14600)
        for i in range(1, 5):
            event_sample_ca = self.create_content(esdeveniments,
                                                  'Event',
                                                  'esdeveniment-de-mostra-' + str(i),
                                                  title='Esdeveniment de mostra ' + str(i))

            event_sample_ca.text = RichTextValue("Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus.", 'text/html', 'text/x-html-safe')
            event_sample_ca.location = "Lloc de l'esdeveniment"
            event_sample_ca.start = now
            event_sample_ca.end = far
            event_sample_ca.timezone = 'Europe/Madrid'
            event_sample_ca.contact_email = 'adreca@noreply.com'
            event_sample_ca.contact_name = 'Responsable esdeveniment'
            event_sample_ca.reindexObject()

        portletManager = getUtility(IPortletManager, 'genweb.portlets.HomePortletManager3')
        spanstorage = getMultiAdapter((portal['ca']['benvingut'], portletManager), ISpanStorage)
        spanstorage.span = '12'

        managerAssignments = getMultiAdapter((portal['ca']['benvingut'], portletManager), IPortletAssignmentMapping)

        from genweb6.core.portlets.new_existing_content.new_existing_content import Assignment as newExistingContentAssignment
        if 'pagina_principal' not in managerAssignments:
            managerAssignments['pagina_principal'] = newExistingContentAssignment(
                ptitle='Pàgina principal',
                show_title=False,
                hide_footer=True,
                content_or_url='INTERN',
                external_url='',
                own_content=create_relation('/'.join(pagina_mostra_ca.getPhysicalPath())))

        from genweb6.core.portlets.fullnews.fullnews import Assignment as fullnewsAssignment
        if 'noticies' not in managerAssignments:
            managerAssignments['noticies'] = fullnewsAssignment(
                view_type='id_full_3cols')

        from genweb6.core.portlets.grid_events.grid_events import Assignment as gridEventsAssignment
        if 'esdeveniments' not in managerAssignments:
            managerAssignments['esdeveniments'] = gridEventsAssignment()

    def create_content(self, container, portal_type, id, publish=True, **kwargs):
        if not getattr(container, id, False):
            obj = createContentInContainer(container, portal_type, checkConstraints=False, **kwargs)
            if publish:
                self.publish_content(obj)
        return getattr(container, id)

    def link_translations(self, items):
        """
        Links the translations with the declared items with the form:
        [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
        is the 'canonical' (in PAM there is no such thing).
        """
        # Grab the first item object and get its canonical handler
        canonical = ITranslationManager(items[0][0])

        for obj, language in items:
            if not canonical.has_translation(language):
                canonical.register_translation(language, obj)

    def constrain_content_types(self, container, content_types):
        # Set on them the allowable content types
        behavior = ISelectableConstrainTypes(container)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(content_types)
        behavior.setImmediatelyAddableTypes(content_types)

    def clone_collection_settings(self, origin, target):
        if getattr(origin, 'query', False):
            target.query = origin.query
        if getattr(origin, 'sort_on', False):
            target.sort_on = origin.sort_on
        if getattr(origin, 'sort_reversed', False):
            target.sort_reversed = origin.sort_reversed
        if getattr(origin, 'limit', False):
            target.limit = origin.limit
        if getattr(origin, 'item_count', False):
            target.item_count = origin.item_count
        if getattr(origin, 'customViewFields', False):
            target.customViewFields = origin.customViewFields

    def getObjectStatus(self, context):
        pw = getToolByName(context, "portal_workflow")
        object_workflow = pw.getWorkflowsFor(context)[0].id
        object_status = pw.getStatusOf(object_workflow, context)
        return object_status

    def publish_content(self, context):
        """
        Make the content visible either in both possible genweb.simple and
        genweb.review workflows.
        """
        pw = getToolByName(context, "portal_workflow")
        object_workflow = pw.getWorkflowsFor(context)[0].id
        object_status = pw.getStatusOf(object_workflow, context)
        if object_status:
            api.content.transition(obj=context, transition={'genweb_simple': 'publish', 'genweb_review': 'publicaalaintranet'}[object_workflow])

    def setGenwebProperties(self):
        """ Set default configuration in genweb properties """
        gwheader = utils.genwebHeaderConfig()
        gwheader.languages_link_to_root = True

        portal = getToolByName(self, 'portal_url').getPortalObject()
        site_props = portal.portal_properties.site_properties
        site_props.exposeDCMetaTags = True
        navtree_props = portal.portal_properties.navtree_properties
        navtree_props.sitemapDepth = 4


def get_portlet_assignments(context, name):
    portlet_manager = queryUtility(
        IPortletManager,
        name=name,
        context=context)
    return getMultiAdapter(
        (context, portlet_manager), IPortletAssignmentMapping)
