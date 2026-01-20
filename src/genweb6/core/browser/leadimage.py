# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.event.interfaces import IOccurrence
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.interfaces import IEvent
from genweb6.core.behaviors.event_image import IEventImage
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
        
        # Si es un Event, verificar si tiene not_show_image activado
        # Si está activado, ocultar la imagen en la página (pero mostrarla en portlets)
        if IEvent.providedBy(self.context):
            # Intentar obtener el valor del campo usando el adapter del behavior
            try:
                from zope.component import getAdapter
                event_image = getAdapter(self.context, IEventImage)
                not_show_image = event_image.not_show_image
            except:
                # Si no se puede obtener el adapter, leer directamente del contexto
                not_show_image = getattr(self.context, 'not_show_image', False)
            
            if not_show_image:
                self.available = False
                return
        
        self.available = True

        super().update()
