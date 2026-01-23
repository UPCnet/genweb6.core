# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.event.interfaces import IOccurrence
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.interfaces import IEvent, INewsItem
from genweb6.core.behaviors.event_image import IEventImage, INewsImage
from zope.interface import alsoProvides
from zope.component import queryAdapter, getAdapter


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
            try:
                event_image = getAdapter(self.context, IEventImage)
                not_show_image = event_image.not_show_image
            except:
                not_show_image = getattr(self.context, 'not_show_image', False)
            
            if not_show_image:
                self.available = False
                return
        
        # Si es un News Item, verificar si tiene not_show_image activado
        # Si está activado, ocultar la imagen en la página (pero mostrarla en portlets)
        if INewsItem.providedBy(self.context):
            try:
                news_image = getAdapter(self.context, INewsImage)
                not_show_image = news_image.not_show_image
            except:
                not_show_image = getattr(self.context, 'not_show_image', False)
            
            if not_show_image:
                self.available = False
                return
        
        self.available = True

        super().update()
