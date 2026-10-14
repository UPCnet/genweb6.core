# -*- coding: utf-8 -*-
"""Vista segura para reset de contraseña con rate-limiting y CAPTCHA."""

from plone import api
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from AccessControl import Unauthorized
from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory
from plone.registry.interfaces import IRegistry

from genweb6.core.utils import get_client_ip, check_rate_limit

import logging

_ = MessageFactory('genweb')

logger = logging.getLogger(__name__)


class SecurePasswordResetView(BrowserView):
    """Vista segura para reset de contraseña.

    Previene enumeración de usuarios e implementa rate-limiting y CAPTCHA.
    """

    def __call__(self):
        """Procesa la solicitud de reset con medidas de seguridad."""
        request = self.request
        form = request.form

        # Obtener configuración de rate-limiting del registry
        registry = queryUtility(IRegistry)
        max_attempts = registry.get(
            'genweb6.core.password_reset.max_attempts', 5
        )
        window_minutes = registry.get(
            'genweb6.core.password_reset.window_minutes', 10
        )
        require_captcha_after = registry.get(
            'genweb6.core.password_reset.require_captcha_after', 3
        )

        # Obtener IP del cliente
        ip_address = get_client_ip(request)

        # Verificar rate-limiting
        is_allowed, remaining_attempts, reset_time = check_rate_limit(
            ip_address, max_attempts, window_minutes
        )

        if not is_allowed:
            # Rate limit excedido
            logger.warning(
                f"Rate limit excedido para IP {ip_address}. "
                f"Reset en {reset_time} segundos"
            )
            # Siempre devolver mensaje genérico
            self._show_generic_message()
            return self._render_form()

        # Verificar si se requiere CAPTCHA
        attempts_count = max_attempts - remaining_attempts
        requires_captcha = attempts_count >= require_captcha_after

        # Si es POST, procesar el formulario
        if request.method == 'POST':
            userid = form.get('userid', '').strip()

            # Validar CAPTCHA si es requerido
            if requires_captcha:
                captcha_valid = self._validate_captcha()
                if not captcha_valid:
                    logger.warning(
                        f"CAPTCHA inválido para IP {ip_address}, "
                        f"usuario: {userid}"
                    )
                    self._show_generic_message()
                    return self._render_form()

            # Validar que se proporcionó un userid
            if not userid:
                self._show_generic_message()
                return self._render_form()

            # Procesar reset de contraseña sin exponer información
            try:
                # Intentar enviar el correo
                response = self.context.portal_registration.mailPassword(
                    userid,
                    request,
                )
                # Si llegamos aquí, el correo se envió correctamente
                # Pero siempre mostramos el mismo mensaje genérico
                self._show_generic_message()
                return response or self._render_form()

            except (ValueError, Unauthorized) as e:
                # ValueError: usuario no existe, email inválido, etc.
                # Unauthorized: permisos deshabilitados, etc.
                # NO exponer el error real, siempre mostrar mensaje genérico
                logger.info(
                    f"Intento de reset de contraseña para usuario "
                    f"'{userid}' desde IP {ip_address}: {type(e).__name__}"
                )
                self._show_generic_message()
                return self._render_form()

            except Exception as e:
                # Cualquier otra excepción (incluido HTTP 500 para usuarios
                # como 'admin', errores SMTP, etc.)
                # Manejar de forma genérica sin exponer información
                logger.error(
                    f"Error procesando reset de contraseña para IP "
                    f"{ip_address}: {str(e)}"
                )
                self._show_generic_message()
                return self._render_form()

        # GET request - mostrar formulario
        return self._render_form()

    def _validate_captcha(self):
        """Valida el CAPTCHA del formulario."""
        try:
            # Obtener el widget de CAPTCHA
            captcha = self.request.form.get('g-recaptcha-response', '')
            if not captcha:
                return False

            # Validar con el servicio de reCAPTCHA
            # Esta validación se hace normalmente en el widget,
            # pero aquí la hacemos manualmente para mayor control
            from plone.formwidget.recaptcha import getRecaptchaSettings
            settings = getRecaptchaSettings()

            if not settings or not settings.public_key or \
               not settings.private_key:
                # Si no hay configuración de CAPTCHA, permitir
                # (para desarrollo)
                logger.warning(
                    "CAPTCHA no configurado, permitiendo request"
                )
                return True

            # Validar con Google reCAPTCHA API
            import urllib.request
            import urllib.parse
            import json

            data = urllib.parse.urlencode({
                'secret': settings.private_key,
                'response': captcha,
                'remoteip': get_client_ip(self.request)
            }).encode()

            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            req = urllib.request.Request(verify_url, data=data)

            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode())
                return result.get('success', False)

        except Exception as e:
            logger.error(f"Error validando CAPTCHA: {str(e)}")
            # En caso de error, ser conservador y rechazar
            return False

    def _show_generic_message(self):
        """Muestra mensaje genérico sin exponer información de usuarios."""
        msg = _(
            'password_reset_generic_message',
            default=(
                'Si el usuario existe en el sistema, recibirá un correo '
                'electrónico con las instrucciones para restablecer la '
                'contraseña.'
            )
        )
        IStatusMessage(self.request).addStatusMessage(msg, type='info')

    def _render_form(self):
        """Renderiza el formulario de reset de contraseña."""
        # Redirigir al formulario personalizado
        self.request.response.redirect(
            self.context.absolute_url() + '/mail_password_form'
        )
        return ''

    def requires_captcha(self):
        """Indica si se requiere CAPTCHA para esta solicitud."""
        registry = queryUtility(IRegistry)
        require_captcha_after = registry.get(
            'genweb6.core.password_reset.require_captcha_after', 3
        )

        # Si require_captcha_after es 0, siempre mostrar CAPTCHA
        if require_captcha_after == 0:
            return True

        max_attempts = registry.get(
            'genweb6.core.password_reset.max_attempts', 5
        )

        ip_address = get_client_ip(self.request)
        is_allowed, remaining_attempts, reset_time = check_rate_limit(
            ip_address, max_attempts, 10
        )

        attempts_count = max_attempts - remaining_attempts
        return attempts_count >= require_captcha_after


class SecurePasswordResetFormView(BrowserView):
    """Vista del formulario de reset de contraseña con CAPTCHA."""

    def requires_captcha(self):
        """Indica si se requiere CAPTCHA para esta solicitud."""
        # Permitir forzar CAPTCHA con parámetro de query (solo desarrollo)
        if self.request.get('force_captcha') == '1':
            return True

        registry = queryUtility(IRegistry)
        require_captcha_after = registry.get(
            'genweb6.core.password_reset.require_captcha_after', 3
        )

        # Si require_captcha_after es 0, siempre mostrar CAPTCHA
        if require_captcha_after == 0:
            return True

        max_attempts = registry.get(
            'genweb6.core.password_reset.max_attempts', 5
        )

        ip_address = get_client_ip(self.request)
        is_allowed, remaining_attempts, reset_time = check_rate_limit(
            ip_address, max_attempts, 10
        )

        attempts_count = max_attempts - remaining_attempts
        return attempts_count >= require_captcha_after

    def get_recaptcha_site_key(self):
        """Obtiene la clave pública de reCAPTCHA."""
        try:
            from plone.formwidget.recaptcha.interfaces import (
                IReCaptchaSettings
            )
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(
                IReCaptchaSettings, check=False
            )

            if settings and settings.public_key:
                return settings.public_key
        except Exception:
            pass
        return ''

    @property
    def portal_url(self):
        """URL del portal."""
        return api.portal.get().absolute_url()
