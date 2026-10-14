"""Vista per debugar l'estat de les inscripcions"""

from Products.Five.browser import BrowserView
import json


class DebugInscripcioView(BrowserView):
    """Vista per mostrar l'estat detallat de les inscripcions"""
    
    def __call__(self):
        """Mostra informació detallada de les inscripcions"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Obtenir totes les inscripcions
        inscripcions = self.context.listFolderContents(
            contentFilter={'portal_type': 'Inscripcio'}
        )
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>🔍 Debug Inscripcions</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .inscripcio {{ 
                    border: 1px solid #ddd; 
                    margin: 20px 0; 
                    padding: 15px; 
                    border-radius: 5px;
                    background: #f9f9f9;
                }}
                .assistit {{ background: #d4edda; border-color: #c3e6cb; }}
                .no-assistit {{ background: #f8d7da; border-color: #f5c6cb; }}
                pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                .btn {{ 
                    background: #007bff; color: white; padding: 8px 15px; 
                    border: none; border-radius: 3px; margin: 5px; cursor: pointer;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn-success {{ background: #28a745; }}
                .btn-danger {{ background: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Debug Inscripcions - {self.context.title}</h1>
                
                <p><strong>Total inscripcions trobades:</strong> {len(inscripcions)}</p>
        """
        
        for i, inscripcio in enumerate(inscripcions):
            ha_assistit = getattr(inscripcio, 'ha_assistit', False)
            data_assistencia = getattr(inscripcio, 'data_assistencia', None)
            
            # Informació completa de l'objecte
            info = {
                'id': inscripcio.getId(),
                'title': inscripcio.title,
                'nom': getattr(inscripcio, 'nom', 'No definit'),
                'cognoms': getattr(inscripcio, 'cognoms', 'No definit'),
                'email': getattr(inscripcio, 'email', 'No definit'),
                'collectiu': getattr(inscripcio, 'collectiu', 'No definit'),
                'ha_assistit': ha_assistit,
                'data_assistencia': str(data_assistencia) if data_assistencia else 'No definit',
                'portal_type': inscripcio.portal_type,
                'uid': inscripcio.UID(),
                'created': str(inscripcio.created()),
                'modified': str(inscripcio.modified()),
                'path': '/'.join(inscripcio.getPhysicalPath())
            }
            
            css_class = 'assistit' if ha_assistit else 'no-assistit'
            status_icon = '✅' if ha_assistit else '❌'
            
            html += f"""
                <div class="inscripcio {css_class}">
                    <h3>{status_icon} Inscripció {i+1}: {inscripcio.getId()}</h3>
                    
                    <p><strong>Nom complet:</strong> {inscripcio.get_nom_complet() if hasattr(inscripcio, 'get_nom_complet') else 'Mètode no disponible'}</p>
                    <p><strong>Email:</strong> {info['email']}</p>
                    <p><strong>Ha assistit:</strong> {ha_assistit}</p>
                    <p><strong>Data assistència:</strong> {info['data_assistencia']}</p>
                    
                    <button class="btn" onclick="toggleDetails('details_{i}')">Mostrar/Ocultar Detalls</button>
                    <button class="btn btn-success" onclick="marcarAssistencia('{inscripcio.UID()}')">Marcar Assistència</button>
                    <button class="btn btn-danger" onclick="esborrarAssistencia('{inscripcio.UID()}')">Esborrar Assistència</button>
                    
                    <div id="details_{i}" style="display:none; margin-top: 15px;">
                        <h4>Informació Completa:</h4>
                        <pre>{json.dumps(info, indent=2, ensure_ascii=False)}</pre>
                    </div>
                </div>
            """
        
        if not inscripcions:
            html += """
                <div class="inscripcio">
                    <h3>⚠️ No s'han trobat inscripcions</h3>
                    <p>No hi ha inscripcions dins d'aquesta activitat.</p>
                    <a href="@@qr_simple_demo" class="btn">Crear Inscripció Demo</a>
                </div>
            """
        
        html += f"""
                <div style="margin-top: 30px; text-align: center;">
                    <a href="{self.context.absolute_url()}" class="btn">← Tornar a l'Activitat</a>
                    <a href="@@assistencia_llistat" class="btn">📊 Llistat Assistència</a>
                    <button class="btn" onclick="window.location.reload()">🔄 Recarregar</button>
                </div>
            </div>
            
            <script>
                function toggleDetails(id) {{
                    const element = document.getElementById(id);
                    element.style.display = element.style.display === 'none' ? 'block' : 'none';
                }}
                
                async function marcarAssistencia(uid) {{
                    try {{
                        const response = await fetch('{self.context.absolute_url()}/@@debug_marcar_assistencia', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ inscripcio_uid: uid }})
                        }});
                        
                        const result = await response.json();
                        console.log('Resposta marcar:', result);
                        
                        if (result.success) {{
                            alert('✅ ' + result.message);
                        }} else {{
                            alert('❌ ' + (result.error || 'Error desconegut'));
                        }}
                        
                        window.location.reload();
                    }} catch (e) {{
                        console.error('Error marcar:', e);
                        alert('Error: ' + e.message);
                    }}
                }}
                
                async function esborrarAssistencia(uid) {{
                    try {{
                        const response = await fetch('{self.context.absolute_url()}/@@debug_esborrar_assistencia', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ inscripcio_uid: uid }})
                        }});
                        
                        const result = await response.json();
                        console.log('Resposta esborrar:', result);
                        
                        if (result.success) {{
                            alert('✅ ' + result.message);
                        }} else {{
                            alert('❌ ' + (result.error || 'Error desconegut'));
                        }}
                        
                        window.location.reload();
                    }} catch (e) {{
                        console.error('Error esborrar:', e);
                        alert('Error: ' + e.message);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        return html