"""Vista per escanejar codis QR des del navegador mòbil"""

from plone import api
from Products.Five.browser import BrowserView
from zope.publisher.browser import BrowserView as ZopeBrowserView
import json


class QRScannerView(BrowserView):
    """Vista per escanejar codis QR amb la càmera del mòbil"""
    
    def __call__(self):
        """Renderitza la pàgina d'escaneig QR"""
        return self.index()
    
    def get_api_url(self):
        """Retorna la URL de l'API de validació"""
        portal_url = api.portal.get().absolute_url()
        return f"{portal_url}/++api++/qr_validation"


class QRValidationAjaxView(BrowserView):
    """Vista AJAX per validar codis QR"""
    
    def __call__(self):
        """Processa la validació d'un codi QR via AJAX"""
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            # Obtenir el codi QR del request
            qr_code = self.request.get('qr_code', '')
            
            if not qr_code:
                self.request.response.setStatus(400)
                return json.dumps({'error': 'Codi QR no proporcionat'})
            
            # Importar i usar el servei de validació
            from ..api.qr_validation import QRValidationService
            
            # Crear una instància del servei
            service = QRValidationService(self.context, self.request)
            
            # Simular el body del request per al servei
            body_data = json.dumps({'qr_code': qr_code})
            self.request._body = body_data.encode('utf-8')
            self.request.environ['CONTENT_LENGTH'] = str(len(body_data))
            
            # Processar la validació
            result = service.validate_qr()
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'error': f'Error processant QR: {str(e)}'})


class QRStatsAjaxView(BrowserView):
    """Vista AJAX per obtenir estadístiques d'una activitat"""
    
    def __call__(self):
        """Retorna estadístiques d'assistència d'una activitat"""
        self.request.response.setHeader('Content-Type', 'application/json')
        
        try:
            activitat_uid = self.request.get('activitat_uid', '')
            
            if not activitat_uid:
                self.request.response.setStatus(400)
                return json.dumps({'error': 'UID de l\'activitat no proporcionat'})
            
            # Importar i usar el servei d'estadístiques
            from ..api.qr_validation import QRStatsService
            
            # Crear una instància del servei
            service = QRStatsService(self.context, self.request)
            
            # Processar les estadístiques
            result = service.reply()
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'error': f'Error obtenint estadístiques: {str(e)}'})