from Products.Five import BrowserView
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from genweb6.core.controlpanels.anonimitzar import IAnonimitzarSettings
from plone.namedfile.file import NamedBlobFile  

import requests
import logging
import transaction
from io import BytesIO
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

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


class CleanPDFsView(BrowserView):
    """Vista que recorre tots els arxius PDF i elimina els metadades usant l'API."""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(portal_type='File')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IAnonimitzarSettings, check=False)

        api_url = settings.api_url
        api_key = settings.api_key

        headers = {
            'accept': 'application/json;charset=utf-8',
            'X-Api-Key': api_key
        }

        count_total = 0
        count_cleaned = 0
        count_signed = 0
        errors = []

        for brain in brains:
            obj = brain.getObject()

            # Reparar obj.file si és bytes (cas erroni)
            # if isinstance(obj.file, bytes):
            #     filename = obj.getId() + '.pdf'
            #     obj.file = NamedBlobFile(
            #         data=obj.file,
            #         contentType='application/pdf',
            #         filename=filename
            #     )
            #     obj.reindexObject()

            if not obj.file or not obj.file.filename.lower().endswith('.pdf'):
                continue

            file_data = obj.file.data

            if is_signed_pdf(file_data):
                logger.info(f"[SKIPPED] {obj.absolute_url()} - PDF signat")
                count_signed += 1
                continue

            count_total += 1

            try:
                filename = obj.file.filename

                files = {
                    'fitxerPerAnonimitzar': (filename, file_data, 'application/pdf')
                }

                response = requests.post(api_url, headers=headers, files=files)

                if response.status_code == 200:
                    cleaned_data = response.content

                    obj.file = NamedBlobFile(
                        data=cleaned_data,
                        contentType='application/pdf',
                        filename=filename
                    )

                    obj.reindexObject()
                    count_cleaned += 1
                    logger.info(f"[OK] {obj.absolute_url()}")
                else:
                    errors.append(f"{obj.absolute_url()}: {response.status_code}")
                    logger.warning(f"[FAIL] {obj.absolute_url()} - {response.status_code}")

            except Exception as e:
                errors.append(f"{obj.absolute_url()}: {str(e)}")
                logger.exception(f"[ERROR] {obj.absolute_url()}")

        html = f"""
            <h2>PDF Metadata Cleanup</h2>
            <p>Total PDFs candidates: <strong>{count_total + count_signed}</strong></p>
            <p>Skipped (signed): <strong>{count_signed}</strong></p>
            <p>Successfully cleaned: <strong>{count_cleaned}</strong></p>
            <p>Errors: <strong>{len(errors)}</strong></p>
            <pre>{'<br>'.join(errors)}</pre>
        """

        transaction.commit()
        self.request.response.setHeader("Content-Type", "text/html; charset=utf-8")
        return html
