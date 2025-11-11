# -*- coding: utf-8 -*-
"""
Tests de seguridad para la validación de portrait upload.

Estos tests verifican que el sistema rechaza archivos maliciosos
y acepta solo imágenes válidas (JPG, PNG, WEBP).
"""
import unittest
from io import BytesIO

from genweb6.core.testing import GENWEB_INTEGRATION_TESTING
from genweb6.core.validations import (
    validate_image_file_content,
    validate_portrait_upload,
    InvalidImageFile,
    UnsafeImageType,
)


class PortraitValidationUnitTest(unittest.TestCase):
    """Tests unitarios para validación de portrait por magic bytes"""

    def setUp(self):
        """Prepara los datos de prueba"""
        # JPEG válido (magic bytes)
        self.jpeg_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            + b'\x00' * 100
        )

        # PNG válido (magic bytes)
        self.png_data = (
            b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR\x00\x00\x00\x01'
            + b'\x00' * 100
        )

        # WebP válido (magic bytes)
        self.webp_data = (
            b'RIFF' + b'\x00\x00\x00\x00' + b'WEBP' + b'VP8 ' + b'\x00' * 100
        )

        # PHP file malicioso
        self.php_data = b'<?php system($_GET["cmd"]); ?>'

        # Shell script malicioso
        self.shell_data = b'#!/bin/bash\nrm -rf /'

        # Texto plano
        self.text_data = b'This is just text'

        # GIF (no está en whitelist)
        self.gif_data = b'GIF89a' + b'\x00' * 100

    def test_jpeg_valid_magic_bytes(self):
        """Test que valida JPEG por magic bytes"""
        result = validate_image_file_content(self.jpeg_data)
        self.assertEqual(result, 'jpeg')

    def test_png_valid_magic_bytes(self):
        """Test que valida PNG por magic bytes"""
        result = validate_image_file_content(self.png_data)
        self.assertEqual(result, 'png')

    def test_webp_valid_magic_bytes(self):
        """Test que valida WebP por magic bytes"""
        result = validate_image_file_content(self.webp_data)
        self.assertEqual(result, 'webp')

    def test_php_file_rejected(self):
        """Test que rechaza archivos PHP"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(self.php_data)

    def test_shell_script_rejected(self):
        """Test que rechaza shell scripts"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(self.shell_data)

    def test_text_file_rejected(self):
        """Test que rechaza archivos de texto"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(self.text_data)

    def test_gif_file_rejected(self):
        """Test que rechaza GIF (no está en whitelist)"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(self.gif_data)

    def test_empty_file_rejected(self):
        """Test que rechaza archivos vacíos"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(b'')

    def test_too_small_file_rejected(self):
        """Test que rechaza archivos demasiado pequeños"""
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(b'abc')

    def test_file_like_object_jpeg(self):
        """Test validación con objeto file-like (JPEG)"""
        file_obj = BytesIO(self.jpeg_data)
        result = validate_image_file_content(file_obj)
        self.assertEqual(result, 'jpeg')

    def test_file_like_object_malicious(self):
        """Test rechazo con objeto file-like (PHP)"""
        file_obj = BytesIO(self.php_data)
        with self.assertRaises(InvalidImageFile):
            validate_image_file_content(file_obj)


class PortraitUploadIntegrationTest(unittest.TestCase):
    """Tests de integración para el upload completo de portrait"""

    layer = GENWEB_INTEGRATION_TESTING

    def setUp(self):
        """Prepara el entorno de test"""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # Datos de prueba
        self.valid_jpeg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            + b'\x00' * 100
        )
        self.malicious_php = b'<?php system($_GET["cmd"]); ?>'

    def test_validate_portrait_with_valid_image(self):
        """Test que acepta una imagen válida en validate_portrait_upload"""

        class FakePortrait:
            def __init__(self, data, filename):
                self.data = data
                self.filename = filename

        portrait = FakePortrait(self.valid_jpeg, 'photo.jpg')
        result = validate_portrait_upload(portrait)
        self.assertTrue(result)

    def test_validate_portrait_with_malicious_file(self):
        """Test que rechaza archivo malicioso en validate_portrait_upload"""

        class FakePortrait:
            def __init__(self, data, filename):
                self.data = data
                self.filename = filename

        portrait = FakePortrait(self.malicious_php, 'shell.php')
        with self.assertRaises(InvalidImageFile):
            validate_portrait_upload(portrait)

    def test_validate_portrait_with_none(self):
        """Test que maneja None correctamente"""
        result = validate_portrait_upload(None)
        self.assertFalse(result)


class SecurityScenarioTest(unittest.TestCase):
    """
    Tests que simulan escenarios de seguridad reales
    basados en la vulnerabilidad reportada
    """

    def test_shell_php_upload_blocked(self):
        """
        Test del escenario real reportado:
        Intento de subir shell.php debe ser bloqueado
        """
        # Contenido típico de un webshell
        malicious_content = (
            b'<?php\n'
            b'if(isset($_GET["cmd"])) {\n'
            b'    system($_GET["cmd"]);\n'
            b'}\n'
            b'?>'
        )

        # Este contenido DEBE ser rechazado
        with self.assertRaises(InvalidImageFile) as cm:
            validate_image_file_content(malicious_content)

        # Verificar que el mensaje de error es apropiado
        self.assertIn('no reconocido', str(cm.exception))

    def test_php_disguised_as_jpg(self):
        """
        Test que rechaza PHP incluso si tiene extensión .jpg
        La validación NO debe confiar en la extensión
        """

        class FakePortrait:
            def __init__(self, data, filename):
                self.data = data
                self.filename = filename

        # PHP con extensión de imagen
        portrait = FakePortrait(
            b'<?php system("whoami"); ?>',
            'fake_image.jpg'  # Extensión engañosa
        )

        # DEBE ser rechazado por contenido, no por extensión
        with self.assertRaises(InvalidImageFile):
            validate_portrait_upload(portrait)

    def test_jpeg_with_php_extension_accepted(self):
        """
        Test que acepta JPEG real incluso con extensión .php
        La validación SOLO debe mirar el contenido real
        """

        class FakePortrait:
            def __init__(self, data, filename):
                self.data = data
                self.filename = filename

        # JPEG real con extensión engañosa
        jpeg_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            + b'\x00' * 100
        )
        portrait = FakePortrait(jpeg_data, 'file.php')

        # DEBE ser aceptado porque el contenido es JPEG válido
        result = validate_portrait_upload(portrait)
        self.assertTrue(result)


def test_suite():
    """Crea la suite de tests"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortraitValidationUnitTest))
    suite.addTest(unittest.makeSuite(PortraitUploadIntegrationTest))
    suite.addTest(unittest.makeSuite(SecurityScenarioTest))
    return suite


if __name__ == '__main__':
    unittest.main()

