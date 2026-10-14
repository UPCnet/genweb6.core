"""Vista simple per mostrar QR de la inscripció demo"""

from Products.Five.browser import BrowserView
from plone import api
from ..qr_generator import QRGenerator
import json


class QRSimpleDemoView(BrowserView):
    """Vista simple per mostrar QR"""
    
    def __call__(self):
        """Mostra QR de la inscripció demo"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        try:
            # Buscar inscripció demo
            inscripcions = self.context.listFolderContents(
                contentFilter={'portal_type': 'Inscripcio'}
            )
            
            inscripcio_demo = None
            for inscripcio in inscripcions:
                if inscripcio.email == 'demo@upc.edu':
                    inscripcio_demo = inscripcio
                    break
            
            if not inscripcio_demo:
                # Crear inscripció si no existeix
                inscripcio_demo = api.content.create(
                    container=self.context,
                    type='Inscripcio',
                    id='inscripcio-demo-simple',
                    title='Demo Simple',
                    nom='Demo',
                    cognoms='Simple',
                    email='demo@upc.edu',
                    collectiu='ESTUDIANT',
                    telefon='123456789'
                )
            
            # Generar dades QR
            qr_data = {
                "type": "upcarts_inscripcio",
                "activitat_id": self.context.UID(),
                "inscripcio_id": inscripcio_demo.UID(),
                "activitat_title": self.context.title,
                "nom": f"{inscripcio_demo.nom} {inscripcio_demo.cognoms}",
                "email": inscripcio_demo.email,
                "collectiu": inscripcio_demo.collectiu
            }
            
            # Generar QR
            qr_generator = QRGenerator()
            qr_json = json.dumps(qr_data)
            qr_image_base64 = qr_generator.generate_qr_image(qr_json)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>QR Demo Simple</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        padding: 20px; 
                        text-align: center;
                        background: #f8f9fa;
                    }}
                    .container {{ 
                        max-width: 500px; 
                        margin: 0 auto; 
                        background: white;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{ color: #007bff; margin-bottom: 30px; }}
                    .qr-image {{ 
                        max-width: 300px; 
                        margin: 20px auto; 
                        border: 3px solid #007bff;
                        border-radius: 10px;
                        padding: 10px;
                        background: white;
                    }}
                    .info {{ 
                        background: #e9ecef; 
                        padding: 15px; 
                        border-radius: 5px; 
                        margin: 20px 0;
                        text-align: left;
                    }}
                    .btn {{ 
                        background: #28a745; 
                        color: white; 
                        padding: 15px 25px; 
                        border: none; 
                        border-radius: 5px; 
                        text-decoration: none; 
                        display: inline-block;
                        margin: 10px;
                        font-size: 16px;
                    }}
                    .btn:hover {{ background: #218838; }}
                    .back {{ background: #6c757d; }}
                    .back:hover {{ background: #5a6268; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎫 QR Demo</h1>
                    
                    <div class="info">
                        <strong>📋 Inscripció:</strong><br>
                        <strong>Nom:</strong> {inscripcio_demo.nom} {inscripcio_demo.cognoms}<br>
                        <strong>Email:</strong> {inscripcio_demo.email}<br>
                        <strong>Assistit:</strong> {'Sí' if getattr(inscripcio_demo, 'ha_assistit', False) else 'No'}
                    </div>
                    
                    <h3>📱 Escaneja aquest QR:</h3>
                    <img src="data:image/png;base64,{qr_image_base64}" 
                         alt="Codi QR" class="qr-image">
                    
                    <br>
                    <a href="{self.context.absolute_url()}/@@qr_scanner_final" class="btn">
                        📷 Anar a l'Escàner
                    </a>
                    
                    <br>
                    <a href="{self.context.absolute_url()}" class="btn back">← Tornar</a>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            return f"""
            <html>
            <body>
                <h1>Error</h1>
                <p>Error generant QR: {str(e)}</p>
                <a href="{self.context.absolute_url()}">← Tornar</a>
            </body>
            </html>
            """