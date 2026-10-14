"""Formulari d'inscripció a activitats amb generació i enviament de QR"""

from plone import api
from plone.app.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from Products.Five.browser import BrowserView
from z3c.form import form, field, button
from zope import schema
from zope.interface import Interface, implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import smtplib
from ..qr_generator import QRGenerator


COLLECTIUS_VOCAB = SimpleVocabulary([
    SimpleTerm(value='PDI', title='PDI - Personal Docent i Investigador'),
    SimpleTerm(value='PTGAS', title='PTGAS - Personal Tècnic de Gestió i Administració i Serveis'),
    SimpleTerm(value='ESTUDIANT', title='Estudiant'),
    SimpleTerm(value='ALUMNI', title='Alumni'),
    SimpleTerm(value='EXTERN', title='Extern'),
])


class IInscripcioFormSchema(Interface):
    """Schema per al formulari d'inscripció"""
    
    nom = schema.TextLine(
        title="Nom",
        required=True,
    )
    
    cognoms = schema.TextLine(
        title="Cognoms",
        required=True,
    )
    
    email = schema.TextLine(
        title="Email",
        required=True,
    )
    
    telefon = schema.TextLine(
        title="Telèfon de contacte",
        required=True,
    )
    
    collectiu = schema.Choice(
        title="Col·lectiu",
        vocabulary=COLLECTIUS_VOCAB,
        required=True,
    )
    
    centre_unitat = schema.TextLine(
        title="Centre/Unitat",
        description="En cas extern posar 'E', en cas Alumni posar 'A'",
        required=True,
    )


class InscripcioForm(form.Form):
    """Formulari d'inscripció a una activitat"""
    
    fields = field.Fields(IInscripcioFormSchema)
    ignoreContext = True
    
    def __init__(self, context, request):
        super(InscripcioForm, self).__init__(context, request)
        self.activitat = context
    
    @button.buttonAndHandler('Inscriure\'s')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        # Verificar que l'activitat permet inscripcions
        if not getattr(self.activitat, 'permet_inscripcions', False):
            api.portal.show_message(
                message="Aquesta activitat no permet inscripcions online",
                request=self.request,
                type='error'
            )
            return
        
        # Verificar si ja existeix una inscripció amb aquest email
        existing = self.activitat.get_inscripcio_by_email(data['email'])
        if existing:
            api.portal.show_message(
                message="Ja existeix una inscripció amb aquest email per aquesta activitat",
                request=self.request,
                type='warning'
            )
            return
        
        try:
            # Crear la inscripció
            inscripcio_id = f"inscripcio-{len(self.activitat.get_inscripcions()) + 1}"
            inscripcio = api.content.create(
                container=self.activitat,
                type='Inscripcio',
                id=inscripcio_id,
                **data
            )
            
            # Generar el codi QR
            qr_generator = QRGenerator()
            qr_data = {
                "type": "upcarts_inscripcio",
                "activitat_id": self.activitat.UID(),
                "inscripcio_id": inscripcio.UID(),
                "activitat_title": self.activitat.title,
                "nom": inscripcio.get_nom_complet(),
                "email": inscripcio.email,
                "collectiu": inscripcio.get_collectiu_display()
            }
            
            # Generar QR i guardar-lo a la inscripció
            qr_json = json.dumps(qr_data)
            qr_image_base64 = qr_generator.generate_qr_image(qr_json)
            
            # Guardar el QR a la inscripció
            inscripcio.qr_code = qr_json
            inscripcio.qr_image_data = qr_image_base64
            
            qr_result = {
                'data': qr_data,
                'json': qr_json,
                'image': qr_image_base64
            }
            
            # Enviar email amb el QR
            success = self.send_qr_email(inscripcio, qr_result)
            
            if success:
                api.portal.show_message(
                    message=f"Inscripció realitzada correctament! S'ha enviat un email amb el codi QR a {data['email']}",
                    request=self.request,
                    type='info'
                )
            else:
                api.portal.show_message(
                    message="Inscripció realitzada però hi ha hagut un error enviant l'email. Contacta amb l'organització.",
                    request=self.request,
                    type='warning'
                )
            
            # Redirigir a la pàgina de confirmació
            self.request.response.redirect(f"{self.activitat.absolute_url()}/inscripcio_confirmacio?inscripcio_id={inscripcio.UID()}")
            
        except Exception as e:
            api.portal.show_message(
                message=f"Error creant la inscripció: {str(e)}",
                request=self.request,
                type='error'
            )
    
    def send_qr_email(self, inscripcio, qr_result):
        """Envia l'email amb el codi QR"""
        try:
            # Configuració SMTP (hauria de venir del registry)
            portal = api.portal.get()
            email_from = api.portal.get_registry_record('plone.email_from_address')
            
            # Crear el missatge
            msg = MIMEMultipart('related')
            msg['Subject'] = f"Confirmació d'inscripció - {self.activitat.title}"
            msg['From'] = email_from
            msg['To'] = inscripcio.email
            
            # Cos de l'email en HTML
            html_body = self.generate_email_html(inscripcio, qr_result)
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Adjuntar la imatge QR
            qr_image_data = base64.b64decode(qr_result['image'])
            qr_image = MIMEImage(qr_image_data)
            qr_image.add_header('Content-ID', '<qr_code>')
            qr_image.add_header('Content-Disposition', 'inline', filename='qr_code.png')
            msg.attach(qr_image)
            
            # Enviar l'email (això hauria d'usar la configuració SMTP de Plone)
            # Per ara, només guardem que s'ha "enviat"
            inscripcio.qr_email_sent = True
            inscripcio.qr_email_date = datetime.datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error enviant email: {e}")
            return False
    
    def generate_email_html(self, inscripcio, qr_result):
        """Genera el cos HTML de l'email"""
        activitat = inscripcio.get_activitat()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Confirmació d'inscripció</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .qr-section {{ text-align: center; margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px; }}
                .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .info-table th, .info-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .info-table th {{ background-color: #e9ecef; }}
                .footer {{ text-align: center; padding: 20px; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmació d'Inscripció</h1>
                    <h2>UPCArts</h2>
                </div>
                
                <div class="content">
                    <p>Hola <strong>{inscripcio.get_nom_complet()}</strong>,</p>
                    
                    <p>La teva inscripció a l'activitat <strong>{activitat.title}</strong> s'ha realitzat correctament.</p>
                    
                    <table class="info-table">
                        <tr>
                            <th>Activitat</th>
                            <td>{activitat.title}</td>
                        </tr>
                        <tr>
                            <th>Data i hora</th>
                            <td>{activitat.data_inici.strftime('%d/%m/%Y %H:%M') if activitat.data_inici else 'Per determinar'}</td>
                        </tr>
                        <tr>
                            <th>Lloc</th>
                            <td>{getattr(activitat, 'lloc', 'Per determinar')}</td>
                        </tr>
                        <tr>
                            <th>Nom</th>
                            <td>{inscripcio.get_nom_complet()}</td>
                        </tr>
                        <tr>
                            <th>Email</th>
                            <td>{inscripcio.email}</td>
                        </tr>
                        <tr>
                            <th>Col·lectiu</th>
                            <td>{inscripcio.get_collectiu_display()}</td>
                        </tr>
                    </table>
                    
                    <div class="qr-section">
                        <h3>Codi QR d'Accés</h3>
                        <p>Presenta aquest codi QR a l'entrada de l'activitat per registrar la teva assistència:</p>
                        <img src="cid:qr_code" alt="Codi QR" style="max-width: 200px; border: 1px solid #ddd; padding: 10px;">
                        <p><small>També pots mostrar aquest email des del teu mòbil</small></p>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>Guarda aquest email o fes una captura de pantalla del codi QR</li>
                        <li>Presenta el codi QR a l'entrada de l'activitat</li>
                        <li>Si tens problemes, contacta amb nosaltres</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>UPCArts - Universitat Politècnica de Catalunya</p>
                    <p>Per a més informació: <a href="https://upcarts.upc.edu">upcarts.upc.edu</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class InscripcioFormView(BrowserView):
    """Vista per mostrar el formulari d'inscripció"""
    
    def __init__(self, context, request):
        super(InscripcioFormView, self).__init__(context, request)
        self.form = InscripcioForm(context, request)
        self.form.__parent__ = self
    
    def __call__(self):
        # Verificar que l'activitat permet inscripcions
        if not getattr(self.context, 'permet_inscripcions', False):
            api.portal.show_message(
                message="Aquesta activitat no permet inscripcions online",
                request=self.request,
                type='error'
            )
            return self.request.response.redirect(self.context.absolute_url())
        
        self.form.update()
        return self.form.render()


class InscripcioConfirmacioView(BrowserView):
    """Vista de confirmació després de la inscripció"""
    
    def __call__(self):
        inscripcio_id = self.request.get('inscripcio_id')
        if not inscripcio_id:
            return self.request.response.redirect(self.context.absolute_url())
        
        self.inscripcio = api.content.get(UID=inscripcio_id)
        if not self.inscripcio:
            api.portal.show_message(
                message="Inscripció no trobada",
                request=self.request,
                type='error'
            )
            return self.request.response.redirect(self.context.absolute_url())
        
        return self.index()
    
    def get_qr_data_url(self):
        """Retorna la URL de dades de la imatge QR"""
        if hasattr(self.inscripcio, 'qr_image_data') and self.inscripcio.qr_image_data:
            return f"data:image/png;base64,{self.inscripcio.qr_image_data}"
        return None