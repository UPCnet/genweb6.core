"""Vista super simple per provar QR sense dependències"""

from Products.Five.browser import BrowserView


class QRSimpleView(BrowserView):
    """Vista simple per provar que tot funciona"""
    
    def __call__(self):
        """Retorna HTML simple"""
        
        # Configurar Content-Type per HTML
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        try:
            import qrcode
            import json
            import datetime
            import io
            import base64
            
            # Generar dades de prova
            qr_data = {
                'type': 'upcarts_inscripcio',
                'activitat_id': 'test-123',
                'inscripcio_id': 'inscripcio-456',
                'activitat_title': 'Test Activitat UPCArts',
                'nom': 'Joan Exemple',
                'email': 'joan@upc.edu',
                'collectiu': 'ESTUDIANT',
                'timestamp': datetime.datetime.now().isoformat(),
            }
            
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(json.dumps(qr_data, ensure_ascii=False))
            qr.make(fit=True)
            
            # Crear imatge
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            status = "✅ QR generat correctament!"
            
        except Exception as e:
            status = f"❌ Error: {str(e)}"
            img_base64 = ""
            qr_data = {}
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prova QR Simple</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .status {{ padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .success {{ background: #d4edda; color: #155724; }}
                .error {{ background: #f8d7da; color: #721c24; }}
                .qr-section {{ text-align: center; margin: 30px 0; }}
                .qr-image {{ border: 2px solid #007bff; padding: 15px; background: white; }}
                pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 Prova del Sistema QR</h1>
                
                <div class="status {'success' if '✅' in status else 'error'}">
                    <h2>{status}</h2>
                </div>
                
                {f'''
                <div class="qr-section">
                    <h3>📱 Codi QR Generat</h3>
                    <img src="data:image/png;base64,{img_base64}" alt="Codi QR" class="qr-image">
                    <p>Escaneja aquest QR amb el teu mòbil</p>
                </div>
                
                <div>
                    <h3>📋 Dades del QR:</h3>
                    <pre>{json.dumps(qr_data, indent=2, ensure_ascii=False)}</pre>
                </div>
                ''' if img_base64 else ''}
                
                <div style="margin-top: 30px;">
                    <a href="{self.context.absolute_url()}/qr_scanner" class="btn">📷 Provar Escàner QR</a>
                    <a href="{self.context.absolute_url()}" class="btn">← Tornar</a>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #e7f3ff; border-radius: 8px;">
                    <h4>ℹ️ Informació del sistema:</h4>
                    <ul>
                        <li><strong>Libreria qrcode:</strong> Instal·lada i funcionant</li>
                        <li><strong>Dependències:</strong> PIL/Pillow disponible</li>
                        <li><strong>Generació:</strong> Base64 per embedding</li>
                        <li><strong>Format:</strong> JSON amb dades d'inscripció</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html