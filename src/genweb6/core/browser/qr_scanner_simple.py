"""Escàner QR simplificat que funciona"""

from Products.Five.browser import BrowserView
import json


class QRScannerSimpleView(BrowserView):
    """Escàner QR simple sense templates problemàtics"""
    
    def __call__(self):
        """Retorna HTML de l'escàner directament"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Escàner QR - UPCArts</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f5f5f5;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ 
                    text-align: center; 
                    color: #007bff; 
                    margin-bottom: 30px;
                }}
                #qr-reader {{ 
                    width: 100%; 
                    max-width: 500px; 
                    margin: 20px auto; 
                    display: block;
                }}
                .controls {{ 
                    text-align: center; 
                    margin: 20px 0; 
                }}
                .btn {{ 
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 12px 24px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    font-size: 16px; 
                    margin: 5px;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn:disabled {{ 
                    background: #6c757d; 
                    cursor: not-allowed; 
                }}
                .result {{ 
                    margin: 20px 0; 
                    padding: 15px; 
                    border-radius: 5px; 
                    display: none;
                }}
                .result.success {{ 
                    background: #d4edda; 
                    border: 1px solid #c3e6cb; 
                    color: #155724; 
                }}
                .result.error {{ 
                    background: #f8d7da; 
                    border: 1px solid #f5c6cb; 
                    color: #721c24; 
                }}
                .result.warning {{ 
                    background: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    color: #856404; 
                }}
                .back-link {{ 
                    display: inline-block; 
                    margin-top: 20px; 
                    color: #007bff; 
                    text-decoration: none; 
                }}
                .back-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📱 Escàner QR UPCArts</h1>
                
                <div class="controls">
                    <button id="start-btn" class="btn" onclick="startScanner()">🎥 Iniciar Càmera</button>
                    <button id="stop-btn" class="btn" onclick="stopScanner()" style="display: none;">⏹️ Aturar</button>
                </div>
                
                <div id="qr-reader"></div>
                
                <div id="result" class="result">
                    <h3 id="result-title"></h3>
                    <div id="result-content"></div>
                </div>
                
                <a href="{self.context.absolute_url()}" class="back-link">← Tornar a l'activitat</a>
            </div>
            
            <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
            <script>
                let html5QrCode = null;
                let isScanning = false;
                
                function showResult(resultType, title, content) {{
                    const result = document.getElementById('result');
                    const resultTitle = document.getElementById('result-title');
                    const resultContent = document.getElementById('result-content');
                    
                    result.className = `result ${{resultType}}`;
                    result.style.display = 'block';
                    resultTitle.textContent = title;
                    resultContent.innerHTML = content;
                    
                    result.scrollIntoView({{ behavior: 'smooth' }});
                }}
                
                function processQRResult(decodedText) {{
                    console.log('QR llegit:', decodedText);
                    
                    showResult('warning', 'Processant...', 'Validant el codi QR...');
                    
                    // Simular validació (en producció seria una crida AJAX real)
                    setTimeout(() => {{
                        try {{
                            const qrData = JSON.parse(decodedText);
                            
                            if (qrData.type === 'upcarts_inscripcio') {{
                                showResult('success', 
                                    '✅ Assistència Registrada!', 
                                    `
                                    <strong>Activitat:</strong> ${{qrData.activitat_title || 'N/A'}}<br>
                                    <strong>Participant:</strong> ${{qrData.nom || 'N/A'}}<br>
                                    <strong>Email:</strong> ${{qrData.email || 'N/A'}}<br>
                                    <strong>Col·lectiu:</strong> ${{qrData.collectiu || 'N/A'}}<br>
                                    <strong>Hora registre:</strong> ${{new Date().toLocaleString('ca-ES')}}
                                    `
                                );
                            }} else {{
                                showResult('error', '❌ QR No Vàlid', 'Aquest QR no és per a inscripcions UPCArts');
                            }}
                        }} catch (e) {{
                            showResult('error', '❌ Error de Format', 'El QR no conté dades vàlides JSON');
                        }}
                    }}, 1000);
                }}
                
                function startScanner() {{
                    if (isScanning) return;
                    
                    html5QrCode = new Html5Qrcode("qr-reader");
                    
                    const config = {{
                        fps: 10,
                        qrbox: {{ width: 250, height: 250 }},
                        aspectRatio: 1.0
                    }};
                    
                    html5QrCode.start(
                        {{ facingMode: "environment" }},
                        config,
                        processQRResult,
                        (errorMessage) => {{
                            // Ignorar errors de no trobar QR
                        }}
                    ).then(() => {{
                        isScanning = true;
                        document.getElementById('start-btn').style.display = 'none';
                        document.getElementById('stop-btn').style.display = 'inline-block';
                        showResult('warning', 'Càmera Activa', 'Apunta la càmera cap al codi QR per escanejar');
                    }}).catch(err => {{
                        console.error('Error:', err);
                        showResult('error', 'Error de Càmera', 
                            'No s\'ha pogut accedir a la càmera. Assegura\'t de donar permisos i utilitzar HTTPS.');
                    }});
                }}
                
                function stopScanner() {{
                    if (!isScanning || !html5QrCode) return;
                    
                    html5QrCode.stop().then(() => {{
                        isScanning = false;
                        document.getElementById('start-btn').style.display = 'inline-block';
                        document.getElementById('stop-btn').style.display = 'none';
                        
                        const result = document.getElementById('result');
                        result.style.display = 'none';
                    }}).catch(err => {{
                        console.error('Error aturant:', err);
                    }});
                }}
                
                // Auto-iniciar en dispositius mòbils
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {{
                    window.addEventListener('load', () => {{
                        setTimeout(() => {{
                            if (!isScanning) startScanner();
                        }}, 1000);
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        return html