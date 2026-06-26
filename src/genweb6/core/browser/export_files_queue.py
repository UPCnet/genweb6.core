# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.i18n import translate
from zope.interface import alsoProvides

from genweb6.core import _
from genweb6.core import export_job_registry
from genweb6.core.async_tasks import cancel_scheduled_export, get_export_queue_stats


_STATUS_LABELS = {
    export_job_registry.STATUS_QUEUED: _(u"Pendent"),
    export_job_registry.STATUS_RUNNING: _(u"En execució"),
    export_job_registry.STATUS_SUCCESS: _(u"Finalitzada"),
    export_job_registry.STATUS_EMPTY: _(u"Sense fitxers"),
    export_job_registry.STATUS_ERROR: _(u"Error"),
    export_job_registry.STATUS_INTERRUPTED: _(u"Interrompuda"),
    export_job_registry.STATUS_CANCELLED: _(u"Cancel·lada"),
}


class ExportFilesQueueView(BrowserView):
    """Vista de gestió de la cua d'exportacions asíncrones de fitxers."""

    template = ViewPageTemplateFile('views_templates/export_files_queue.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def jobs(self):
        return export_job_registry.list_jobs(limit=200)

    def stats(self):
        return get_export_queue_stats()

    def status_label(self, status):
        label = _STATUS_LABELS.get(status)
        if label is None:
            return status
        return translate(label, context=self.request)

    def portal_types_label(self, job):
        portal_types = job.get('portal_types') or []
        if not portal_types:
            return job.get('portal_types_sig') or u'-'

        portal_types_tool = api.portal.get().portal_types
        labels = []
        for type_id in portal_types:
            try:
                title = portal_types_tool[type_id].Title()
            except KeyError:
                title = type_id
            labels.append(translate(title, context=self.request))
        return u', '.join(labels)

    def folder_url(self, job):
        base_url = job.get('base_url')
        if base_url:
            return base_url
        context_path = job.get('context_path') or ''
        site_path = job.get('site_path') or ''
        if context_path.startswith(site_path):
            relative = context_path[len(site_path):].lstrip('/')
            portal = api.portal.get()
            return '{0}/{1}'.format(portal.absolute_url(), relative)
        return context_path

    def can_cancel(self, job):
        return job.get('status') == export_job_registry.STATUS_QUEUED

    def __call__(self):
        if self.request.form.get('cancel_job'):
            alsoProvides(self.request, IDisableCSRFProtection)
            job_id = self.request.form.get('job_id', '').strip()
            success, error_code = cancel_scheduled_export(job_id)
            if success:
                message = _(u"L'exportació s'ha cancel·lat correctament.")
                msg_type = 'info'
            elif error_code == 'not_found':
                message = _(u"No s'ha trobat l'exportació indicada.")
                msg_type = 'warning'
            else:
                message = _(
                    u"No es pot cancel·lar aquesta exportació "
                    u"(només es poden cancel·lar les pendents)."
                )
                msg_type = 'warning'
            IStatusMessage(self.request).addStatusMessage(message, msg_type)
            self.request.response.redirect(
                '{0}/@@export_files_queue'.format(
                    api.portal.get().absolute_url())
            )
            return u''

        return self.template()
