# -*- coding: utf-8 -*-
import socket
from plone import api
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

from plone.namedfile.file import NamedBlobFile

from genweb6.core.utils import genwebMetadadesConfig

import logging
import requests
from io import BytesIO
from PyPDF2 import PdfReader
import time

logger = logging.getLogger(__name__)


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
        IStatusMessage(content.request).addStatusMessage(
            u'Cannot delete protected content.', type='error')
        raise (Unauthorized, u'Cannot delete protected content.')
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
        IStatusMessage(content.request).addStatusMessage(
            u'Cannot moved or renamed protected content.', type='error')
        raise (Unauthorized, u'Cannot moved or renamed protected content.')
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


def updateLastLoginTimeAfterLogin(event):
    """
    Update last login time in memberdata tool after login

    Args:
        event (Products.PlonePAS.events.UserLoggedInEvent):
            Plone Implementation of the logged in event
    """
    pmd = api.portal.get_tool(name='portal_memberdata')
    users_last_login = event.object.getProperty('last_login_time', None)
    if users_last_login:
        pmd.last_login_time = users_last_login


def is_signed_pdf(data):
    try:
        reader = PdfReader(BytesIO(data))
        if '/AcroForm' in reader.trailer['/Root']:
            acroform = reader.trailer['/Root']['/AcroForm']
            if '/Fields' in acroform:
                for field in acroform['/Fields']:
                    field_obj = field.get_object()
                    if field_obj.get('/FT') == '/Sig':
                        return True
        return False
    except Exception as e:
        logger.warning(f"Error analizando firma en PDF: {e}")
        return False


def clean_pdf_on_upload_file(obj, event):
    clean_pdf_on_upload(obj, 'file')


def clean_pdf_on_upload(obj, field_name='file'):
    """Subscriber que limpia el PDF al subirlo si no está firmado.

    Args:
        obj: El objeto que contiene el archivo
        field_name: Nombre del campo que contiene el archivo (por defecto 'file')
    """
    file_field = getattr(obj, field_name, None)
    if not file_field:
        return

    if not file_field.filename.lower().endswith('.pdf'):
        return

    settings = genwebMetadadesConfig()

    api_url = settings.api_url
    api_key = settings.api_key

    if not api_url or not api_key:
        return

    file_data = file_field.data

    start_time_check_signed = time.time()
    if is_signed_pdf(file_data):
        logger.info(f"[SKIPPED] {obj.absolute_url()} - PDF signat")
        return

    end_time_check_signed = time.time()
    time_check_signed = end_time_check_signed - start_time_check_signed
    logger.error(f"[GW6 METADADAS CHECK SIGNED] {obj.absolute_url()} - Tiempo de verificación de firma: {time_check_signed} segundos")

    try:
        headers = {
            'accept': 'application/json;charset=utf-8',
            'X-Api-Key': api_key
        }

        filename = file_field.filename
        files = {
            'fitxerPerNetejarMetadades': (filename, file_data, 'application/pdf')
        }

        start_time_clean_pdf = time.time()

        response = requests.post(api_url, headers=headers, files=files)

        end_time_clean_pdf = time.time()
        time_clean_pdf = end_time_clean_pdf - start_time_clean_pdf
        logger.error(f"[GW6 METADADAS CLEAN PDF] {obj.absolute_url()} - Tiempo de limpieza de PDF: {time_clean_pdf} segundos")

        if response.status_code == 200:
            cleaned_data = response.content

            setattr(obj, field_name, NamedBlobFile(
                data=cleaned_data,
                contentType='application/pdf',
                filename=filename
            ))

            obj.reindexObject()
            logger.info(f"[OK] {obj.absolute_url()} - PDF sense metadades")
        else:
            logger.warning(
                f"[FAIL] {obj.absolute_url()} - {response.status_code} - {response.text}")

    except Exception as e:
        logger.exception(f"[ERROR] {obj.absolute_url()} - {e}")
