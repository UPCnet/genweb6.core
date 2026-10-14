"""Content type Activitat per UPCArts amb suport per inscripcions i codis QR"""

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('genweb6.core')
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from zope.schema import URI
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.supermodel import model
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
import datetime
import json
from decimal import Decimal


class IActivitat(model.Schema):
    """Schema per al content type Activitat"""
    
    # Els camps title i description els proporciona el behavior plone.basic
    
    text = RichText(
        title=_("Text"),
        required=False,
    )
    
    # Dates i horaris
    data_inici = schema.Datetime(
        title=_("Data i hora d'inici"),
        required=True,
    )
    
    data_fi = schema.Datetime(
        title=_("Data i hora de finalització"),
        required=False,
    )
    
    tot_el_dia = schema.Bool(
        title=_("Tot el dia"),
        required=False,
        default=False,
    )
    
    # Localització
    lloc = schema.TextLine(
        title=_("Lloc de l'activitat"),
        required=False,
    )
    
    responsable = schema.TextLine(
        title=_("Responsable de l'activitat"),
        required=False,
    )
    
    email_contacte = schema.TextLine(
        title=_("Email de contacte"),
        required=False,
    )
    
    telefon_contacte = schema.TextLine(
        title=_("Telèfon de contacte"),
        required=False,
    )
    
    web_info = URI(
        title=_("Web amb més informació"),
        required=False,
    )
    
    # Camps específics per inscripcions
    permet_inscripcions = schema.Bool(
        title=_("Permet inscripcions"),
        description=_("Marca si aquesta activitat permet inscripcions online"),
        default=False,
    )
    
    # Passaport Cultural
    passaport_cultural = schema.Bool(
        title=_("Forma part del Passaport Cultural"),
        description=_("Marca si aquesta activitat forma part del Passaport Cultural"),
        default=False,
    )
    
    hores_passaport = schema.Int(
        title=_("Hores del Passaport Cultural"),
        description=_("Nombre d'hores que representa per al Passaport Cultural"),
        required=False,
        min=0,
    )
    
    # Informació per al QR
    qr_info_extra = schema.Text(
        title=_("Informació extra per al codi QR"),
        description=_("Informació addicional que s'inclourà al codi QR generat"),
        required=False,
    )
    
    # Preu
    preu = schema.Decimal(
        title=_("Preu"),
        description=_("Preu de l'activitat (0 si és gratuïta)"),
        required=False,
        default=Decimal('0'),
    )


@implementer(IActivitat)
class Activitat(Container):
    """Content type Activitat"""
    
    def get_inscripcions(self):
        """Retorna les inscripcions d'aquesta activitat"""
        inscripcions = []
        for obj in self.objectValues():
            if obj.portal_type == 'Inscripcio':
                inscripcions.append(obj)
        return inscripcions
    
    def get_inscripcio_by_email(self, email):
        """Busca una inscripció per email"""
        for inscripcio in self.get_inscripcions():
            if inscripcio.email == email:
                return inscripcio
        return None
    
    def get_assistents(self):
        """Retorna les inscripcions que han assistit"""
        assistents = []
        for inscripcio in self.get_inscripcions():
            if getattr(inscripcio, 'ha_assistit', False):
                assistents.append(inscripcio)
        return assistents
    
    def generate_qr_data(self, inscripcio_id):
        """Genera les dades per al codi QR"""
        data = {
            'activitat_id': self.UID(),
            'inscripcio_id': inscripcio_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'title': self.title,
        }
        
        if self.qr_info_extra:
            data['extra'] = self.qr_info_extra
            
        return json.dumps(data)