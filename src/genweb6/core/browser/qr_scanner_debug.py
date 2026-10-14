"""Escàner QR amb debug complet"""

from Products.Five.browser import BrowserView


class QRScannerDebugView(BrowserView):
    """Escàner QR amb informació de debug"""
    
    def __call__(self):
        """Retorna HTML de l'escàner amb debug"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Debug Escàner QR - UPCArts</title>
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
                .debug-info {{
                    background: #e9ecef;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    font-family: monospace;
                    font-size: 12px;
                }}
                #qr-reader {{ 
                    width: 100%; 
                    max-width: 500px; 
                    margin: 20px auto; 
                    display: block;
                    min-height: 300px;
                    border: 2px dashed #ccc;
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Debug Escàner QR</h1>
                
                <div id="debug-info" class="debug-info">
                    <strong>Debug Info:</strong><br>
                    Navegador: <span id="browser-info"></span><br>
                    HTTPS: <span id="https-info"></span><br>
                    Llibreria Html5Qrcode: <span id="lib-info">Carregant...</span><br>
                    Càmeres disponibles: <span id="cameras-info">Detectant...</span><br>
                </div>
                
                <div class="controls">
                    <button id="check-cameras" class="btn" onclick="checkCameras()">🔍 Detectar Càmeres</button>
                    <button id="start-btn" class="btn" onclick="startScanner()">🎥 Iniciar Escàner</button>
                    <button id="stop-btn" class="btn" onclick="stopScanner()" style="display: none;">⏹️ Aturar</button>
                </div>
                
                <div id="qr-reader"></div>
                
                <div id="result" class="result" style="display: none;">
                    <h3 id="result-title"></h3>
                    <div id="result-content"></div>
                </div>
                
                <div class="debug-info">
                    <strong>Test QR:</strong> Pots provar amb aquest text simulat:<br>
                    <button class="btn" onclick="simulateQR()">🧪 Simular QR</button>
                </div>
                
                <a href="{self.context.absolute_url()}" class="back-link">← Tornar a l'activitat</a>
            </div>
            
            <script>
                // Debug info inicial
                document.getElementById('browser-info').textContent = navigator.userAgent;
                document.getElementById('https-info').textContent = location.protocol === 'https:' ? 'SÍ' : 'NO (requerit per càmera)';
                
                let html5QrCode = null;
                let isScanning = false;
                
                function log(message) {{
                    console.log(message);
                    const debugInfo = document.getElementById('debug-info');
                    debugInfo.innerHTML += '<br>' + new Date().toLocaleTimeString() + ': ' + message;
                }}
                
                function showResult(resultType, title, content) {{
                    const result = document.getElementById('result');
                    const resultTitle = document.getElementById('result-title');
                    const resultContent = document.getElementById('result-content');
                    
                    result.className = `result ${{resultType}}`;
                    result.style.display = 'block';
                    resultTitle.textContent = title;
                    resultContent.innerHTML = content;
                    
                    log(`Resultat: ${{resultType}} - ${{title}}`);
                }}
                
                function checkCameras() {{
                    log('Detectant càmeres...');
                    
                    if (typeof Html5Qrcode === 'undefined') {{
                        document.getElementById('cameras-info').textContent = 'Html5Qrcode no disponible';
                        log('ERROR: Html5Qrcode no està carregat');
                        return;
                    }}
                    
                    Html5Qrcode.getCameras().then(cameras => {{
                        log(`Trobades ${{cameras.length}} càmeres`);
                        document.getElementById('cameras-info').textContent = `${{cameras.length}} trobades`;
                        
                        cameras.forEach((camera, index) => {{
                            log(`Càmera ${{index}}: ${{camera.label || camera.id}}`);
                        }});
                        
                        if (cameras.length === 0) {{
                            showResult('error', 'Cap Càmera', 'No s\'han detectat càmeres disponibles');
                        }}
                    }}).catch(err => {{
                        log(`ERROR detectant càmeres: ${{err}}`);
                        document.getElementById('cameras-info').textContent = 'Error: ' + err.message;
                        showResult('error', 'Error Càmeres', err.message);
                    }});
                }}
                
                function simulateQR() {{
                    const testData = {{
                        "type": "upcarts_inscripcio",
                        "activitat_id": "test-123",
                        "inscripcio_id": "inscripcio-456",
                        "activitat_title": "Test Simulat",
                        "nom": "Usuari de Prova",
                        "email": "prova@upc.edu",
                        "collectiu": "ESTUDIANT"
                    }};
                    
                    processQRResult(JSON.stringify(testData));
                }}
                
                function processQRResult(decodedText) {{
                    log(`QR llegit: ${{decodedText}}`);
                    
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
                        log(`ERROR parsejant JSON: ${{e}}`);
                        showResult('error', '❌ Error de Format', 'El QR no conté dades vàlides JSON: ' + e.message);
                    }}
                }}
                
                function startScanner() {{
                    log('Iniciant escàner...');
                    
                    if (typeof Html5Qrcode === 'undefined') {{
                        showResult('error', 'Error Llibreria', 'Html5Qrcode no està disponible');
                        return;
                    }}
                    
                    if (isScanning) {{
                        log('Escàner ja està actiu');
                        return;
                    }}
                    
                    try {{
                        html5QrCode = new Html5Qrcode("qr-reader");
                        log('Html5Qrcode creat correctament');
                        
                        const config = {{
                            fps: 10,
                            qrbox: {{ width: 250, height: 250 }}
                        }};
                        
                        html5QrCode.start(
                            {{ facingMode: "environment" }},
                            config,
                            processQRResult,
                            (errorMessage) => {{
                                // Ignorar errors de no trobar QR
                            }}
                        ).then(() => {{
                            log('Escàner iniciat correctament');
                            isScanning = true;
                            document.getElementById('start-btn').style.display = 'none';
                            document.getElementById('stop-btn').style.display = 'inline-block';
                            showResult('success', '✅ Càmera Activa', 'Apunta la càmera cap al codi QR');
                        }}).catch(err => {{
                            log(`ERROR iniciant escàner: ${{err}}`);
                            showResult('error', '❌ Error Càmera', 
                                `No s'ha pogut iniciar: ${{err.message || err}}<br><br>
                                <strong>Possibles solucions:</strong><br>
                                • Dona permisos de càmera<br>
                                • Utilitza HTTPS<br>
                                • Tanca altres apps que usin la càmera`);
                        }});
                        
                    }} catch (err) {{
                        log(`ERROR creant Html5Qrcode: ${{err}}`);
                        showResult('error', 'Error Inicialització', err.message);
                    }}
                }}
                
                function stopScanner() {{
                    if (!html5QrCode || !isScanning) return;
                    
                    html5QrCode.stop().then(() => {{
                        log('Escàner aturat');
                        isScanning = false;
                        document.getElementById('start-btn').style.display = 'inline-block';
                        document.getElementById('stop-btn').style.display = 'none';
                    }}).catch(err => {{
                        log(`ERROR aturant: ${{err}}`);
                    }});
                }}
                
                // Carregar i verificar llibreria
                window.addEventListener('load', () => {{
                    setTimeout(() => {{
                        if (typeof Html5Qrcode !== 'undefined') {{
                            document.getElementById('lib-info').textContent = 'Carregada correctament';
                            log('Html5Qrcode carregat correctament');
                            checkCameras();
                        }} else {{
                            document.getElementById('lib-info').textContent = 'ERROR: No carregada';
                            log('ERROR: Html5Qrcode no s\'ha carregat');
                            showResult('error', 'Error Llibreria', 'No s\'ha pogut carregar Html5Qrcode');
                        }}
                    }}, 1000);
                }});
            </script>
            
            <!-- Carregar Html5Qrcode -->
            <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js" 
                    onload="console.log('Html5Qrcode script carregat')"
                    onerror="console.error('Error carregant Html5Qrcode')"></script>
        </body>
        </html>
        """
        
        return html