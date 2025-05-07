from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from zope.interface import alsoProvides

class CustomLeadImageViewlet(LeadImageViewlet):
    def update(self):
        # Accede al objeto original si es una ocurrencia
        real_context = getattr(self.context, '__parent__', self.context)

        # Solo usa el objeto real si tiene la interfaz de lead image
        if ILeadImage.providedBy(real_context):
            self.context = real_context

        super().update()
