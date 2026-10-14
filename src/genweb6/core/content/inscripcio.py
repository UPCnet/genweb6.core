"""Content type Inscripcio per gestionar inscripcions a activitats"""

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('genweb6.core')
from plone.dexterity.content import Item
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.supermodel import model
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
import datetime


COLLECTIUS = [
    ('PDI', 'PDI - Personal Docent i Investigador'),
    ('PTGAS', 'PTGAS - Personal Tècnic de Gestió i Administració i Serveis'),
    ('ESTUDIANT', 'Estudiant'),
    ('ALUMNI', 'Alumni'),
    ('EXTERN', 'Extern'),
]


class IInscripcio(model.Schema):
    """Schema per al content type Inscripcio"""
    
    # Dades personals
    nom = schema.TextLine(
        title=_("Nom"),
        required=True,
    )
    
    cognoms = schema.TextLine(
        title=_("Cognoms"),
        required=True,
    )
    
    email = schema.TextLine(
        title=_("Email"),
        required=True,
    )
    
    telefon = schema.TextLine(
        title=_("Telèfon de contacte"),
        required=True,
    )
    
    # Col·lectiu
    collectiu = schema.Choice(
        title=_("Col·lectiu"),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value=key, title=value)
            for key, value in COLLECTIUS
        ]),
        required=True,
    )
    
    centre_unitat = schema.TextLine(
        title=_("Centre/Unitat"),
        description=_("En cas extern posar 'E', en cas Alumni posar 'A'"),
        required=True,
    )
    
    # Dates de gestió
    data_inscripcio = schema.Datetime(
        title=_("Data d'inscripció"),
        required=True,
        default=datetime.datetime.now(),
    )
    
    # Control d'assistència
    ha_assistit = schema.Bool(
        title=_("Ha assistit"),
        description=_("Marca si la persona ha assistit a l'activitat"),
        default=False,
    )
    
    data_assistencia = schema.Datetime(
        title=_("Data i hora d'assistència"),
        description=_("Moment en què es va registrar l'assistència"),
        required=False,
    )
    
    # Codi QR generat
    qr_code = schema.Text(
        title=_("Codi QR"),
        description=_("Dades del codi QR generat per aquesta inscripció"),
        required=False,
    )
    
    qr_image_data = schema.Text(
        title=_("Imatge QR (base64)"),
        description=_("Dades de la imatge QR en format base64"),
        required=False,
    )


@implementer(IInscripcio)
class Inscripcio(Item):
    """Content type Inscripcio"""
    
    def get_activitat(self):
        """Retorna l'activitat pare"""
        return self.aq_parent
    
    def get_nom_complet(self):
        """Retorna el nom complet"""
        return f"{self.nom} {self.cognoms}"
    
    def marcar_assistencia(self):
        """Marca l'assistència i registra la data"""
        self.ha_assistit = True
        self.data_assistencia = datetime.datetime.now()
    
    def get_collectiu_display(self):
        """Retorna el nom complet del col·lectiu"""
        for key, value in COLLECTIUS:
            if key == self.collectiu:
                return value
        return self.collectiu