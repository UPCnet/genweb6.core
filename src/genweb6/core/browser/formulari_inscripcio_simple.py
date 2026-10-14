"""Formulari d'inscripció simple amb generació automàtica de QR"""

from Products.Five.browser import BrowserView
from plone import api
from ..qr_generator import QRGenerator
import json
import datetime


class FormulariInscripcioSimpleView(BrowserView):
    """Formulari d'inscripció simple"""
    
    def __call__(self):
        """Mostra el formulari o processa la inscripció"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        if self.request.method == 'POST':
            return self.processar_inscripcio()
        else:
            return self.mostrar_formulari()
    
    def mostrar_formulari(self):
        """Mostra el formulari d'inscripció"""
        
        # Verificar que l'activitat permet inscripcions
        if not getattr(self.context, 'permet_inscripcions', False):
            return f"""
            <html>
            <body>
                <h1>❌ Inscripcions Tancades</h1>
                <p>Aquesta activitat no permet inscripcions online.</p>
                <a href="{self.context.absolute_url()}">← Tornar a l'activitat</a>
            </body>
            </html>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📝 Inscripció - {self.context.title}</title>
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
                }}
                h1 {{ color: #007bff; text-align: center; }}
                .activitat-info {{
                    background: #e9ecef;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .form-group {{
                    margin: 20px 0;
                }}
                label {{
                    display: block;
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #495057;
                }}
                input, select, textarea {{
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ced4da;
                    border-radius: 5px;
                    font-size: 16px;
                    box-sizing: border-box;
                }}
                input:focus, select:focus, textarea:focus {{
                    border-color: #007bff;
                    outline: none;
                    box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
                }}
                .required {{
                    color: #dc3545;
                }}
                .btn {{
                    background: #007bff;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 18px;
                    width: 100%;
                    margin-top: 20px;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn-secondary {{
                    background: #6c757d;
                    margin-top: 10px;
                }}
                .btn-secondary:hover {{ background: #5a6268; }}
                .help-text {{
                    font-size: 14px;
                    color: #6c757d;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📝 Formulari d'Inscripció</h1>
                
                <div class="activitat-info">
                    <h3>{self.context.title}</h3>
                    <p><strong>Data:</strong> {self.context.data_inici.strftime('%d/%m/%Y %H:%M') if getattr(self.context, 'data_inici', None) else 'Per determinar'}</p>
                    <p><strong>Lloc:</strong> {getattr(self.context, 'lloc', 'Per determinar')}</p>
                    {f'<p><strong>Preu:</strong> {self.context.preu}€</p>' if getattr(self.context, 'preu', 0) > 0 else '<p><strong>Preu:</strong> Gratuït</p>'}
                </div>
                
                <form method="post" action="{self.context.absolute_url()}/@@formulari_inscripcio">
                    <div class="form-group">
                        <label for="nom">Nom <span class="required">*</span></label>
                        <input type="text" id="nom" name="nom" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="cognoms">Cognoms <span class="required">*</span></label>
                        <input type="text" id="cognoms" name="cognoms" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email <span class="required">*</span></label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="telefon">Telèfon de contacte <span class="required">*</span></label>
                        <input type="tel" id="telefon" name="telefon" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="collectiu">Col·lectiu <span class="required">*</span></label>
                        <select id="collectiu" name="collectiu" required>
                            <option value="">Selecciona el teu col·lectiu</option>
                            <option value="PDI">PDI - Personal Docent i Investigador</option>
                            <option value="PTGAS">PTGAS - Personal Tècnic de Gestió i Administració i Serveis</option>
                            <option value="ESTUDIANT">Estudiant</option>
                            <option value="ALUMNI">Alumni</option>
                            <option value="EXTERN">Extern</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="centre_unitat">Centre/Unitat <span class="required">*</span></label>
                        <input type="text" id="centre_unitat" name="centre_unitat" required>
                        <div class="help-text">En cas extern posar 'E', en cas Alumni posar 'A'</div>
                    </div>
                    
                    <button type="submit" class="btn">📝 Inscriure's</button>
                    <a href="{self.context.absolute_url()}" class="btn btn-secondary" style="text-decoration: none; display: block; text-align: center;">← Tornar a l'activitat</a>
                </form>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def processar_inscripcio(self):
        """Processa la inscripció i genera el QR"""
        
        try:
            # Obtenir dades del formulari
            data = {
                'nom': self.request.get('nom', '').strip(),
                'cognoms': self.request.get('cognoms', '').strip(),
                'email': self.request.get('email', '').strip(),
                'telefon': self.request.get('telefon', '').strip(),
                'collectiu': self.request.get('collectiu', ''),
                'centre_unitat': self.request.get('centre_unitat', '').strip(),
            }
            
            # Validar dades
            errors = []
            if not data['nom']:
                errors.append('El nom és obligatori')
            if not data['cognoms']:
                errors.append('Els cognoms són obligatoris')
            if not data['email']:
                errors.append('L\'email és obligatori')
            if not data['telefon']:
                errors.append('El telèfon és obligatori')
            if not data['collectiu']:
                errors.append('El col·lectiu és obligatori')
            if not data['centre_unitat']:
                errors.append('El centre/unitat és obligatori')
            
            if errors:
                return self.mostrar_error(errors)
            
            # Verificar que l'activitat permet inscripcions
            if not getattr(self.context, 'permet_inscripcions', False):
                return self.mostrar_error(['Aquesta activitat no permet inscripcions online'])
            
            # Verificar si ja existeix una inscripció amb aquest email
            inscripcions_existents = self.context.listFolderContents(
                contentFilter={'portal_type': 'Inscripcio'}
            )
            for inscripcio in inscripcions_existents:
                if inscripcio.email.lower() == data['email'].lower():
                    return self.mostrar_error(['Ja existeix una inscripció amb aquest email per aquesta activitat'])
            
            # Crear la inscripció
            import time
            timestamp = str(int(time.time()))
            inscripcio_id = f"inscripcio-{timestamp}"
            
            inscripcio = api.content.create(
                container=self.context,
                type='Inscripcio',
                id=inscripcio_id,
                title=f'Inscripció - {data["nom"]} {data["cognoms"]}',
                **data
            )
            
            # Generar el QR automàticament
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
            
            # Generar QR i guardar-lo a la inscripció
            qr_json = json.dumps(qr_data)
            qr_image_base64 = qr_generator.generate_qr_image(qr_json)
            
            # Guardar el QR als camps de la inscripció
            inscripcio.qr_code = qr_json
            inscripcio.qr_image_data = qr_image_base64
            
            # Guardar canvis
            inscripcio.reindexObject()
            
            # Mostrar pàgina de confirmació amb QR
            return self.mostrar_confirmacio(inscripcio, qr_data, qr_image_base64)
            
        except Exception as e:
            return self.mostrar_error([f'Error processant la inscripció: {str(e)}'])
    
    def mostrar_error(self, errors):
        """Mostra una pàgina d'error"""
        
        errors_html = '<br>'.join([f'• {error}' for error in errors])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>❌ Error d'Inscripció</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; border: 1px solid #f5c6cb; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Error d'Inscripció</h1>
                <div class="error">
                    <h3>S'han trobat els següents errors:</h3>
                    <p>{errors_html}</p>
                </div>
                <a href="{self.context.absolute_url()}/@@formulari_inscripcio" class="btn">← Tornar al formulari</a>
            </div>
        </body>
        </html>
        """
    
    def mostrar_confirmacio(self, inscripcio, qr_data, qr_image_base64):
        """Mostra la pàgina de confirmació amb el QR"""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>✅ Inscripció Confirmada</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    margin: 0;
                    background: #f8f9fa;
                }}
                .container {{ 
                    max-width: 700px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                h1 {{ color: #28a745; }}
                .success-info {{
                    background: #d4edda;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    text-align: left;
                    border: 1px solid #c3e6cb;
                }}
                .qr-container {{
                    margin: 30px 0;
                    padding: 30px;
                    background: #f8f9fa;
                    border-radius: 15px;
                    border: 3px dashed #007bff;
                }}
                .qr-image {{
                    max-width: 300px;
                    margin: 20px auto;
                    display: block;
                    border: 3px solid #007bff;
                    border-radius: 10px;
                    padding: 15px;
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
                .instructions {{
                    background: #fff3cd;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border: 1px solid #ffeaa7;
                }}
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
                <h1>✅ Inscripció Confirmada!</h1>
                
                <div class="success-info">
                    <h3>📋 Dades de la teva inscripció:</h3>
                    <strong>Activitat:</strong> {self.context.title}<br>
                    <strong>Nom:</strong> {inscripcio.get_nom_complet()}<br>
                    <strong>Email:</strong> {inscripcio.email}<br>
                    <strong>Col·lectiu:</strong> {inscripcio.get_collectiu_display()}<br>
                    <strong>Data inscripció:</strong> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
                    <strong>ID Inscripció:</strong> {inscripcio.getId()}
                </div>
                
                <div class="qr-container">
                    <h3>📱 El teu Codi QR</h3>
                    <p><strong>Guarda aquest QR per registrar la teva assistència!</strong></p>
                    
                    <img src="data:image/png;base64,{qr_image_base64}" 
                         alt="Codi QR d'assistència" class="qr-image">
                    
                    <div class="instructions">
                        <h4>📋 Instruccions:</h4>
                        <ul style="text-align: left;">
                            <li><strong>Guarda aquest QR</strong> fent una captura de pantalla</li>
                            <li><strong>Porta'l el dia de l'activitat</strong> al teu mòbil</li>
                            <li><strong>Presenta'l a l'entrada</strong> per registrar assistència</li>
                            <li>També pots accedir a la teva inscripció des del web</li>
                        </ul>
                    </div>
                    
                    <div class="json-data">
                        <strong>Dades del QR:</strong><br>
                        {json.dumps(qr_data, indent=2, ensure_ascii=False)}
                    </div>
                </div>
                
                <a href="{self.context.absolute_url()}/@@qr_scanner_final" class="btn btn-success">
                    📷 Provar Escàner (Test)
                </a>
                
                <a href="{inscripcio.absolute_url()}" class="btn">
                    👤 Veure la meva Inscripció
                </a>
                
                <a href="{self.context.absolute_url()}/@@assistencia_llistat" class="btn btn-secondary">
                    📊 Llistat d'Assistència
                </a>
                
                <br>
                <a href="{self.context.absolute_url()}" class="btn btn-secondary">← Tornar a l'Activitat</a>
            </div>
        </body>
        </html>
        """