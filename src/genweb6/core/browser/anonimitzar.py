from zope.interface import Interface
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from genweb6.core.controlpanels.anonimitzar import IAnonimitzarSettings 

import requests
from plone import api
import logging

logger = logging.getLogger(__name__)

class AnonimitzarView(BrowserView):
    template = ViewPageTemplateFile("views_templates/anonimitzar.pt")

    def __call__(self):
        request = self.request

        if request.method == "POST" and 'pdf_file' in request.form:
            file_upload = request.form['pdf_file']

            if not file_upload or not getattr(file_upload, 'filename', '').lower().endswith('.pdf'):
                return "<p><strong>Error:</strong> Has de pujar un arxiu PDF vàlid.</p>"

            try:
                files = {
                    'fitxerPerAnonimitzar': (
                        file_upload.filename,
                        file_upload,
                        'application/pdf'
                    )
                }
                registry = getUtility(IRegistry)
                settings = registry.forInterface(IAnonimitzarSettings, check=False)

                api_url = settings.api_url
                api_key = settings.api_key

                headers = {
                    'accept': 'application/json;charset=utf-8',
                    'X-Api-Key': api_key
                }

                response = requests.post(
                    api_url,
                    headers=headers,
                    files=files
                )

                if response.status_code == 200:
                    content_disposition = response.headers.get("Content-Disposition", "")

                    original_filename = file_upload.filename

                    if "filename=" in content_disposition:
                        original_filename = content_disposition.split("filename=")[1].strip('"')

                    if '.' in original_filename:
                        name_part = original_filename.rsplit('.', 1)[0]
                        ext_part = original_filename.rsplit('.', 1)[1]
                    else:
                        name_part = original_filename
                        ext_part = 'pdf'

                    filename = f"{name_part}_anonimitzat.{ext_part}"

                    request.response.setHeader('Content-Type', 'application/pdf')
                    request.response.setHeader(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    request.response.setHeader('Content-Length', str(len(response.content)))
                    return response.content

                else:
                    return f"<p><strong>Error:</strong> Codi {response.status_code} - {response.text}</p>"

            except Exception as e:
                logger.exception("Error al enviar PDF per anonimitzar")
                return f"<p><strong>Excepció:</strong> {str(e)}</p>"

        return self.template()
