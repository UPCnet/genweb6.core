# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_inner

from plone import api
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from plone.app.layout.viewlets.common import PersonalBarViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet
from plone.app.multilingual.browser.selector import addQuery
from plone.app.multilingual.browser.selector import getPostPath
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import NOTG
from plone.formwidget.namedfile.converter import b64decode_file
from plone.memoize.view import memoize_contextless
from plone.memoize.view import memoize
from plone.namedfile.file import NamedFile
from plone.uuid.interfaces import IUUID
from zope.component import queryAdapter

from genweb6.core import _
from genweb6.core import utils
from genweb6.core.interfaces import IHomePage
from genweb6.core.utils import genwebCintilloConfig
from genweb6.core.utils import genwebFooterConfig
from genweb6.core.utils import genwebHeaderConfig
from genweb6.core.utils import genwebResourcesConfig
from genweb6.core.utils import toLocalizedTime


class viewletBase(ViewletBase):

    @memoize_contextless
    def root_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return api.portal.get()

    def pref_lang(self):
        lt = api.portal.get_tool(name='portal_languages')
        lang = lt.getPreferredLanguage()
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'
        return lang

    def isAnonymous(self):
        return api.user.is_anonymous()

    def current_url(self):
        return self.context.absolute_url()


class GWGlobalSectionsViewlet(GlobalSectionsViewlet):
    # Customizamos el GlobalSectionsViewlet para añadirle a los enlaces externos target="_blank"

    # Añadimos el target al enlace y una clase para indicar que estamos en esa posición
    _item_markup_template = (
        '<li class="{id}{has_sub_class}{current} nav-item">'
        '<a href="{url}" target="{target}" class="state-{review_state} nav-link"{aria_haspopup}>{title}</a>{opener}'
        "{sub}"
        "</li>")

    # Añadimos si es un enlace externo en caso de tenerlo habilitado en el tipo de contenido y no estas validado
    # open_link_in_new_window
    #
    # A parte comprobamos si estamos posicionados en la tab actual
    def customize_entry(self, entry, brain):
        entry.update({"external_link": bool(
            getattr(brain, "open_link_in_new_window", False)) and api.user.is_anonymous()})
        entry.update({"current": entry['path']
                     in "/".join(self.context.getPhysicalPath())})

    def customize_tab(self, entry, tab):
        lang = self.context.language
        if not lang:
            lang = self.context.getPhysicalPath()[
                len(api.portal.get().getPhysicalPath())]

        path = '/' + api.portal.get().id + '/' + lang + '/' + tab['id']
        brain = api.content.get(path=path)
        entry.update({"external_link": bool(
            getattr(brain, "open_link_in_new_window", False)) and api.user.is_anonymous()})
        entry.update({"current": path in "/".join(self.context.getPhysicalPath())})

    # Añadimos target y current al dict
    def render_item(self, item, path):
        sub = self.build_tree(item["path"], first_run=False)
        if sub:
            item.update(
                {
                    "sub": sub,
                    "opener": self._opener_markup_template.format(**item),
                    "aria_haspopup": ' aria-haspopup="true"',
                    "has_sub_class": " has_subtree",
                    "current": " current" if item["current"] else "",
                    "target": "_blank" if item["external_link"] else "_self"
                }
            )
        else:
            item.update(
                {
                    "sub": sub,
                    "opener": "",
                    "aria_haspopup": "",
                    "has_sub_class": "",
                    "current": " current" if item["current"] else "",
                    "target": "_blank" if item["external_link"] else "_self"
                }
            )

        return self._item_markup_template.format(**item)


class cintilloViewlet(viewletBase):

    def render(self):
        cintillo_config = genwebCintilloConfig()
        if cintillo_config.active:
            return super(viewletBase, self).render()
        else:
            return ""

    def info_cintillo(self):
        cintillo_config = genwebCintilloConfig()
        lang = self.pref_lang()

        return {"style": "background-color: " + cintillo_config.background_color +
                         "; color: " + cintillo_config.font_color + ";",
                "icon": cintillo_config.icon,
                "title": getattr(cintillo_config, "title_" + lang, ""),
                "text": getattr(cintillo_config, "text_" + lang, "")}


class headerViewlet(
        viewletBase, SearchBoxViewlet, GWGlobalSectionsViewlet, PersonalBarViewlet):

    _opener_markup_template = (
        '<input type="checkbox" class="opener" />'
        '<label for="navitem-{uid}" role="button" aria-label="{title}"></label>'
    )

    @memoize
    def getClass(self):
        header_config = genwebHeaderConfig()

        default_class = 'd-flex align-items-center ' + \
                        getattr(header_config, 'theme', 'light-to-dark-theme')

        return default_class

    @memoize
    def getLogosHeader(self):
        header_config = genwebHeaderConfig()
        portal_url = self.root_url()

        if getattr(header_config, 'logo', False):
            filename, data = b64decode_file(header_config.logo)
            logo = '{}/@@gw-logo'.format(portal_url)
        else:
            logo = '%s/++theme++genweb6.theme/img/logo.png' % portal_url

        if getattr(header_config, 'logo_responsive', False):
            filename, data = b64decode_file(header_config.logo_responsive)
            logo_responsive = '{}/@@gw-logo-responsive'.format(portal_url)
        else:
            logo_responsive = logo

        if getattr(header_config, 'secundary_logo', False):
            filename, data = b64decode_file(header_config.secundary_logo)
            secundary_logo = '{}/@@gw-secundary-logo'.format(portal_url)
        else:
            secundary_logo = None

        if getattr(header_config, 'secundary_logo_responsive', False):
            filename, data = b64decode_file(header_config.secundary_logo_responsive)
            secundary_logo_responsive = '{}/@@gw-secundary-logo-responsive'.format(
                portal_url)
        else:
            secundary_logo_responsive = secundary_logo

        return {"logo": logo,
                "logo_responsive": logo_responsive,
                "logo_alt": getattr(header_config, 'logo_alt', ""),
                "logo_url": getattr(header_config, 'logo_url', None),
                "logo_target": "_blank" if header_config.logo_external_url else "_self",
                "logo_responsive": logo_responsive,
                "secundary_logo": secundary_logo,
                "secundary_logo_responsive": secundary_logo_responsive,
                "secundary_logo_alt": getattr(header_config, 'secundary_logo_alt', ""),
                "secundary_logo_url": getattr(header_config, 'secundary_logo_url', None),
                "secundary_logo_target": "_blank" if header_config.secundary_logo_external_url else "_self"}

    @memoize
    def languages(self):
        lt = api.portal.get_tool(name='portal_languages')
        if lt is None:
            return []

        bound = lt.getLanguageBindings(self.request)
        current = bound[0]

        def merge(lang, info):
            info["code"] = lang
            info["selected"] = lang == current
            return info

        header_config = genwebHeaderConfig()

        languages = [
            merge(lang, info)
            for (lang, info) in lt.getAvailableLanguageInformation().items()
            if info["selected"] and lang in header_config.idiomes_publicats
        ]

        supported_langs = lt.getSupportedLanguages()

        def index(info):
            return len(supported_langs)

        lang_selected = None
        lang_others = []

        redirect_to_root = header_config.languages_link_to_root
        if not redirect_to_root:
            translation_group = queryAdapter(self.context, ITG)
            if translation_group is None:
                translation_group = NOTG
        else:
            translation_group = NOTG

        portal_url = api.portal.get().absolute_url()
        for lang in languages:
            if redirect_to_root:
                url = self.root_url(
                ) + '/' + lang['code'] + '?set_language=' + lang['code']
            else:
                query_extras = {'set_language': lang['code']}
                post_path = getPostPath(self.context, self.request)
                if post_path:
                    query_extras['post_path'] = post_path

                url = addQuery(
                    self.request,
                    portal_url +
                    '/@@multilingual-selector/%s/%s' % (
                        translation_group,
                        lang['code']
                    ),
                    **query_extras
                )

            lang.update({'url': url})

            if lang['selected']:
                lang_selected = lang
            else:
                lang_others.append(lang)

        len_others = len(lang_others)

        result = {'selected': lang_selected, 'others': sorted(
            lang_others, key=index),
            'has_selector': len_others > 0 and self.context.portal_type !=
            'Plone Site'}

        return result

    # Funcion para añadir a la busqueda un path o literal especifico, para customizarlo en algún paquete de cliente
    def custom_search(self):
        return {'literal': None,
                'path': None}


class heroViewlet(viewletBase):

    def isHomepage(self):
        if IHomePage.providedBy(self.context):

            # Homepage normal
            if ILanguageRootFolder.providedBy(self.context) and self.request.steps[-1] == 'homepage':
                return True

            # Homepage con tiles
            parent = self.context.aq_parent
            if ILanguageRootFolder.providedBy(parent) and hasattr(parent, 'default_page') and parent.default_page == self.context.id and self.request.steps[-1] == 'layout_view':
                return True

        return False

    def getClass(self):
        header_config = genwebHeaderConfig()
        theme = getattr(header_config, 'theme', 'light-to-dark-theme') + ' '

        if self.isHomepage():
            return theme + getattr(header_config, 'main_hero_style', 'image-hero')

        return theme + getattr(header_config, 'content_hero_style', 'image-hero')

    def getHeroHeader(self):
        header_config = genwebHeaderConfig()
        portal_url = self.root_url()

        if self.isHomepage():
            hero = getattr(header_config, 'main_hero_style', 'image-hero')
        else:
            hero = getattr(header_config, 'content_hero_style', 'image-hero')

        if 'pretty-image-hero' in hero:
            if getattr(header_config, 'full_hero_image', False):
                img_url = '{}/@@gw-full-hero'.format(portal_url)
            else:
                return False
        else:
            if getattr(header_config, 'hero_image', False):
                img_url = '{}/@@gw-hero'.format(portal_url)
            else:
                return False

        return img_url


class logosFooterViewlet(viewletBase):

    @memoize
    def getLogosFooter(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        lang = utils.pref_lang()
        return catalog.searchResults(portal_type='Logos_Footer',
                                     review_state=['published', 'intranet'],
                                     Language=lang,
                                     sort_on='getObjPositionInParent')

    def getAltAndTitle(self, altortitle):
        """ Funcio que extreu idioma actiu i afegeix al alt i al title de les imatges del banner
            el literal Obriu l'enllac en una finestra nova.
        """
        return '%s, %s' % (altortitle, self.portal().translate(
            _('obrir_link_finestra_nova')))


class linksFooterViewlet(viewletBase, GWGlobalSectionsViewlet):

    _opener_markup_template = ('')

    def render(self):
        config = genwebFooterConfig()
        if config.enable_links and self.context.portal_type != 'Plone Site':
            return super(viewletBase, self).render()
        else:
            return ""

    @memoize
    def getCustomLinks(self):
        lang = self.pref_lang()
        footer_config = genwebFooterConfig()

        title = getattr(footer_config, 'title_links_' + lang, '')
        if not title or title == '':
            title = self.context.translate(
                'Administració', domain='genweb', target_language=lang)

        result = {'title': title,
                  'links': []}

        # if footer_config.enable_login:
        #     result['links'].append(
        #         {
        #             'title': self.context.translate('Log in', domain='plone', target_language=lang),
        #             'link': self.context.absolute_url() + '/login',
        #             'external': False
        #         }
        #     )

        # if footer_config.enable_register:
        #     portal = api.portal.get()
        #     result['links'].append(
        #         {
        #             'title': self.context.translate('Register', domain='plone', target_language=lang),
        #             'link': portal.absolute_url() + '/@@register',
        #             'external': False
        #         }
        #     )

        table = getattr(footer_config, 'table_links_' + lang, [])
        if table:
            for link in table:
                result['links'].append(
                    {
                        'title': link['title'],
                        'link': link['link'],
                        'external': True
                    }
                )

        return result

    @memoize
    def getLinksPersonalized(self):
        return genwebFooterConfig().complete_custom_links

    @memoize
    def getLinksPage(self):
        """
        Funcio que retorna la pagina de contacte personalitzada
        """
        context = aq_inner(self.context)
        lang = self.context.Language()

        if lang == 'ca':
            customized_page = getattr(context, 'enllacospersonalitzats', False)
        elif lang == 'es':
            customized_page = getattr(context, 'enlacespersonalizados', False)
        elif lang == 'en':
            customized_page = getattr(context, 'customizedlinks', False)

        try:
            state = api.content.get_state(customized_page)
            if state == 'published':
                return customized_page.text.raw
            else:
                return ''
        except:
            return ''


class footerViewlet(viewletBase):

    @memoize
    def getClass(self):
        footer_config = genwebFooterConfig()
        return getattr(footer_config, 'theme', 'dark-theme')

    @memoize
    def getHeroURL(self):
        header_config = genwebHeaderConfig()
        portal_url = self.root_url()

        if getattr(header_config, 'full_hero_image', False):
            return '{}/@@gw-full-hero'.format(portal_url)
        elif getattr(header_config, 'hero_image', False):
            return '{}/@@gw-hero'.format(portal_url)
        else:
            return False

    @memoize
    def getSignatura(self):
        lang = self.pref_lang()
        footer_config = genwebFooterConfig()
        return getattr(footer_config, 'signatura_' + lang, '')

    @memoize
    def getLinksPeu(self):
        lang = self.pref_lang()

        links = {"ca": {"contact":       {"url": self.root_url() + "/ca/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/ca/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}},

                 "es": {"contact":       {"url": self.root_url() + "/es/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/es/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}},

                 "en": {"contact":       {"url": self.root_url() + "/en/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/en/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}}}

        return links[lang]


class resourcesViewlet(viewletBase):

    @memoize
    def getFileCSS(self):
        resources_config = genwebResourcesConfig()
        if getattr(resources_config, 'file_css', False):
            filename, data = b64decode_file(resources_config.file_css)
            data = NamedFile(data=data, filename=filename)
            return data._data._data

    @memoize
    def getTextCSS(self):
        resources_config = genwebResourcesConfig()
        return "<style>" + resources_config.text_css + "</style>"


class socialtoolsViewlet(viewletBase):

    def render(self):
        if api.user.is_anonymous():
            return super(viewletBase, self).render()
        else:
            return ""

    @memoize
    def data(self):
        title = self.context.title
        url = self.root_url() + '/resolveuid/' + IUUID(self.context)

        return [
            {
                'title': 'Twitter',
                'url': 'https://twitter.com/intent/tweet?url=' + url + '&text=' + title,
                'icon': 'bi bi-twitter',
                'action': False,
            },
            {
                'title': 'Facebook',
                'url': 'https://www.facebook.com/sharer/sharer.php?u=' + url,
                'icon': 'bi bi-facebook',
                'action': False,
            },
            {
                'title': 'Whatsapp',
                'url': 'https://wa.me/?text=' + title + ' ' + url,
                'icon': 'bi bi-whatsapp',
                'action': False,
            },
            # {
            #     'title': 'Telegram',
            #     'url': 'https://telegram.me/share/url?url=' + url + '&text=' + title,
            #     'icon': 'bi bi-telegram',
            #     'action': False,
            # },
            # {
            #     'title': 'Linkedin',
            #     'url': 'https://www.linkedin.com/shareArticle?url=' + url,
            #     'icon': 'bi bi-linkedin',
            #     'action': False,
            # },
            {
                'title': _(u"Copiar enllaç"),
                'url': url,
                'icon': 'fa-regular fa-copy',
                'action': True,
                'id': 'copy-universal-link',
                'tooltip': _(u"Copiat!"),
            }
        ]


class newsDateViewlet(viewletBase):

    def render(self):
        if INewsItem.providedBy(self.context):
            return super(viewletBase, self).render()
        else:
            return ""

    def formatDate(self):
        if self.context.effective_date:
            return toLocalizedTime(self, self.context.effective_date)

        return toLocalizedTime(self, self.context.modification_date)
