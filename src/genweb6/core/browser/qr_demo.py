"""Vista de demostració per crear inscripció i mostrar QR"""

from Products.Five.browser import BrowserView
from plone import api
from ..qr_generator import QRGenerator
import json


class QRDemoView(BrowserView):
    """Vista per crear inscripció de prova i mostrar QR"""
    
    def __call__(self):
        """Crea inscripció de prova i mostra QR"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Crear inscripció de prova si no existeix
        inscripcio = self.crear_inscripcio_prova()
        
        # Generar QR
        qr_generator = QRGenerator()
        qr_data = {
            "type": "upcarts_inscripcio",
            "activitat_id": self.context.UID(),
            "inscripcio_id": inscripcio.UID(),
            "activitat_title": self.context.title,
            "nom": inscripcio.get_nom_complet(),
            "email": inscripcio.email,
            "collectiu": inscripcio.get_collectiu_display()
        }
        
        qr_image_base64 = qr_generator.generate_qr_image(json.dumps(qr_data))
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🎫 QR Demo - {self.context.title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    margin: 0;
                    background: #f8f9fa;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                h1 {{ color: #007bff; }}
                .qr-container {{
                    margin: 20px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    border: 2px dashed #007bff;
                }}
                .qr-image {{
                    max-width: 300px;
                    margin: 20px auto;
                    display: block;
                }}
                .info {{
                    background: #e9ecef;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    text-align: left;
                }}
                .buttons {{
                    margin: 20px 0;
                }}
                button, .btn {{
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    margin: 5px;
                    border-radius: 5px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }}
                button:hover, .btn:hover {{ background: #0056b3; }}
                .success {{ background: #28a745 !important; }}
                .back-link {{ 
                    color: #007bff; 
                    text-decoration: none; 
                    margin-top: 20px;
                    display: inline-block;
                }}
                .json-data {{
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 12px;
                    text-align: left;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎫 QR Demo</h1>
                <h2>{self.context.title}</h2>
                
                <div class="info">
                    <strong>📋 Inscripció Creada:</strong><br>
                    <strong>Nom:</strong> {inscripcio.get_nom_complet()}<br>
                    <strong>Email:</strong> {inscripcio.email}<br>
                    <strong>Col·lectiu:</strong> {inscripcio.get_collectiu_display()}<br>
                    <strong>UID:</strong> {inscripcio.UID()}<br>
                    <strong>Assistit:</strong> {'Sí' if getattr(inscripcio, 'ha_assistit', False) else 'No'}
                </div>
                
                <div class="qr-container">
                    <h3>📱 Codi QR per Escanejar</h3>
                    <img src="data:image/png;base64,{qr_image_base64}" 
                         alt="Codi QR" class="qr-image">
                    <p><em>Escaneja aquest QR amb l'escàner per registrar assistència</em></p>
                </div>
                
                <div class="info">
                    <strong>🔍 Dades del QR:</strong>
                    <div class="json-data">{json.dumps(qr_data, indent=2, ensure_ascii=False)}</div>
                </div>
                
                <div class="buttons">
                    <a href="{self.context.absolute_url()}/@@qr_scanner_final" class="btn success">
                        📷 Anar a l'Escàner
                    </a>
                    <button onclick="window.location.reload()">🔄 Recrear QR</button>
                </div>
                
                <a href="{self.context.absolute_url()}" class="back-link">← Tornar a l'activitat</a>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def crear_inscripcio_prova(self):
        """Crea una inscripció de prova si no existeix"""
        
        # Buscar si ja existeix una inscripció de prova
        inscripcions = self.context.listFolderContents(
            contentFilter={'portal_type': 'Inscripcio'}
        )
        
        for inscripcio in inscripcions:
            if inscripcio.email == 'demo@upc.edu':
                return inscripcio
        
        # Crear nova inscripció de prova
        inscripcio_id = 'inscripcio-demo'
        
        if inscripcio_id in self.context.objectIds():
            api.content.delete(self.context[inscripcio_id])
        
        inscripcio = api.content.create(
            container=self.context,
            type='Inscripcio',
            id=inscripcio_id,
            title='Inscripció Demo',
            nom='Demo',
            cognoms='UPCArts',
            email='demo@upc.edu',
            collectiu='ESTUDIANT',
            telefon='123456789'
        )
        
        return inscripcio