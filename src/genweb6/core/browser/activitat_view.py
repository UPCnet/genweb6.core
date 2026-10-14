"""Vista personalitzada per l'Activitat amb botó d'inscripció"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView


class ActivitatView(BrowserView):
    """Vista personalitzada per l'Activitat"""
    
    template = ViewPageTemplateFile('activitat_view.pt')
    
    def __call__(self):
        """Renderitza el template"""
        return self.template()
    
    def get_inscripcions(self):
        """Retorna les inscripcions d'aquesta activitat"""
        return self.context.listFolderContents(
            contentFilter={'portal_type': 'Inscripcio'}
        )
    
    def get_data_formatted(self):
        """Retorna la data formatejada"""
        if hasattr(self.context, 'data_inici') and self.context.data_inici:
            return self.context.data_inici.strftime('%d/%m/%Y %H:%M')
        return 'Per determinar'
    
    def get_preu_formatted(self):
        """Retorna el preu formatejat"""
        preu = getattr(self.context, 'preu', 0)
        if preu and preu > 0:
            return f'{preu}€'
        return 'Gratuït'
    
    def get_percentatge_assistencia(self, total_assistents, total_inscripcions):
        """Calcula el percentatge d'assistència"""
        if total_inscripcions > 0:
            return f'{round((total_assistents/total_inscripcions)*100, 1)}%'
        return '0%'