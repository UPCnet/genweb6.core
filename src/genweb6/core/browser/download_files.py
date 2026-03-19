# -*- coding: utf-8 -*-
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from datetime import datetime
from plone import api
from plone.namedfile import NamedBlobFile
from zope.i18nmessageid import MessageFactory

from genweb6.core import _

import os
import uuid

import pdfkit
import transaction

_PMF = MessageFactory('plone')


def query_items_under_root(root, portal_types):
    """
    Todos los contenidos bajo ``root`` que coincidan con ``portal_types``,
    ordenados por path (padre antes que hijo). No usa el árbol de navegación,
    así que incluye Document, File, etc. aunque no aparezcan en el menú.
    """
    catalog = api.portal.get_tool('portal_catalog')
    base_path = '/'.join(root.getPhysicalPath())
    brains = catalog.searchResults(
        path={'query': base_path},
        portal_type=list(portal_types),
    )
    items = [b for b in brains if b.getPath() != base_path]
    items.sort(key=lambda b: b.getPath())
    return items


class DownloadFiles(BrowserView):

    template = ViewPageTemplateFile('views_templates/download_files.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def options(self):
        return {'File': _PMF('File'),
                'Image': _PMF('Image'),
                'News Item': _PMF('News Item'),
                'Document': _PMF('Document'),
                'genweb.upc.documentimage': _('Document Image'),
                'Event': _PMF('Event')}

    def _getSystemFontsCSS(self):
        """Crea un archivo CSS temporal que fuerza el uso de fuentes del sistema."""
        css_file = os.path.join('/tmp', 'system_fonts_pdf.css')
        # CSS que fuerza fuentes del sistema estándar y maximiza el ancho del contenido
        css_content = """
/* Fuerza el uso de fuentes del sistema estándar */
* {
    font-family: Arial, Helvetica, "Liberation Sans", "DejaVu Sans", sans-serif !important;
}
"""
        with open(css_file, 'w') as f:
            f.write(css_content)
        return css_file

    def __call__(self):
        form = self.request.form
        if not form or 'file_type' not in form:
            return self.template()

        query = {'portal_type': []}
        options = [key for key in self.options().keys()]
        if 'all' in form['file_type']:
            query['portal_type'] = ['LIF', 'LRF', 'Folder'] + options
        else:
            query['portal_type'] = ['LIF', 'LRF', 'Folder']
            for option in options:
                if option in form['file_type']:
                    query['portal_type'].append(option)

        items = query_items_under_root(self.context, query['portal_type'])
        if not items:
            IStatusMessage(self.request).addStatusMessage(u"No files found!", "info")
            return self.template()

        today = datetime.today().strftime("%Y-%m-%d")
        plone_id = 'export-{0}'.format(self.context.id)
        exp_path = 'export-{0}-{1}'.format(self.context.id, today)

        if os.path.exists(exp_path):
            os.system('rm -rf {}'.format(exp_path))
        if plone_id in self.context:
            api.content.delete(obj=self.context[plone_id])

        items = query_items_under_root(self.context, query['portal_type'])
        os.mkdir(exp_path)
        from_path = '/'.join(self.context.getPhysicalPath())

        ac_cookie = self.request.cookies.get('__ac')
        options_pdf = {'cookie': [('__ac', ac_cookie)]} if ac_cookie else {}

        css_file = self._getSystemFontsCSS()
        options_pdf['user-style-sheet'] = css_file

        for item in items:
            relative_path = os.path.relpath(item.getPath(), from_path)
            zip_path = os.path.join(exp_path, relative_path)
            is_folderish = getattr(item, 'is_folderish', False) or item.portal_type in (
                'Folder', 'LIF', 'LRF', 'Large Folder',
            )

            if is_folderish:
                os.makedirs(zip_path, exist_ok=True)
                print(("Saved {}".format(zip_path)))
            elif item.portal_type == 'File':
                obj = item.getObject()
                parent_dir = os.path.dirname(zip_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                with open(zip_path, 'wb') as f:
                    f.write(obj.file.data)
                print("Saved {}".format(zip_path))
            elif item.portal_type == 'Image':
                obj = item.getObject()
                parent_dir = os.path.dirname(zip_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                with open(zip_path, 'wb') as f:
                    f.write(obj.image.data)
                print("Saved {}".format(zip_path))
            elif item.portal_type in ['News Item', 'Document', 'genweb.upc.documentimage', 'Event']:
                obj = item.getObject()
                pdf_path = zip_path + '.pdf'
                parent_dir = os.path.dirname(pdf_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                url = obj.absolute_url() + '/@@genweb.get.dxdocument.text.complete.style'
                tmp_pdf = '/tmp/{0}-{1}.pdf'.format(exp_path, uuid.uuid4().hex)
                try:
                    pdfkit.from_url(url, tmp_pdf, options=options_pdf)
                    if os.path.isfile(tmp_pdf) and os.path.getsize(tmp_pdf) > 0:
                        with open(tmp_pdf, 'rb') as tmp_f:
                            with open(pdf_path, 'wb') as f:
                                f.write(tmp_f.read())
                        print("Saved {}".format(pdf_path))
                finally:
                    if os.path.isfile(tmp_pdf):
                        try:
                            os.remove(tmp_pdf)
                        except OSError:
                            pass

        os.system('zip -r {0}.zip {0}'.format(exp_path))
        os.system('rm -rf {}'.format(exp_path))

        allowed_types = [ct.id for ct in self.context.allowedContentTypes()]
        disable_file = False
        if 'File' not in allowed_types:
            disable_file = True
            behavior = ISelectableConstrainTypes(self.context)
            behavior.setLocallyAllowedTypes(list(allowed_types + ['File']))

        zip_file = api.content.create(
            type='File',
            title=exp_path,
            id=plone_id,
            container=self.context,
        )
        zip_file.file = NamedBlobFile(
            data=open('{}.zip'.format(exp_path), 'rb'),
            filename=u'{}.zip'.format(exp_path),
            contentType='application/zip'
        )

        if disable_file:
            behavior.setLocallyAllowedTypes(list(allowed_types))

        zip_file.reindexObject()
        transaction.commit()
        self.request.response.redirect(zip_file.absolute_url() + '/view')


