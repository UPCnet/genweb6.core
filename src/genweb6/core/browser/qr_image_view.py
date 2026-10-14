"""Vista per mostrar només la imatge QR"""

from Products.Five.browser import BrowserView
import base64


class QRImageView(BrowserView):
    """Vista per retornar la imatge QR com a PNG"""
    
    def __call__(self):
        """Retorna la imatge QR"""
        
        inscripcio = self.context
        qr_image_data = getattr(inscripcio, 'qr_image_data', '')
        
        if qr_image_data:
            try:
                # Decodificar base64 i retornar com a imatge PNG
                image_data = base64.b64decode(qr_image_data)
                
                self.request.response.setHeader('Content-Type', 'image/png')
                self.request.response.setHeader('Content-Length', str(len(image_data)))
                self.request.response.setHeader('Content-Disposition', f'inline; filename="qr_{inscripcio.getId()}.png"')
                
                return image_data
                
            except Exception as e:
                # Si hi ha error, retornar un PNG d'error simple
                self.request.response.setStatus(500)
                return f"Error generant imatge QR: {str(e)}"
        else:
            self.request.response.setStatus(404)
            return "Imatge QR no trobada"


class QRMobileView(BrowserView):
    """Vista optimitzada per mòbil per mostrar el QR"""
    
    def __call__(self):
        """Mostra el QR optimitzat per mòbil"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        inscripcio = self.context
        activitat = inscripcio.aq_parent
        qr_image_data = getattr(inscripcio, 'qr_image_data', '')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <title>🎫 QR - {inscripcio.get_nom_complet()}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                    background: #000;
                    color: white;
                    text-align: center;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }}
                .container {{ 
                    max-width: 400px; 
                    margin: 0 auto;
                }}
                h1 {{ 
                    color: #fff; 
                    font-size: 24px;
                    margin-bottom: 10px;
                }}
                .activitat {{ 
                    color: #ccc; 
                    font-size: 18px;
                    margin-bottom: 30px;
                }}
                .qr-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    box-shadow: 0 4px 20px rgba(255,255,255,0.3);
                }}
                .qr-image {{
                    width: 100%;
                    max-width: 300px;
                    height: auto;
                }}
                .info {{
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 16px;
                }}
                .instructions {{
                    color: #ccc;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .brightness {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 10px;
                    border-radius: 50%;
                    cursor: pointer;
                    font-size: 20px;
                }}
            </style>
        </head>
        <body>
            <button class="brightness" onclick="toggleBrightness()" title="Canviar brillantor">💡</button>
            
            <div class="container">
                <h1>🎫 Codi QR</h1>
                <div class="activitat">{activitat.title}</div>
                
                <div class="info">
                    <strong>{inscripcio.get_nom_complet()}</strong><br>
                    {inscripcio.get_collectiu_display()}
                </div>
        """
        
        if qr_image_data:
            html += f"""
                <div class="qr-container">
                    <img src="data:image/png;base64,{qr_image_data}" 
                         alt="Codi QR" class="qr-image">
                </div>
            """
        else:
            html += """
                <div class="qr-container" style="color: #000;">
                    <p>❌ QR no disponible</p>
                </div>
            """
        
        html += f"""
                <div class="instructions">
                    📱 Mostra aquest QR a l'entrada<br>
                    💡 Toca la bombeta per més llum
                </div>
            </div>
            
            <script>
                let brightMode = false;
                
                function toggleBrightness() {{
                    brightMode = !brightMode;
                    if (brightMode) {{
                        document.body.style.background = '#fff';
                        document.body.style.color = '#000';
                        document.querySelector('.activitat').style.color = '#666';
                        document.querySelector('.instructions').style.color = '#666';
                    }} else {{
                        document.body.style.background = '#000';
                        document.body.style.color = '#fff';
                        document.querySelector('.activitat').style.color = '#ccc';
                        document.querySelector('.instructions').style.color = '#ccc';
                    }}
                }}
                
                // Evitar que la pantalla s'apagui
                if ('wakeLock' in navigator) {{
                    navigator.wakeLock.request('screen').catch(err => {{
                        console.log('Wake lock no disponible:', err);
                    }});
                }}
                
                // Maximitzar brillantor automàticament en mòbils
                if (window.screen && window.screen.orientation) {{
                    document.addEventListener('visibilitychange', function() {{
                        if (!document.hidden) {{
                            // Quan la pàgina torna a ser visible, intentar mantenir la pantalla activa
                            if ('wakeLock' in navigator) {{
                                navigator.wakeLock.request('screen').catch(() => {{}});
                            }}
                        }}
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        return html