"""Vista per crear inscripcions de test"""

from Products.Five.browser import BrowserView
from plone import api
from ..qr_generator import QRGenerator
import json
import random


class CrearInscripcioTestView(BrowserView):
    """Vista per crear una nova inscripció de test"""
    
    def __call__(self):
        """Crea una nova inscripció de test"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Noms de test
        noms_test = [
            ("Maria", "García López", "maria.garcia@upc.edu", "PDI"),
            ("Joan", "Martínez Pérez", "joan.martinez@upc.edu", "ESTUDIANT"), 
            ("Anna", "Rodríguez Vila", "anna.rodriguez@upc.edu", "PTGAS"),
            ("Pere", "Fernández Ruiz", "pere.fernandez@upc.edu", "ALUMNI"),
            ("Laura", "González Moreno", "laura.gonzalez@upc.edu", "EXTERN"),
            ("David", "Sánchez Torres", "david.sanchez@upc.edu", "ESTUDIANT"),
            ("Carla", "López Jiménez", "carla.lopez@upc.edu", "PDI"),
            ("Marc", "Hernández Vega", "marc.hernandez@upc.edu", "ESTUDIANT")
        ]
        
        # Seleccionar un nom aleatori
        nom, cognoms, email, collectiu = random.choice(noms_test)
        
        # Crear ID únic
        import time
        timestamp = str(int(time.time()))
        inscripcio_id = f"inscripcio-test-{timestamp}"
        
        try:
            # Crear nova inscripció
            inscripcio = api.content.create(
                container=self.context,
                type='Inscripcio',
                id=inscripcio_id,
                title=f'Inscripció Test - {nom} {cognoms}',
                nom=nom,
                cognoms=cognoms,
                email=email,
                collectiu=collectiu,
                telefon=f'93{random.randint(1000000, 9999999)}'
            )
            
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
                <title>✅ Nova Inscripció Creada</title>
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
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    h1 {{ color: #28a745; }}
                    .info {{
                        background: #d4edda;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        text-align: left;
                        border: 1px solid #c3e6cb;
                    }}
                    .qr-container {{
                        margin: 30px 0;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 10px;
                        border: 2px dashed #007bff;
                    }}
                    .qr-image {{
                        max-width: 300px;
                        margin: 20px auto;
                        display: block;
                        border: 3px solid #007bff;
                        border-radius: 10px;
                        padding: 10px;
                        background: white;
                    }}
                    .btn {{
                        background: #007bff;
                        color: white;
                        padding: 15px 25px;
                        border: none;
                        border-radius: 5px;
                        text-decoration: none;
                        display: inline-block;
                        margin: 10px;
                        font-size: 16px;
                    }}
                    .btn:hover {{ background: #0056b3; }}
                    .btn-success {{ background: #28a745; }}
                    .btn-success:hover {{ background: #218838; }}
                    .btn-secondary {{ background: #6c757d; }}
                    .btn-secondary:hover {{ background: #5a6268; }}
                    .json-data {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        font-family: monospace;
                        font-size: 12px;
                        text-align: left;
                        word-break: break-all;
                        margin-top: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Nova Inscripció Creada!</h1>
                    
                    <div class="info">
                        <h3>📋 Dades de la Inscripció:</h3>
                        <strong>Nom:</strong> {inscripcio.get_nom_complet()}<br>
                        <strong>Email:</strong> {inscripcio.email}<br>
                        <strong>Col·lectiu:</strong> {inscripcio.get_collectiu_display()}<br>
                        <strong>Telèfon:</strong> {inscripcio.telefon}<br>
                        <strong>ID:</strong> {inscripcio.getId()}<br>
                        <strong>UID:</strong> {inscripcio.UID()}<br>
                        <strong>Assistit:</strong> {'Sí' if getattr(inscripcio, 'ha_assistit', False) else 'No'}
                    </div>
                    
                    <div class="qr-container">
                        <h3>📱 QR per Escanejar</h3>
                        <img src="data:image/png;base64,{qr_image_base64}" 
                             alt="Codi QR" class="qr-image">
                        <p><em>Escaneja aquest QR per registrar assistència</em></p>
                        
                        <div class="json-data">
                            <strong>Dades del QR:</strong><br>
                            {json.dumps(qr_data, indent=2, ensure_ascii=False)}
                        </div>
                    </div>
                    
                    <a href="{self.context.absolute_url()}/@@qr_scanner_final" class="btn btn-success">
                        📷 Anar a l'Escàner
                    </a>
                    
                    <a href="{self.context.absolute_url()}/@@crear_inscripcio_test" class="btn">
                        ➕ Crear Altra Inscripció
                    </a>
                    
                    <a href="{self.context.absolute_url()}/@@assistencia_llistat" class="btn btn-secondary">
                        📊 Veure Llistat
                    </a>
                    
                    <br>
                    <a href="{self.context.absolute_url()}" class="btn btn-secondary">← Tornar a l'Activitat</a>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            return f"""
            <html>
            <body>
                <h1>❌ Error</h1>
                <p>Error creant inscripció: {str(e)}</p>
                <a href="{self.context.absolute_url()}">← Tornar</a>
            </body>
            </html>
            """