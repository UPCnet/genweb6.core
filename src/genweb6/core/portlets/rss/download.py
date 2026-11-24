# -*- coding: utf-8 -*-
"""Descarga de feeds RSS para los portlets RSS (el de Plone y el de genweb).

Sustituye a ``plone.app.portlets.portlets.rss._download_feed_and_response``
(plone.app.portlets >= 5.0.8), que corta a los 3,5 s y no sigue redirecciones.
Con ese límite, feeds lentos (por ejemplo, el RSS de la propia web cuando se
regenera sin caché) fallaban y el portlet se quedaba en blanco.

Se mantienen las protecciones del parche de seguridad de Plone:

- límite de tamaño (``MAXIMUM_RSS_FEED_SIZE_BYTES``, 1 MB por defecto);
- cada redirección se valida con ``_rss_feed_url_validator`` (no se puede
  saltar a file://, hosts internos, etc.) y como máximo se siguen
  ``MAX_REDIRECTS``;
- timeout, ahora de 5 s por defecto, configurable con la variable de entorno
  ``GENWEB_RSS_FEED_TIMEOUT`` (segundos). Como en ``requests``, es el tiempo
  máximo para conectar y el tiempo máximo esperando datos, no el total.
"""
from plone.app.portlets.portlets.rss import MAXIMUM_RSS_FEED_SIZE_BYTES
from plone.app.portlets.portlets.rss import _rss_feed_url_validator
from urllib.parse import urljoin

import os
import requests


RSS_FEED_TIMEOUT = float(os.getenv('GENWEB_RSS_FEED_TIMEOUT', 5))
MAX_REDIRECTS = 3


def download_feed_and_response(url, limit=MAXIMUM_RSS_FEED_SIZE_BYTES,
                               headers=None):
    """Descarga el feed y devuelve ``(contenido, respuesta)``.

    Misma firma y contrato que la función de plone.app.portlets: puede lanzar
    excepciones de ``requests``, ``ValueError`` o ``zope.interface.Invalid``
    (redirección a una URL no permitida); quien llama las captura.
    """
    if limit <= 0:
        raise ValueError('You must pass a limit for the number of bytes.')

    for _hop in range(MAX_REDIRECTS + 1):
        response = requests.get(
            url, stream=True, allow_redirects=False,
            timeout=RSS_FEED_TIMEOUT, headers=headers)
        if not response.is_redirect:
            break
        location = response.headers.get('Location', '')
        response.close()
        url = urljoin(url, location)
        # Una redirección no puede llevar donde no se permitiría configurar.
        _rss_feed_url_validator(url)
    else:
        raise ValueError('Too many redirects.')

    response.raise_for_status()
    if response.status_code == 304:
        # No ha cambiado desde la última descarga (If-Modified-Since / ETag).
        return b'', response

    length = response.headers.get('Content-Length')
    if length and int(length) > limit:
        raise ValueError('Content-Length header too large')

    contents = b''
    for chunk in response.iter_content(64 * 1024):
        contents += chunk
        if len(contents) > limit:
            response.close()
            raise ValueError('Downloaded too much content.')
    return contents, response


def feed_renderer_enabled(self):
    """El portlet se muestra si el feed está bien o si aún tiene elementos.

    Si una actualización falla (feed lento, caído o mal formado), se siguen
    mostrando los últimos elementos buenos en lugar de ocultar el portlet;
    se vuelve a intentar al cabo de ``RSSFeed.FAILURE_DELAY`` minutos.
    """
    feed = self._getFeed()
    return feed.ok or bool(feed.items)


# Para sustituir ``Renderer.enabled`` del portlet RSS de Plone (patches.zcml).
renderer_enabled = property(feed_renderer_enabled)
