"""Utilitat per generar codis QR per a les inscripcions d'activitats"""

import qrcode
import io
import base64
from PIL import Image
import json
import datetime
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class QRGenerator:
    """Generador de codis QR per a inscripcions"""
    
    def __init__(self):
        self.qr_config = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_L,
            'box_size': 10,
            'border': 4,
        }
    
    def generate_qr_data(self, activitat, inscripcio):
        """Genera les dades que aniran dins del codi QR"""
        data = {
            'type': 'upcarts_inscripcio',
            'activitat_id': activitat.UID(),
            'inscripcio_id': inscripcio.UID(),
            'activitat_title': activitat.title,
            'nom': inscripcio.get_nom_complet(),
            'email': inscripcio.email,
            'collectiu': inscripcio.collectiu,
            'data_inscripcio': inscripcio.data_inscripcio.isoformat(),
            'timestamp': datetime.datetime.now().isoformat(),
        }
        
        # Afegir informació extra si existeix
        if hasattr(activitat, 'qr_info_extra') and activitat.qr_info_extra:
            data['extra_info'] = activitat.qr_info_extra
            
        # Afegir data de l'activitat
        if hasattr(activitat, 'data_inici') and activitat.data_inici:
            data['data_activitat'] = activitat.data_inici.isoformat()
            
        return json.dumps(data, ensure_ascii=False)
    
    def generate_qr_image(self, data_string):
        """Genera la imatge QR a partir de les dades"""
        qr = qrcode.QRCode(**self.qr_config)
        qr.add_data(data_string)
        qr.make(fit=True)
        
        # Crear la imatge
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_base64
    
    def generate_qr_for_inscripcio(self, activitat, inscripcio):
        """Genera el codi QR complet per a una inscripció"""
        # Generar dades
        qr_data = self.generate_qr_data(activitat, inscripcio)
        
        # Generar imatge
        qr_image = self.generate_qr_image(qr_data)
        
        # Guardar a la inscripció
        inscripcio.qr_code = qr_data
        inscripcio.qr_image_data = qr_image
        
        return {
            'data': qr_data,
            'image': qr_image,
            'data_url': f"data:image/png;base64,{qr_image}"
        }
    
    def validate_qr_data(self, qr_string):
        """Valida les dades d'un codi QR"""
        try:
            data = json.loads(qr_string)
            
            # Verificar que té els camps necessaris
            required_fields = ['type', 'activitat_id', 'inscripcio_id']
            for field in required_fields:
                if field not in data:
                    return False, f"Camp obligatori '{field}' no trobat"
            
            # Verificar que és del tipus correcte
            if data['type'] != 'upcarts_inscripcio':
                return False, "Tipus de QR no vàlid"
            
            return True, data
            
        except json.JSONDecodeError:
            return False, "Format JSON no vàlid"
        except Exception as e:
            return False, f"Error validant QR: {str(e)}"


# Instància global del generador
qr_generator = QRGenerator()