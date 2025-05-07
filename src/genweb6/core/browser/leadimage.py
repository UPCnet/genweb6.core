# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.event.interfaces import IOccurrence


class CustomLeadImageViewlet(LeadImageViewlet):

    def update(self):
        # Si es una Occurrence se va al contexto del Evento
        if IOccurrence.providedBy(self.context):
            self.context = getattr(self.context, '__parent__', self.context)

        super().update()
