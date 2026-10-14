"""Vista per generar directament la imatge QR"""

from Products.Five.browser import BrowserView
import qrcode
import io
import json
import datetime


class QRImageView(BrowserView):
    """Vista que retorna directament la imatge PNG del QR"""
    
    def __call__(self):
        """Genera i retorna la imatge QR directament"""
        
        try:
            # Generar dades de prova
            qr_data = {
                'type': 'upcarts_inscripcio',
                'activitat_id': self.context.UID() if hasattr(self.context, 'UID') else 'test-123',
                'inscripcio_id': 'inscripcio-test-456',
                'activitat_title': getattr(self.context, 'title', 'Test Activitat'),
                'nom': 'Joan Exemple',
                'email': 'joan@upc.edu',
                'collectiu': 'ESTUDIANT',
                'timestamp': datetime.datetime.now().isoformat(),
            }
            
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data, ensure_ascii=False))
            qr.make(fit=True)
            
            # Crear imatge
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Configurar response per imatge PNG
            self.request.response.setHeader('Content-Type', 'image/png')
            self.request.response.setHeader('Content-Disposition', 'inline; filename="qr_code.png"')
            
            return buffer.getvalue()
            
        except Exception as e:
            # En cas d'error, retornar text
            self.request.response.setHeader('Content-Type', 'text/plain')
            return f"Error generant QR: {str(e)}"