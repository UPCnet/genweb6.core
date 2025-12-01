from Products.Five import BrowserView
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from genweb6.core.controlpanels.netejar_metadades import IMetadadesSettings
from plone.namedfile.file import NamedBlobFile  

import requests
import logging
import transaction
from io import BytesIO
from PyPDF2 import PdfReader
import warnings

logger = logging.getLogger(__name__)

def is_signed_pdf(data):
    """
    Verifica si un PDF está firmado digitalmente.
    Suprime warnings de PyPDF2 relacionados con fuentes corruptas.
    """
    try:
        # Suprimir warnings específicos de PyPDF2
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="PyPDF2")
            warnings.filterwarnings("ignore", message=".*Invalid Font Weight.*")
            warnings.filterwarnings("ignore", message=".*Unknown character collection.*")
            warnings.filterwarnings("ignore", message=".*Expected the optional content group list.*")
            
            reader = PdfReader(BytesIO(data))
            
            # Verificar si tiene AcroForm (formularios)
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
        settings = registry.forInterface(IMetadadesSettings, check=False)

        api_url = settings.api_url
        api_key = settings.api_key

        headers = {
            'accept': 'application/json;charset=utf-8',
            'X-Api-Key': api_key
        }

        count_total = 0
        count_cleaned = 0
        count_signed = 0
        count_problematic = 0
        errors = []
        problematic_pdfs = []



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

            # Verificar si el PDF está firmado
            try:
                if is_signed_pdf(file_data):
                    logger.info(f"[SKIPPED] {obj.absolute_url()} - PDF signat")
                    count_signed += 1
                    continue
            except Exception as e:
                logger.warning(f"[PROBLEMATIC] {obj.absolute_url()} - Error verificando firma: {e}")
                problematic_pdfs.append(f"{obj.absolute_url()} - Error verificando firma: {str(e)}")
                count_problematic += 1
                continue

            count_total += 1

            try:
                filename = obj.file.filename
                #logger.info(f"[PROCESSING] {obj.absolute_url()} - {filename}")

                files = {
                    'fitxerPerNetejarMetadades': (filename, file_data, 'application/pdf')
                }

                response = requests.post(api_url, headers=headers, files=files, timeout=30)

                if response.status_code == 200:
                    cleaned_data = response.content
                    
                    # Verificar que el contenido limpiado no esté vacío
                    if len(cleaned_data) == 0:
                        errors.append(f"{obj.absolute_url()}: API retornó contenido vacío")
                        logger.warning(f"[FAIL] {obj.absolute_url()} - API retornó contenido vacío")
                        continue

                    obj.file = NamedBlobFile(
                        data=cleaned_data,
                        contentType='application/pdf',
                        filename=filename
                    )

                    obj.reindexObject()
                    count_cleaned += 1
                    logger.info(f"[OK] {obj.absolute_url()}")
                else:
                    error_msg = f"API error {response.status_code}"
                    if hasattr(response, 'text'):
                        error_msg += f": {response.text[:200]}"
                    errors.append(f"{obj.absolute_url()}: {error_msg}")
                    logger.warning(f"[FAIL] {obj.absolute_url()} - {error_msg}")

            except requests.exceptions.Timeout:
                error_msg = "Timeout en la petición a la API"
                errors.append(f"{obj.absolute_url()}: {error_msg}")
                logger.warning(f"[TIMEOUT] {obj.absolute_url()}")
            except requests.exceptions.RequestException as e:
                error_msg = f"Error de conexión: {str(e)}"
                errors.append(f"{obj.absolute_url()}: {error_msg}")
                logger.warning(f"[CONNECTION_ERROR] {obj.absolute_url()} - {error_msg}")
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                errors.append(f"{obj.absolute_url()}: {error_msg}")
                logger.exception(f"[ERROR] {obj.absolute_url()} - {error_msg}")

        html = f"""
            <h2>PDF Metadata Cleanup</h2>
            <p>Total PDFs candidates: <strong>{count_total + count_signed + count_problematic}</strong></p>
            <p>Skipped (signed): <strong>{count_signed}</strong></p>
            <p>Problematic PDFs: <strong>{count_problematic}</strong></p>
            <p>Successfully cleaned: <strong>{count_cleaned}</strong></p>
            <p>Errors: <strong>{len(errors)}</strong></p>
            {f'<h3>PDFs problemáticos:</h3><pre>{"<br>".join(problematic_pdfs)}</pre>' if problematic_pdfs else ''}
            {f'<h3>Errores:</h3><pre>{"<br>".join(errors)}</pre>' if errors else ''}
        """

        transaction.commit()
        self.request.response.setHeader("Content-Type", "text/html; charset=utf-8")
        return html
