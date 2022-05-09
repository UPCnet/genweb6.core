# -*- coding: utf-8 -*-
from Acquisition import aq_parent, aq_inner
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError

from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from zope.i18nmessageid import MessageFactory

try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

import transaction
import unicodedata

_ = MessageFactory('plone')


class FolderDelete(BrowserView):
    __module__ = __name__
    delete_confirmation = ViewPageTemplateFile('templates/confirmation.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.paths = None
        self.portal = getSite()
        self.utils = self.portal.plone_utils

        if 'paths' in self.request.form:
            self.paths = self.request.form['paths']

    def action(self):
        """ return name of the view """
        return ('@@%s' % self.__name__)

    def paths(self):
        """ return paths"""
        return self.paths

    def strip_portal_path(self, path):
        portal_path = self.portal.getPhysicalPath()
        path = path.split('/')
        for id in portal_path:
            if id == path[0]:
                path.pop(0)
        return '/'.join(path)

    def titles(self):
        """ return paths, without portal_id"""

        stripped_paths = [self.strip_portal_path(path) for path in self.paths]
        return stripped_paths

    def __call__(self):
        """ some documentation """
        if (self.paths is None):
            if ('@@folder_delete' in self.request['URL']):
                return self.request.response.redirect(self.context.absolute_url() + '/folder_contents')
            else:
                message = _(u'You must select at least one item.')
                self.utils.addPortalMessage(message)
                return self.request.response.redirect(self.context.absolute_url() + '/folder_contents')
        # if not self submitted, return confirmation screen
        if ('form.button.Delete' not in self.request and 'form.button.Cancel' not in self.request):
            return self.delete_confirmation()
        elif 'form.button.Delete' in self.request:
            return self.delete_folder()
        elif 'form.button.Cancel' in self.request:
            return self.request.response.redirect(self.context.absolute_url() + '/folder_contents')

    def delete_folder(self):
        """ delete objects """
        self.request.set('link_integrity_events_to_expect', len(self.paths))
        # Using the legacy method from Plone 4
        success, failure = self.utils.deleteObjectsByPaths(
            self.paths, REQUEST=self.request)
        if success:
            self.status = 'success'
            mapping = {u'items': ', '.join(success)}
            message = _(u'${items} deleted.', mapping=mapping)
            self.utils.addPortalMessage(message)
            view = self.context.restrictedTraverse('folder_contents')
        if failure:
            failure_message = ', '.join(
                [('%s (%s)' % (x, str(y))) for (x, y,) in failure.items()])
            message = _(u'${items} could not be deleted.',
                        mapping={u'items': failure_message})
            self.utils.addPortalMessage(message, type='error')
            view = self.context.restrictedTraverse('folder_contents')
        return view()

    def deleteObjectsByPaths(self, paths, handle_errors=True, REQUEST=None):
        """Copy of deleteObjectsByPaths of the method of same name in
        ``Products.CMFPlone.PloneTool.PloneTool``.
        We just know that
        """
        failure = {}
        success = []
        # use the portal for traversal in case we have relative paths
        portal = getSite()
        traverse = portal.restrictedTraverse
        for path in paths:
            # Skip and note any errors
            if handle_errors:
                sp = transaction.savepoint(optimistic=True)
            try:
                obj = traverse(path)

                # Check for the case where a path to a nonexisting object
                # deletes an acquired object
                if path.startswith('/'):
                    absolute_path = path
                else:
                    portal_path = '/'.join(portal.getPhysicalPath())
                    absolute_path = "%s/%s" % (portal_path, path)
                if '/'.join(obj.getPhysicalPath()) != absolute_path:
                    raise
                # end check

                obj_parent = aq_parent(aq_inner(obj))
                obj_parent.manage_delObjects([obj.getId()])
                # PATCH: support for content with non ASCII chars
                title_or_id = obj.title_or_id()
                if not isinstance(title_or_id, unicode):
                    title_or_id = unicode(title_or_id, 'UTF-8', 'ignore')
                # Transform in plain ASCII
                title_or_id = unicodedata.normalize(
                    'NFKD', title_or_id).encode('ascii', 'ignore')
                success.append('%s (%s)' % (title_or_id, path))
                # /PATCH
            except ConflictError:
                raise
            except LinkIntegrityNotificationException:
                raise
            except Exception as e:
                if handle_errors:
                    sp.rollback()
                    failure[path] = e
                else:
                    raise
        transaction_note('Deleted %s' % (', '.join(success)))
        return success, failure
