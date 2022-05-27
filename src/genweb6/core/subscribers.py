# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

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
        IStatusMessage(content.request).addStatusMessage(u'Cannot delete protected content.', type='error')
        raise(Unauthorized, u'Cannot delete protected content.')
    else:
        return


def preventMovedOnProtectedContent(content, event):
    """ Community added handler
    """
    try:
        api.portal.get()
    except:
        # Most probably we are on Zope root and trying to moved or renamed an entire Plone
        # Site so grant it unconditionally
        return

    # Only (global) site managers can moved or renamed packet content from root folder

    if 'Manager' not in api.user.get_roles():
        IStatusMessage(content.request).addStatusMessage(u'Cannot moved or renamed protected content.', type='error')
        raise(Unauthorized, u'Cannot moved or renamed protected content.')
    else:
        return


def addedPermissionsPloneSiteRoot(content, event):
    # sender_email = api.portal.get_registry_record('plone.email_from_address')
    # sender_name = api.portal.get_registry_record('plone.email_from_name').encode('utf-8')
    email_charset = api.portal.get_registry_record('plone.email_charset')
    # fromMsg = sender_name + ' ' + '<' + sender_email + '>'
    fromMsg = 'gestio.genweb@upc.edu'

    serverid = socket.gethostname()
    mountpoint = '/'.join(content.getPhysicalPath())
    plone = content.absolute_url()

    # TODO Enviar correo para abrir tiquet
    mailhost = api.portal.get_tool(name='MailHost')
    msg = MIMEMultipart()
    msg['From'] = fromMsg
    msg['To'] = 'mailtoticket.areatic@upc.edu'
    msg['Subject'] = escape(safe_unicode('Recatalogar el genweb ' + plone))
    msg['charset'] = email_charset

    message = "Màquina: " + serverid + "\nMontpoint: " + mountpoint + "\nURL: " + plone

    msg.attach(MIMEText(message, 'plain', email_charset))
    mailhost.send(msg)
