# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from zope.interface import alsoProvides

import logging

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
        for brain in self.context.portal_catalog(portal_type=('Folder', 'privateFolder')):
            obj = brain.getObject()
            if getattr(obj, "layout", None) == original:
                logger.info('- Actualitzat: ' + obj.absolute_url())
                msg += obj.absolute_url() + '\n'
                if 'list' not in self.request.form:
                    obj.setLayout(target)

        logger.info('- Ha finalitzat el procés.')
        return msg + '\nHa finalitzat el procés.'
