# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from PyPDF2 import PdfReader

from datetime import datetime
from io import BytesIO
from plone import api
from plone.registry.interfaces import IRegistry
from zipfile import ZipFile
from zope.component import getUtility
from zope.publisher.browser import BrowserView

from genweb6.core.browser.clean_pdfs import is_signed_pdf
from genweb6.core.controlpanels.netejar_metadades import IMetadadesSettings
from genweb6.core.indicators.client import Client

import io
import logging
import requests

logger = logging.getLogger(__name__)


class NetejarMetadadesView(BrowserView):
    template = ViewPageTemplateFile("views_templates/netejar_metadades.pt")

    def canView(self):
        if api.user.is_anonymous():
            return False

        username = api.user.get_current().id

        if username == 'admin':
            return True

        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Manager' in roles:
            return True

        if not bool([group.id for group in api.group.get_groups(username=username) if group.id in ['PDI', 'PAS']]):
            return False

        return True

    def __call__(self):
        if not self.canView():
            return Unauthorized

        request = self.request

        if request.method == "POST" and 'pdf_file' in request.form:
            file_uploads = request.form.get('pdf_file')
            if not isinstance(file_uploads, list):
                file_uploads = [file_uploads]

            cleaned_count = 0
            zip_buffer = BytesIO()

            try:
                registry = getUtility(IRegistry)
                settings = registry.forInterface(IMetadadesSettings, check=False)

                api_url = settings.api_url
                api_key = settings.api_key

                headers = {
                    'accept': 'application/json;charset=utf-8', 
                    'X-Api-Key': api_key
                    }

                indicador_client = Client(
                    url_base=settings.indicadors_api_url,
                    api_key=settings.indicadors_api_key
                )

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
                            zip_file.writestr(f"{filename}_SIGNAT.txt", "PDF signat")
                            continue

                        files = {'fitxerPerNetejarMetadades': (filename, BytesIO(content), 'application/pdf')}
                        response = requests.post(api_url, headers=headers, files=files, timeout=90)

                        logger.info(f"Resposta API status: {response.status_code}")
                        logger.info(f"INFO: {filename} net de metadades")

                        if response.status_code == 200:
                            name_part, ext_part = filename.rsplit('.', 1)
                            anon_name = f"{name_part}_sense_metadades.{ext_part}"
                            zip_file.writestr(anon_name, response.content)
                            cleaned_count += 1
                        else:
                            error_msg = f"{filename} - Error {response.status_code}: {response.text}"
                            logger.error(error_msg)
                            zip_file.writestr(f"{filename}_ERROR.txt", error_msg)

                if cleaned_count > 0:
                    try:
                        categories = indicador_client.list_categories(
                            service_id=settings.indicadors_servei_id,
                            indicator_id=settings.indicadors_categoria_id
                        )
                        if categories:
                            categoria = categories[0]
                            pdfs_count = int(categoria.value or 0) + cleaned_count

                            indicador_client.update_category(
                                service_id=settings.indicadors_servei_id,
                                indicator_id=settings.indicadors_categoria_id,
                                category_id=categoria.identifier,
                                category_description=categoria.description,
                                category_type=categoria.type,
                                category_frequency=categoria.frequency,
                                category_value=pdfs_count
                            )
                            logger.info(f"Indicador actualitzat a {pdfs_count}")
                    except Exception as e:
                        logger.exception("Error a l'actualitzar l'indicador")

                request.response.setHeader('Content-Type', 'application/zip')
                request.response.setHeader(
                    'Content-Disposition', 'attachment; filename="pdfs_sense_metadades.zip"'
                )
                request.response.setHeader('Content-Length', str(len(zip_buffer.getvalue())))
                return zip_buffer.getvalue()

            except Exception as e:
                logger.exception("Error al netejar metadades de múltiples PDFs")
                return f"<p><strong>Excepció:</strong> {str(e)}</p>"

        return self.template()
