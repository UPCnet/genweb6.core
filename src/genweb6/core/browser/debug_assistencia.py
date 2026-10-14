"""Vistes per debugar i modificar assistència"""

from Products.Five.browser import BrowserView
from plone import api
import json
import datetime
import transaction


class DebugMarcarAssistenciaView(BrowserView):
    """Vista per marcar assistència manualment"""
    
    def __call__(self):
        """Marca assistència d'una inscripció"""
        
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            # Obtenir dades del request
            if self.request.method == 'POST':
                body = self.request.get('BODY', '{}')
                data = json.loads(body)
                inscripcio_uid = data.get('inscripcio_uid')
            else:
                inscripcio_uid = self.request.get('inscripcio_uid')
            
            if not inscripcio_uid:
                return json.dumps({'error': 'UID de la inscripció no proporcionat'})
            
            # Buscar la inscripció
            inscripcio = api.content.get(UID=inscripcio_uid)
            if not inscripcio:
                return json.dumps({'error': 'Inscripció no trobada'})
            
            # Marcar assistència directament
            inscripcio.ha_assistit = True
            inscripcio.data_assistencia = datetime.datetime.now()
            
            # Guardar canvis
            inscripcio.reindexObject()
            transaction.commit()
            
            return json.dumps({
                'success': True,
                'message': f'Assistència marcada per {inscripcio.get_nom_complet()}',
                'ha_assistit': inscripcio.ha_assistit,
                'data_assistencia': str(inscripcio.data_assistencia)
            })
            
        except Exception as e:
            return json.dumps({'error': f'Error marcant assistència: {str(e)}'})


class DebugEsborrarAssistenciaView(BrowserView):
    """Vista per esborrar assistència manualment"""
    
    def __call__(self):
        """Esborra assistència d'una inscripció"""
        
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            # Obtenir dades del request
            if self.request.method == 'POST':
                body = self.request.get('BODY', '{}')
                data = json.loads(body)
                inscripcio_uid = data.get('inscripcio_uid')
            else:
                inscripcio_uid = self.request.get('inscripcio_uid')
            
            if not inscripcio_uid:
                return json.dumps({'error': 'UID de la inscripció no proporcionat'})
            
            # Buscar la inscripció
            inscripcio = api.content.get(UID=inscripcio_uid)
            if not inscripcio:
                return json.dumps({'error': 'Inscripció no trobada'})
            
            # Esborrar assistència
            inscripcio.ha_assistit = False
            inscripcio.data_assistencia = None
            
            # Guardar canvis
            inscripcio.reindexObject()
            transaction.commit()
            
            return json.dumps({
                'success': True,
                'message': f'Assistència esborrada per {inscripcio.get_nom_complet()}',
                'ha_assistit': inscripcio.ha_assistit,
                'data_assistencia': None
            })
            
        except Exception as e:
            return json.dumps({'error': f'Error esborrant assistència: {str(e)}'})


class DebugInfoInscripcioView(BrowserView):
    """Vista per obtenir informació detallada d'una inscripció"""
    
    def __call__(self):
        """Retorna informació detallada d'una inscripció"""
        
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            inscripcio_uid = self.request.get('inscripcio_uid')
            
            if not inscripcio_uid:
                return json.dumps({'error': 'UID de la inscripció no proporcionat'})
            
            # Buscar la inscripció
            inscripcio = api.content.get(UID=inscripcio_uid)
            if not inscripcio:
                return json.dumps({'error': 'Inscripció no trobada'})
            
            # Obtenir tots els atributs
            info = {
                'id': inscripcio.getId(),
                'title': inscripcio.title,
                'uid': inscripcio.UID(),
                'portal_type': inscripcio.portal_type,
                'nom': getattr(inscripcio, 'nom', None),
                'cognoms': getattr(inscripcio, 'cognoms', None),
                'email': getattr(inscripcio, 'email', None),
                'collectiu': getattr(inscripcio, 'collectiu', None),
                'ha_assistit': getattr(inscripcio, 'ha_assistit', None),
                'data_assistencia': str(getattr(inscripcio, 'data_assistencia', None)),
                'created': str(inscripcio.created()),
                'modified': str(inscripcio.modified()),
                'path': '/'.join(inscripcio.getPhysicalPath()),
                'parent_path': '/'.join(inscripcio.aq_parent.getPhysicalPath()),
                'all_attributes': [attr for attr in dir(inscripcio) if not attr.startswith('_')]
            }
            
            return json.dumps(info, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'error': f'Error obtenint informació: {str(e)}'})