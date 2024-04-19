# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.app.textfield.value import RichTextValue

from zope.interface import alsoProvides

import logging
import transaction

logger = logging.getLogger(__name__)


class migrationfixfolderviews(BrowserView):
    """
Aquesta vista canvia totes les vistes X per una Y.
La vista folder_extender no existeix en Plone 5

Paràmetres:
- old: Obligatori, vista a cambiar.
- new: Obligatori, nova vista que volem.
- list: Opcional, no aplica el canvi i llista el contiguts que utilitzen la vista antigua.

Exemples:
- /migrationfixfolderviews?old=folder_extended&new=listing_view
- /migrationfixfolderviews?old=folder_extended&new=listing_view&list
"""

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        if 'old' not in self.request.form or 'new' not in self.request.form:
            return 'Cal afegir els paràmetres old i new.\n\nEx:\n/migrationfixfolderviews?old=folder_extended&new=listing_view'

        original = self.request.form['old']
        target = self.request.form['new']

        msg = ''
        for brain in self.context.portal_catalog(portal_type=('Folder')):
            obj = brain.getObject()
            if getattr(obj, "layout", None) == original:
                logger.info('- Actualitzat: ' + obj.absolute_url())
                msg += obj.absolute_url() + '\n'
                if 'list' not in self.request.form:
                    obj.setLayout(target)

        logger.info('- Ha finalitzat el procés.')
        return msg + '\nHa finalitzat el procés.'

class migrationfixtemplates(BrowserView):
    """
Aquesta vista afegeix a las plantilles <div class="mceTmpl"></div>
"""

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        portal = api.portal.get()
        pc = api.portal.get_tool(name='portal_catalog')
        plantilles = pc.searchResults(portal_type='Document',
                                      path='/'.join(portal.getPhysicalPath()) + '/plantilles')

        msg = ''
        for brain in plantilles:
            obj = brain.getObject()
            if 'mceTmpl' not in obj.text.raw:
                new_text = str('<div class="mceTmpl">' + obj.text.raw + '</div>')
                obj.text = RichTextValue(new_text, 'text/plain', 'text/html')
                obj.reindexObject()

                logger.info('- Actualitzat: ' + obj.absolute_url())
                msg += obj.absolute_url() + '\n'
            else:
                logger.info('- No cal actualitzar: ' + obj.absolute_url())

        logger.info('- Ha finalitzat el procés.')
        return msg + '\nHa finalitzat el procés.'

class fix_collection_migration(BrowserView):
    """
Arreglar colecciones rotas criterios migrador
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        indexes_to_fix = [
            u'portal_type',
            u'review_state',
            u'Creator'
        ]

        operator_mapping = {
            "plone.app.querystring.operation.selection.is":
            "plone.app.querystring.operation.selection.any",
            # old -> new
            "plone.app.querystring.operation.string.is":
            "plone.app.querystring.operation.selection.any",
        }

        operator_mapping_or = {
            # old -> new
            u"plone.app.querystring.operation.selection.is":
                u"plone.app.querystring.operation.selection.any",
            u"plone.app.querystring.operation.string.is":
                u"plone.app.querystring.operation.selection.any",
        }

        operator_mapping_and = {
            # old -> new
            u"plone.app.querystring.operation.selection.is":
                u"plone.app.querystring.operation.selection.all",
            u"plone.app.querystring.operation.string.is":
                u"plone.app.querystring.operation.selection.all",
        }

        PORTAL_TYPE_MAPPING = {
            "Topic": "Collection",
            "Window": "Document",
        }

        REVIEW_STATE_MAPPING = {}

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type=['Collection']
        )

        for brain in brains:
            item = brain.getObject()
            query = item.query
            fixed_query = []

            for crit in query:
                if crit["i"] == "portal_type" and len(crit["v"]) > 30:
                    # Criterion is all types
                    continue

                if crit["o"].endswith("relativePath") and crit["v"] == "..":
                    # relativePath no longer accepts ..
                    crit["v"] = "..::1"

                if crit["i"] in indexes_to_fix:
                    for old_operator, new_operator in operator_mapping.items():
                        if crit["o"] == old_operator:
                            crit["o"] = new_operator

                if crit["o"] == "plone.app.querystring.operation.selection.all" and len(crit["v"]) == 1:
                    # all operator with one value is equivalent to any
                    crit["o"] = "plone.app.querystring.operation.selection.any"

                if crit["i"] == "portal_type":
                    # Some types may have changed their names
                    fixed_types = []
                    for portal_type in crit["v"]:
                        fixed_type = PORTAL_TYPE_MAPPING.get(portal_type, portal_type)
                        fixed_types.append(fixed_type)
                    crit["v"] = list(set(fixed_types))

                if crit["i"] == "review_state":
                    # Review states may have changed their names
                    fixed_states = []
                    for review_state in crit["v"]:
                        fixed_state = REVIEW_STATE_MAPPING.get(review_state, review_state)
                        fixed_states.append(fixed_state)
                    crit["v"] = list(set(fixed_states))

                if crit["o"] == "plone.app.querystring.operation.string.currentUser":
                    crit["v"] = ""

                fixed_query.append(crit)

            logger.info('- Actualitzada Collection: ' + item.absolute_url())
            logger.info('- Collection query old: ' + str(query))
            logger.info('- Collection query new: ' + str(fixed_query))
            item.reindexObject()

        transaction.commit()
        return 'OK'