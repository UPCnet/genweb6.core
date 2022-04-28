# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from plone import api

import socket


def preventDeletionOnProtectedContent(content, event):
    """ Community added handler
    """
    try:
        api.portal.get()
    except:
        # Most probably we are on Zope root and trying to delete an entire Plone
        # Site so grant it unconditionally
        return

    # Only (global) site managers can delete packet content from root folder

    if 'Manager' not in api.user.get_roles():
        raise(Unauthorized, u'Cannot delete protected content.')
    else:
        return


def addedPermissionsPloneSiteRoot(content, event):
    portal = api.portal.get()
    # sender_email = portal.getProperty('email_from_address')
    # sender_name = portal.getProperty('email_from_name').encode('utf-8')
    email_charset = portal.getProperty('email_charset')
    # fromMsg = sender_name + ' ' + '<' + sender_email + '>'
    fromMsg = 'gestio.genweb@upc.edu'

    serverid = socket.gethostname()
    mountpoint = '/'.join(content.getPhysicalPath())
    plone = content.absolute_url()

    # TODO Enviar correo para abrir tiquet
    context = aq_inner(content)
    mailhost = getToolByName(context, 'MailHost')
    msg = MIMEMultipart()
    msg['From'] = fromMsg
    msg['To'] = 'mailtoticket.areatic@upc.edu'
    msg['Subject'] = escape(safe_unicode('Recatalogar el genweb ' + plone))
    msg['charset'] = email_charset

    message = "Màquina: " + serverid + "\nMontpoint: " + mountpoint + "\nURL: " + plone

    msg.attach(MIMEText(message, 'plain', email_charset))
    mailhost.send(msg)
