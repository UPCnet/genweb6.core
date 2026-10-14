"""Vista simple per provar la generació de QR"""

from Products.Five.browser import BrowserView
import qrcode
import io
import base64
import json
import datetime


class QRTestView(BrowserView):
    """Vista per provar la generació de QR"""
    
    def __call__(self):
        """Genera un QR de prova per a l'activitat actual"""
        
        # Configurar Content-Type per HTML
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Generar dades de prova per al QR
        qr_data = {
            'type': 'upcarts_inscripcio',
            'activitat_id': self.context.UID() if hasattr(self.context, 'UID') else 'test-123',
            'inscripcio_id': 'inscripcio-test-456',
            'activitat_title': getattr(self.context, 'title', 'Activitat de prova'),
            'nom': 'Joan Exemple',
            'email': 'joan@upc.edu',
            'collectiu': 'ESTUDIANT',
            'data_inscripcio': datetime.datetime.now().isoformat(),
            'timestamp': datetime.datetime.now().isoformat(),
        }
        
        # Convertir a JSON
        qr_string = json.dumps(qr_data, ensure_ascii=False)
        
        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Crear imatge
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Retornar HTML amb el QR
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>QR Test - {getattr(self.context, 'title', 'Activitat')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                .qr-section {{ background: #f8f9fa; padding: 30px; border-radius: 8px; margin: 20px 0; }}
                .qr-image {{ border: 2px solid #007bff; padding: 10px; background: white; border-radius: 8px; }}
                .data-section {{ background: #e9ecef; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; }}
                pre {{ background: white; padding: 15px; border-radius: 4px; overflow-x: auto; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Prova del Sistema QR</h1>
                <h2>{getattr(self.context, 'title', 'Activitat de prova')}</h2>
                
                <div class="qr-section">
                    <h3>📱 Codi QR Generat</h3>
                    <img src="data:image/png;base64,{img_base64}" alt="Codi QR" class="qr-image">
                    <p><small>Escaneja aquest QR amb el teu mòbil</small></p>
                </div>
                
                <div class="data-section">
                    <h3>📋 Dades del QR</h3>
                    <pre>{json.dumps(qr_data, indent=2, ensure_ascii=False)}</pre>
                </div>
                
                <div>
                    <a href="{self.context.absolute_url()}/qr_scanner" class="btn">📷 Obrir Escàner QR</a>
                    <a href="{self.context.absolute_url()}" class="btn">← Tornar a l'Activitat</a>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #d1ecf1; border-radius: 8px;">
                    <h4>🧪 Com provar:</h4>
                    <ol style="text-align: left;">
                        <li>Fes una captura de pantalla d'aquest QR</li>
                        <li>Clica "Obrir Escàner QR"</li>
                        <li>Apunta la càmera al QR de la pantalla</li>
                        <li>Veuràs com es registra l'assistència automàticament</li>
                    </ol>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html