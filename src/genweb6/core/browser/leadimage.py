# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.event.interfaces import IOccurrence
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from genweb6.core.behaviors.event_image import IContentImage
from zope.component import getAdapter


class CustomLeadImageViewlet(LeadImageViewlet):

    def update(self):

        # Si es una Occurrence se va al contexto del Evento
        if IOccurrence.providedBy(self.context):
            self.context = getattr(self.context, '__parent__', self.context)

        if not ILeadImage.providedBy(self.context):
            self.available = False
            return
        
        # Verificar si tiene not_show_image activado
        # Si está activado, ocultar la imagen en la página (pero mostrarla en portlets)
        try:
            content_image = getAdapter(self.context, IContentImage)
            not_show_image = content_image.not_show_image
        except:
            not_show_image = getattr(self.context, 'not_show_image', False)
        
        if not_show_image:
            self.available = False
            return
        
        self.available = True

        super().update()
