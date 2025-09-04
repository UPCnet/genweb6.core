# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from genweb6.core.controlpanels.netejar_metadades import IMetadadesSettings
import requests
from plone import api
import logging
from zipfile import ZipFile
import io
from io import BytesIO
from datetime import datetime
from PyPDF2 import PdfReader
from genweb6.core.browser.clean_pdfs import is_signed_pdf

logger = logging.getLogger(__name__)


class NetejarMetadadesView(BrowserView):
    template = ViewPageTemplateFile("views_templates/netejar_metadades.pt")

    def __call__(self):
        request = self.request

        if request.method == "POST" and 'pdf_file' in request.form:
            file_uploads = request.form.get('pdf_file')

            if not isinstance(file_uploads, list):
                file_uploads = [file_uploads]

            try:
                registry = getUtility(IRegistry)
                settings = registry.forInterface(IMetadadesSettings, check=False)

                api_url = settings.api_url
                api_key = settings.api_key

                headers = {
                    'accept': 'application/json;charset=utf-8',
                    'X-Api-Key': api_key
                }

                zip_buffer = io.BytesIO()
                cleaned_count = 0

                with ZipFile(zip_buffer, 'w') as zip_file:
                    for file_upload in file_uploads:
                        filename = file_upload.filename
                        if not filename.lower().endswith('.pdf'):
                            logger.info(f"Se salta archivo no PDF: {filename}")
                            continue

                        file_upload.seek(0)
                        content = file_upload.read()

                        if not content:
                            logger.warning(f"Archivo vacío: {filename}")
                            continue

                        if is_signed_pdf(content):
                            logger.info(f"PDF signat, no és possible eliminar les metadades: {filename}")
                            zip_file.writestr(f"{filename}SIGNAT.txt", "PDF signat")
                            continue

                        file_obj = BytesIO(content)
                        file_obj.name = filename  

                        files = {
                            'fitxerPerNetejarMetadades': (
                                filename,
                                file_obj,
                                'application/pdf'
                            )
                        }

                        # POST individual para cada PDF
                        response = requests.post(api_url, headers=headers, files=files, timeout=90)

                        # logger.info(f"Tamaño original: {len(content)} bytes, limpio: {len(response.content)} bytes para {filename}")
                        logger.info(f"Resposta API status: {response.status_code}")
                        logger.info(f"INFO: {filename} net de metadades")

                        if response.status_code == 200:
                            name_part, ext_part = filename.rsplit('.', 1)
                            anon_name = f"{name_part}_anonimitzat.{ext_part}"
                            zip_file.writestr(anon_name, response.content)
                            site = api.portal.get() 
                            cleaned_count += 1
                            error_msg = f"{filename} - Error {response.status_code}: {response.text}"
                            logger.error(error_msg)
                            zip_file.writestr(f"{filename}_ERROR.txt", error_msg)

                request.response.setHeader('Content-Type', 'application/zip')
                request.response.setHeader('Content-Disposition', 'attachment; filename="pdfs_anonimitzats.zip"')
                request.response.setHeader('Content-Length', str(len(zip_buffer.getvalue())))
                return zip_buffer.getvalue()

            except Exception as e:
                logger.exception("Error al netejar metadades de múltiples PDFs")
                return f"<p><strong>Excepció:</strong> {str(e)}</p>"

        return self.template()
