# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.navtree import DefaultNavtreeStrategy
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from datetime import datetime
from plone import api
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.namedfile import NamedBlobFile
from zope.i18nmessageid import MessageFactory

from genweb6.core import _

import os
import pdfkit
import transaction

_PMF = MessageFactory('plone')


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

        items = query_items_in_natural_sort_order(self.context, query)
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

        items = query_items_in_natural_sort_order(self.context, query)
        os.mkdir(exp_path)
        from_path = '/'.join(self.context.getPhysicalPath())
        folders = {
            plone_id: from_path
        }

        options_pdf = {'cookie': [('__ac', self.request.cookies['__ac'])]}

        for item in items:
            # diff between item path and root path
            relative_path = os.path.relpath(item.getPath(), from_path)
            zip_path = os.path.join(exp_path, relative_path)
            if item.portal_type == 'Folder':
                os.mkdir(zip_path)  # create folder in root path + relative path
                # update virtual folder structure
                folders.update({item.id.lower(): item.getPath()})
                print(("Saved {}".format(zip_path)))
            elif item.portal_type == 'File':
                obj = item.getObject()
                for x in folders:
                    test_path = folders[x] + '/' + obj.id
                    if test_path == item.getPath():
                        f = open(zip_path, 'wb')

                f.write(obj.file.data)
                f.close()
                print("Saved {}".format(zip_path))
            elif item.portal_type == 'Image':
                obj = item.getObject()
                for x in folders:
                    test_path = folders[x] + '/' + obj.id
                    if test_path == item.getPath():
                        f = open(zip_path, 'wb')
                f.write(obj.image.data)
                f.close()
                print("Saved {}".format(zip_path))
            elif item.portal_type in ['News Item', 'Document', 'genweb.upc.documentimage', 'Event']:
                obj = item.getObject()
                for x in folders:
                    test_path = folders[x] + '/' + obj.id
                    if test_path == item.getPath():
                        f = open(zip_path + '.pdf', 'wb')

                pdfkit.from_url(
                    obj.absolute_url(),
                    '/tmp/' + exp_path + '.pdf', options=options_pdf)
                f.write(open('/tmp/' + exp_path + '.pdf', 'rb').read())
                f.close()
                print("Saved {}".format(zip_path + '.pdf'))

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


def query_items_in_natural_sort_order(root, query):
    """
    Create a flattened out list of portal_catalog queried items in their natural depth first navigation order.

    @param root: Content item which acts as a navigation root

    @param query: Dictionary of portal_catalog query parameters

    @return: List of catalog brains
    """

    # Navigation tree base portal_catalog query parameters
    applied_query = {'path': '/'.join(root.getPhysicalPath()),
                     'sort_on': 'getObjPositionInParent'}

    # Apply caller's filters
    applied_query.update(query)

    # Set the navigation tree build strategy
    # - use navigation portlet strategy as base
    strategy = DefaultNavtreeStrategy(root)
    strategy.rootPath = '/'.join(root.getPhysicalPath())
    strategy.showAllParents = True
    strategy.bottomLevel = 999
    # This will yield out tree of nested dicts of
    # item brains with retrofitted navigational data
    tree = buildFolderTree(root, root, applied_query, strategy=strategy)

    items = []

    def flatten(children):
        """ Recursively flatten the tree """
        for c in children:
            # Copy catalog brain object into the result
            items.append(c["item"])
            children = c.get("children", None)
            if children:
                flatten(children)

    flatten(tree["children"])

    return items
