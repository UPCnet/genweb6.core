"""Vista per mostrar el llistat d'assistència a una activitat"""

from Products.Five.browser import BrowserView
from plone import api
import datetime


class AssistenciaLlistatView(BrowserView):
    """Vista per mostrar assistències registrades"""
    
    def __call__(self):
        """Mostra el llistat d'assistència"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Obtenir totes les inscripcions
        inscripcions = self.context.listFolderContents(
            contentFilter={'portal_type': 'Inscripcio'}
        )
        
        # Debug: Mostrar tots els objectes de l'activitat
        tots_objectes = self.context.listFolderContents()
        debug_info = {
            'total_objectes': len(tots_objectes),
            'tipus_objectes': [obj.portal_type for obj in tots_objectes],
            'noms_objectes': [obj.getId() for obj in tots_objectes],
            'inscripcions_trobades': len(inscripcions)
        }
        
        # Separar assistents i no assistents
        assistents = []
        no_assistents = []
        
        for inscripcio in inscripcions:
            if getattr(inscripcio, 'ha_assistit', False):
                assistents.append(inscripcio)
            else:
                no_assistents.append(inscripcio)
        
        # Estadístiques
        total_inscripcions = len(inscripcions)
        total_assistents = len(assistents)
        percentatge = round((total_assistents / total_inscripcions) * 100, 1) if total_inscripcions > 0 else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📊 Llistat d'Assistència - {self.context.title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    margin: 0;
                    background: #f8f9fa;
                }}
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #007bff; text-align: center; margin-bottom: 30px; }}
                .stats {{ 
                    display: flex; 
                    justify-content: space-around; 
                    margin: 30px 0;
                    padding: 20px;
                    background: #e9ecef;
                    border-radius: 10px;
                }}
                .stat {{ text-align: center; }}
                .stat-number {{ 
                    font-size: 2em; 
                    font-weight: bold; 
                    color: #007bff; 
                    display: block;
                }}
                .stat-label {{ color: #6c757d; }}
                
                .section {{ margin: 30px 0; }}
                .section h2 {{ 
                    color: #495057; 
                    border-bottom: 2px solid #dee2e6; 
                    padding-bottom: 10px;
                }}
                
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0;
                }}
                th, td {{ 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #dee2e6;
                }}
                th {{ 
                    background: #f8f9fa; 
                    font-weight: bold; 
                    color: #495057;
                }}
                tr:hover {{ background: #f8f9fa; }}
                
                .assistit {{ color: #28a745; font-weight: bold; }}
                .no-assistit {{ color: #6c757d; }}
                .data-assistencia {{ 
                    font-size: 0.9em; 
                    color: #6c757d; 
                }}
                
                .buttons {{ 
                    text-align: center; 
                    margin: 30px 0; 
                }}
                .btn {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 20px; 
                    border: none; 
                    border-radius: 5px; 
                    text-decoration: none; 
                    display: inline-block;
                    margin: 5px;
                    font-size: 16px;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn-success {{ background: #28a745; }}
                .btn-success:hover {{ background: #218838; }}
                .btn-secondary {{ background: #6c757d; }}
                .btn-secondary:hover {{ background: #5a6268; }}
                
                .empty {{ 
                    text-align: center; 
                    color: #6c757d; 
                    font-style: italic; 
                    padding: 40px;
                }}
                
                @media (max-width: 768px) {{
                    .stats {{ flex-direction: column; }}
                    .stat {{ margin: 10px 0; }}
                    table {{ font-size: 14px; }}
                    th, td {{ padding: 8px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Llistat d'Assistència</h1>
                <h2 style="text-align: center; color: #6c757d; margin-bottom: 30px;">{self.context.title}</h2>
                
                <!-- Debug Info -->
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 12px;">
                    <strong>🔍 Debug Info:</strong><br>
                    <strong>Total objectes a l'activitat:</strong> {debug_info['total_objectes']}<br>
                    <strong>Tipus d'objectes:</strong> {', '.join(debug_info['tipus_objectes'])}<br>
                    <strong>Noms d'objectes:</strong> {', '.join(debug_info['noms_objectes'])}<br>
                    <strong>Inscripcions trobades:</strong> {debug_info['inscripcions_trobades']}<br>
                    <strong>Context UID:</strong> {self.context.UID()}<br>
                    <strong>Context Path:</strong> {'/'.join(self.context.getPhysicalPath())}
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <span class="stat-number">{total_inscripcions}</span>
                        <span class="stat-label">Inscripcions</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">{total_assistents}</span>
                        <span class="stat-label">Assistents</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">{percentatge}%</span>
                        <span class="stat-label">Assistència</span>
                    </div>
                </div>
                
                <div class="buttons">
                    <a href="{self.context.absolute_url()}/@@qr_scanner_final" class="btn btn-success">
                        📷 Escàner QR
                    </a>
                    <a href="{self.context.absolute_url()}/@@qr_simple_demo" class="btn">
                        🎫 Demo QR
                    </a>
                    <button onclick="window.print()" class="btn btn-secondary">
                        🖨️ Imprimir
                    </button>
                    <button onclick="exportarCSV()" class="btn btn-secondary">
                        📄 Exportar CSV
                    </button>
                </div>
        """
        
        # Secció d'assistents
        if assistents:
            html += f"""
                <div class="section">
                    <h2>✅ Assistents ({len(assistents)})</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Nom</th>
                                <th>Email</th>
                                <th>Col·lectiu</th>
                                <th>Data/Hora Assistència</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Ordenar per data d'assistència
            assistents_ordenats = sorted(
                assistents, 
                key=lambda x: getattr(x, 'data_assistencia', datetime.datetime.now()),
                reverse=True
            )
            
            for inscripcio in assistents_ordenats:
                data_assistencia = getattr(inscripcio, 'data_assistencia', None)
                data_str = data_assistencia.strftime('%d/%m/%Y %H:%M:%S') if data_assistencia else 'No registrada'
                
                html += f"""
                            <tr>
                                <td class="assistit">{inscripcio.get_nom_complet()}</td>
                                <td>{inscripcio.email}</td>
                                <td>{inscripcio.get_collectiu_display()}</td>
                                <td class="data-assistencia">{data_str}</td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            """
        else:
            html += """
                <div class="section">
                    <h2>✅ Assistents (0)</h2>
                    <div class="empty">Encara no hi ha assistents registrats</div>
                </div>
            """
        
        # Secció de no assistents
        if no_assistents:
            html += f"""
                <div class="section">
                    <h2>⏳ Pendents d'Assistir ({len(no_assistents)})</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Nom</th>
                                <th>Email</th>
                                <th>Col·lectiu</th>
                                <th>Data Inscripció</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for inscripcio in no_assistents:
                try:
                    data_inscripcio = inscripcio.created().strftime('%d/%m/%Y %H:%M')
                except:
                    data_inscripcio = 'No disponible'
                
                html += f"""
                            <tr>
                                <td class="no-assistit">{inscripcio.get_nom_complet()}</td>
                                <td>{inscripcio.email}</td>
                                <td>{inscripcio.get_collectiu_display()}</td>
                                <td class="data-assistencia">{data_inscripcio}</td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            """
        
        # JavaScript per exportar CSV
        assistents_json = []
        for inscripcio in inscripcions:
            data_assistencia = getattr(inscripcio, 'data_assistencia', None)
            
            # Convertir DateTime de Zope a string
            data_inscripcio_dt = inscripcio.created()
            data_inscripcio_str = data_inscripcio_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            assistents_json.append({
                'nom': inscripcio.get_nom_complet(),
                'email': inscripcio.email,
                'collectiu': inscripcio.get_collectiu_display(),
                'ha_assistit': getattr(inscripcio, 'ha_assistit', False),
                'data_assistencia': data_assistencia.isoformat() if data_assistencia else '',
                'data_inscripcio': data_inscripcio_str
            })
        
        html += f"""
                <a href="{self.context.absolute_url()}" class="btn btn-secondary" style="display: block; width: fit-content; margin: 30px auto;">
                    ← Tornar a l'Activitat
                </a>
            </div>
            
            <script>
                const assistentsData = {assistents_json};
                
                function exportarCSV() {{
                    const headers = ['Nom', 'Email', 'Col·lectiu', 'Ha Assistit', 'Data Assistència', 'Data Inscripció'];
                    const csvContent = [
                        headers.join(','),
                        ...assistentsData.map(row => [
                            '"' + row.nom + '"',
                            '"' + row.email + '"', 
                            '"' + row.collectiu + '"',
                            row.ha_assistit ? 'Sí' : 'No',
                            '"' + (row.data_assistencia || '') + '"',
                            '"' + row.data_inscripcio + '"'
                        ].join(','))
                    ].join('\\n');
                    
                    const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
                    const link = document.createElement('a');
                    const url = URL.createObjectURL(blob);
                    link.setAttribute('href', url);
                    link.setAttribute('download', 'assistencia_{self.context.getId()}.csv');
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                // Auto-refresh cada 30 segons si estem escanejant
                if (window.location.hash === '#auto-refresh') {{
                    setInterval(() => {{
                        window.location.reload();
                    }}, 30000);
                }}
            </script>
        </body>
        </html>
        """
        
        return html