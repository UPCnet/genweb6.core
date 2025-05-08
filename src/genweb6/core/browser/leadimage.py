# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.event.interfaces import IOccurrence
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from zope.interface import alsoProvides
from zope.component import queryAdapter


class CustomLeadImageViewlet(LeadImageViewlet):

    def update(self):

        # Si es una Occurrence se va al contexto del Evento
        if IOccurrence.providedBy(self.context):
            self.context = getattr(self.context, '__parent__', self.context)

        if not ILeadImage.providedBy(self.context):
            self.available = False
            return
        self.available = True

        super().update()
