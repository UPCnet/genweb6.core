"""API REST per validar codis QR i registrar assistència a activitats"""

from plone import api
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from plone.uuid.interfaces import IUUID
import json
import datetime
import transaction
from ..qr_generator import qr_generator


class QRValidationService(BrowserView):
    """Servei per validar codis QR i registrar assistència"""
    
    def __call__(self):
        """Processa la petició"""
        self.request.response.setHeader('Content-Type', 'application/json')
        
        method = self.request.method
        
        try:
            if method == 'POST':
                result = self.validate_qr()
            elif method == 'GET':
                result = self.get_validation_info()
            else:
                self.request.response.setStatus(405)
                result = {'error': 'Method not allowed'}
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'error': f'Error intern: {str(e)}'}, ensure_ascii=False)
    
    def validate_qr(self):
        """Valida un codi QR i registra l'assistència"""
        try:
            # Obtenir dades del request
            data = json.loads(self.request.get('BODY', '{}'))
            
            # Acceptar tant qr_code (string) com dades directes (object)
            if 'qr_code' in data:
                qr_code = data.get('qr_code', '')
                if not qr_code:
                    self.request.response.setStatus(400)
                    return {'error': 'Codi QR no proporcionat'}
                
                # Validar el format del QR
                is_valid, result = qr_generator.validate_qr_data(qr_code)
                
                if not is_valid:
                    self.request.response.setStatus(400)
                    return {'error': f'QR no vàlid: {result}'}
                
                qr_data = result
            else:
                # Les dades ja vénen com a objecte JSON del QR
                qr_data = data
                
                # Validar camps obligatoris
                required_fields = ['type', 'activitat_id', 'inscripcio_id']
                for field in required_fields:
                    if field not in qr_data:
                        self.request.response.setStatus(400)
                        return {'error': f'Camp obligatori mancat: {field}'}
                
                # Validar tipus
                if qr_data.get('type') != 'upcarts_inscripcio':
                    self.request.response.setStatus(400)
                    return {'error': 'Tipus de QR no vàlid'}
            
            # Buscar l'activitat
            activitat = api.content.get(UID=qr_data['activitat_id'])
            if not activitat:
                self.request.response.setStatus(404)
                return {'error': 'Activitat no trobada'}
            
            # Buscar la inscripció
            inscripcio = api.content.get(UID=qr_data['inscripcio_id'])
            if not inscripcio:
                self.request.response.setStatus(404)
                return {'error': 'Inscripció no trobada'}
            
            # Verificar que la inscripció pertany a l'activitat
            if inscripcio.aq_parent.UID() != activitat.UID():
                self.request.response.setStatus(400)
                return {'error': 'La inscripció no correspon a aquesta activitat'}
            
            # Verificar si ja ha assistit
            if getattr(inscripcio, 'ha_assistit', False):
                return {
                    'success': True,
                    'message': 'Assistència ja registrada anteriorment',
                    'already_registered': True,
                    'data': {
                        'activitat': activitat.title,
                        'nom': inscripcio.get_nom_complet(),
                        'email': inscripcio.email,
                        'collectiu': inscripcio.get_collectiu_display(),
                        'data_assistencia': inscripcio.data_assistencia.isoformat() if inscripcio.data_assistencia else None,
                    }
                }
            
            # Registrar l'assistència
            inscripcio.marcar_assistencia()
            
            # Guardar els canvis
            inscripcio.reindexObject()
            
            # Commit de la transacció
            transaction.commit()
            
            return {
                'success': True,
                'message': 'Assistència registrada correctament',
                'already_registered': False,
                'data': {
                    'activitat': activitat.title,
                    'nom': inscripcio.get_nom_complet(),
                    'email': inscripcio.email,
                    'collectiu': inscripcio.get_collectiu_display(),
                    'data_assistencia': inscripcio.data_assistencia.isoformat(),
                }
            }
            
        except json.JSONDecodeError:
            self.request.response.setStatus(400)
            return {'error': 'Format JSON no vàlid'}
        except Exception as e:
            self.request.response.setStatus(500)
            return {'error': f'Error intern: {str(e)}'}
    
    def get_validation_info(self):
        """Retorna informació sobre el servei de validació"""
        return {
            'service': 'QR Validation API',
            'version': '1.0',
            'endpoints': {
                'validate': {
                    'method': 'POST',
                    'description': 'Valida un codi QR i registra assistència',
                    'payload': {
                        'qr_code': 'string - Dades del codi QR en format JSON'
                    }
                }
            }
        }


class QRStatsService(BrowserView):
    """Servei per obtenir estadístiques d'assistència"""
    
    def __call__(self):
        """Processa la petició d'estadístiques"""
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            # Obtenir paràmetres
            activitat_uid = self.request.get('activitat_uid')
            
            if not activitat_uid:
                self.request.response.setStatus(400)
                return {'error': 'UID de l\'activitat no proporcionat'}
            
            # Buscar l'activitat
            activitat = api.content.get(UID=activitat_uid)
            if not activitat:
                self.request.response.setStatus(404)
                return {'error': 'Activitat no trobada'}
            
            # Obtenir estadístiques
            inscripcions = activitat.get_inscripcions()
            assistents = activitat.get_assistents()
            
            stats = {
                'activitat': {
                    'title': activitat.title,
                    'uid': activitat.UID(),
                    'data_inici': activitat.data_inici.isoformat() if activitat.data_inici else None,
                },
                'inscripcions': {
                    'total': len(inscripcions),
                    'assistents': len(assistents),
                    'pendents': len(inscripcions) - len(assistents),
                    'percentatge_assistencia': round((len(assistents) / len(inscripcions)) * 100, 2) if inscripcions else 0,
                },
                'detall_inscripcions': [
                    {
                        'nom': i.get_nom_complet(),
                        'email': i.email,
                        'collectiu': i.get_collectiu_display(),
                        'ha_assistit': getattr(i, 'ha_assistit', False),
                        'data_assistencia': i.data_assistencia.isoformat() if getattr(i, 'data_assistencia', None) else None,
                    }
                    for i in inscripcions
                ]
            }
            
            return json.dumps(stats, ensure_ascii=False)
            
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'error': f'Error obtenint estadístiques: {str(e)}'}, ensure_ascii=False)