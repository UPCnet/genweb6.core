# -*- coding: utf-8 -*-
"""Vista para ver estadísticas de cache LDAP."""

from Products.Five.browser import BrowserView


class LDAPCacheStatsView(BrowserView):
    """Muestra estadísticas de cache LDAP."""

    def __call__(self):
        from genweb6.core.patches import (
            get_ldap_cache_stats,
            _LDAP_LOCAL_CACHE,
        )

        stats = get_ldap_cache_stats()
        
        html = ['<html><head><title>LDAP Cache Stats</title>']
        html.append('<meta http-equiv="refresh" content="5">')  # Auto-refresh cada 5s
        html.append('<style>')
        html.append('body { font-family: monospace; padding: 20px; background: #f5f5f5; }')
        html.append('h1 { color: #333; }')
        html.append('table { border-collapse: collapse; margin: 20px 0; background: white; }')
        html.append('th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }')
        html.append('th { background-color: #4CAF50; color: white; }')
        html.append('tr:hover { background-color: #f1f1f1; }')
        html.append('.stats { background-color: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
        html.append('.empty { color: #666; font-style: italic; }')
        html.append('</style></head><body>')
        
        html.append('<h1>📊 Estadísticas Cache LDAP</h1>')
        html.append('<p><em>Auto-refresh cada 5 segundos</em></p>')
        
        html.append('<div class="stats">')
        html.append(f'<p><strong>Tamaño actual:</strong> {stats["size"]} entradas</p>')
        html.append(f'<p><strong>Tamaño máximo:</strong> {stats["max_size"]} entradas</p>')
        html.append(f'<p><strong>Timeout:</strong> {stats["timeout"]} segundos</p>')
        
        if stats['size'] > 0:
            pct = (stats['size'] / stats['max_size']) * 100
            html.append(f'<p><strong>Uso:</strong> {pct:.1f}%</p>')
        
        html.append('</div>')
        
        if stats['size'] > 0:
            # Analizar tipos de queries
            types = {}
            for key in _LDAP_LOCAL_CACHE.keys():
                func_name = key.split(':')[0]
                types[func_name] = types.get(func_name, 0) + 1
            
            html.append('<h2>📈 Queries por Tipo</h2>')
            html.append('<table>')
            html.append('<tr><th>Función</th><th>Cantidad</th><th>%</th></tr>')
            for func_name, count in sorted(types.items(), key=lambda x: -x[1]):
                pct = (count / stats['size']) * 100
                html.append(f'<tr><td><code>{func_name}</code></td><td>{count}</td><td>{pct:.1f}%</td></tr>')
            html.append('</table>')
            
            # Primeras 30 claves
            html.append('<h2>📋 Primeras 30 Claves en Cache</h2>')
            html.append('<table>')
            html.append('<tr><th>#</th><th>Clave</th></tr>')
            for i, key in enumerate(list(_LDAP_LOCAL_CACHE.keys())[:30], 1):
                html.append(f'<tr><td>{i}</td><td><small>{key}</small></td></tr>')
            html.append('</table>')
        else:
            html.append('<p class="empty">⚠️ Cache vacía. Navega a un órgano primero:</p>')
            html.append('<p class="empty">Ejemplo: <a href="/997/organsb/ca">http://localhost:11001/997/organsb/ca</a></p>')
        
        html.append('</body></html>')
        
        return '\n'.join(html)
