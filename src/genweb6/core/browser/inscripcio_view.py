"""Vista personalitzada per mostrar la inscripció amb QR"""

from Products.Five.browser import BrowserView


class InscripcioView(BrowserView):
    """Vista per mostrar la inscripció amb el QR visible"""
    
    def __call__(self):
        """Mostra la inscripció amb QR"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        inscripcio = self.context
        activitat = inscripcio.aq_parent
        
        # Obtenir dades de la inscripció
        qr_image_data = getattr(inscripcio, 'qr_image_data', '')
        qr_code_json = getattr(inscripcio, 'qr_code', '')
        ha_assistit = getattr(inscripcio, 'ha_assistit', False)
        data_assistencia = getattr(inscripcio, 'data_assistencia', None)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🎫 {inscripcio.title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    margin: 0;
                    background: #f8f9fa;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #007bff; text-align: center; }}
                .status-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .status-assistit {{ background: #d4edda; color: #155724; }}
                .status-pendent {{ background: #fff3cd; color: #856404; }}
                
                .info-section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin: 20px 0;
                }}
                .info-item {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                }}
                .info-label {{ font-weight: bold; color: #495057; }}
                .info-value {{ color: #212529; margin-top: 5px; }}
                
                .qr-section {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 30px;
                    background: #f8f9fa;
                    border-radius: 15px;
                    border: 3px dashed #007bff;
                }}
                .qr-image {{
                    max-width: 300px;
                    margin: 20px auto;
                    display: block;
                    border: 3px solid #007bff;
                    border-radius: 10px;
                    padding: 15px;
                    background: white;
                }}
                .no-qr {{
                    color: #6c757d;
                    font-style: italic;
                    padding: 40px;
                }}
                
                .btn {{
                    background: #007bff;
                    color: white;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    display: inline-block;
                    margin: 10px 5px;
                    font-size: 16px;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn-success {{ background: #28a745; }}
                .btn-success:hover {{ background: #218838; }}
                .btn-secondary {{ background: #6c757d; }}
                .btn-secondary:hover {{ background: #5a6268; }}
                .btn-danger {{ background: #dc3545; }}
                .btn-danger:hover {{ background: #c82333; }}
                
                .actions {{ text-align: center; margin: 30px 0; }}
                
                .json-data {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 12px;
                    word-break: break-all;
                    margin-top: 15px;
                    max-height: 200px;
                    overflow-y: auto;
                }}
                
                @media (max-width: 768px) {{
                    .info-grid {{ grid-template-columns: 1fr; }}
                    .container {{ padding: 15px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎫 Inscripció a {activitat.title}</h1>
                
                <div style="text-align: center;">
        """
        
        if ha_assistit:
            html += f"""
                    <span class="status-badge status-assistit">✅ Assistència Registrada</span>
            """
        else:
            html += f"""
                    <span class="status-badge status-pendent">⏳ Pendent d'Assistir</span>
            """
        
        html += f"""
                </div>
                
                <div class="info-section">
                    <h3>📋 Dades de la Inscripció</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Nom Complet</div>
                            <div class="info-value">{inscripcio.get_nom_complet()}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Email</div>
                            <div class="info-value">{inscripcio.email}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Telèfon</div>
                            <div class="info-value">{getattr(inscripcio, 'telefon', 'No disponible')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Col·lectiu</div>
                            <div class="info-value">{inscripcio.get_collectiu_display()}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Centre/Unitat</div>
                            <div class="info-value">{getattr(inscripcio, 'centre_unitat', 'No disponible')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Data d'Inscripció</div>
                            <div class="info-value">{inscripcio.created().strftime('%d/%m/%Y %H:%M')}</div>
                        </div>
        """
        
        if ha_assistit and data_assistencia:
            html += f"""
                        <div class="info-item">
                            <div class="info-label">Data d'Assistència</div>
                            <div class="info-value">{data_assistencia.strftime('%d/%m/%Y %H:%M:%S')}</div>
                        </div>
            """
        
        html += f"""
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>🎯 Activitat</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Títol</div>
                            <div class="info-value">{activitat.title}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Data i Hora</div>
                            <div class="info-value">{activitat.data_inici.strftime('%d/%m/%Y %H:%M') if getattr(activitat, 'data_inici', None) else 'Per determinar'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Lloc</div>
                            <div class="info-value">{getattr(activitat, 'lloc', 'Per determinar')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Preu</div>
                            <div class="info-value">{getattr(activitat, 'preu', 0)}€</div>
                        </div>
                    </div>
                </div>
        """
        
        # Secció del QR
        if qr_image_data:
            html += f"""
                <div class="qr-section">
                    <h3>📱 Codi QR d'Assistència</h3>
                    <p><strong>Presenta aquest QR a l'entrada de l'activitat</strong></p>
                    
                    <img src="data:image/png;base64,{qr_image_data}" 
                         alt="Codi QR d'assistència" class="qr-image">
                    
                    <p><em>Pots fer una captura de pantalla o mostrar aquesta pàgina des del mòbil</em></p>
            """
            
            if qr_code_json:
                html += f"""
                    <details style="margin-top: 20px;">
                        <summary style="cursor: pointer; color: #007bff;">📄 Veure dades del QR</summary>
                        <div class="json-data">{qr_code_json}</div>
                    </details>
                """
            
            html += """
                </div>
            """
        else:
            html += """
                <div class="qr-section">
                    <div class="no-qr">
                        <h3>⚠️ QR No Disponible</h3>
                        <p>El codi QR no s'ha generat correctament per aquesta inscripció.</p>
                    </div>
                </div>
            """
        
        # Accions
        html += f"""
                <div class="actions">
                    <a href="{activitat.absolute_url()}/@@qr_scanner_final" class="btn btn-success">
                        📷 Provar Escàner
                    </a>
                    
                    <a href="{activitat.absolute_url()}/@@assistencia_llistat" class="btn">
                        📊 Llistat d'Assistència
                    </a>
                    
                    <a href="{inscripcio.absolute_url()}/edit" class="btn btn-secondary">
                        ✏️ Editar Inscripció
                    </a>
                    
                    <a href="{activitat.absolute_url()}" class="btn btn-secondary">
                        ← Tornar a l'Activitat
                    </a>
                </div>
                
                <div style="text-align: center; margin-top: 30px; font-size: 14px; color: #6c757d;">
                    <p>ID Inscripció: {inscripcio.getId()} | UID: {inscripcio.UID()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html