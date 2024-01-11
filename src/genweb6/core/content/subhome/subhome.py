# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexteritySchema
from plone.supermodel import model


class ISubhome(model.Schema, IDexteritySchema):
    """
        Tipus Subhome page: en qualsevol lloc es podra afegir una vista
        similar a la homepage que vol emular el comportament del collage
    """
    pass
