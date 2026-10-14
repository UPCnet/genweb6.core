"""Escàner QR final que funciona amb càmera"""

from Products.Five.browser import BrowserView


class QRScannerFinalView(BrowserView):
    """Escàner QR final amb càmera real"""
    
    def __call__(self):
        """Retorna HTML amb escàner funcional"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📱 Escàner QR UPCArts</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    margin: 0;
                    background: #f8f9fa;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #007bff; text-align: center; }}
                button {{ 
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 15px 25px; 
                    margin: 10px 5px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    font-size: 16px;
                    width: 100%;
                    max-width: 200px;
                }}
                button:hover {{ background: #0056b3; }}
                button:disabled {{ background: #6c757d; cursor: not-allowed; }}
                .success {{ background: #28a745 !important; }}
                .danger {{ background: #dc3545 !important; }}
                
                #scanner-container {{ 
                    margin: 20px 0; 
                    text-align: center;
                }}
                #qr-reader {{ 
                    width: 100%; 
                    max-width: 400px; 
                    margin: 0 auto;
                    border: 2px solid #007bff;
                    border-radius: 10px;
                    overflow: hidden;
                }}
                #result {{ 
                    margin: 20px 0; 
                    padding: 15px; 
                    border-radius: 5px; 
                    display: none;
                }}
                #result.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                #result.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                #result.info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
                
                .status {{ 
                    padding: 10px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                    background: #e9ecef;
                }}
                .buttons {{ text-align: center; }}
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
                
                <div class="status">
                    <strong>Status:</strong> <span id="status">Inicialitzant...</span><br>
                    <strong>Càmera:</strong> <span id="camera-status">No detectada</span><br>
                    <strong>Llibreria:</strong> <span id="lib-status">Carregant...</span>
                </div>
                
                <div class="buttons">
                    <button id="test-btn" onclick="testFunction()">🧪 Test</button>
                    <button id="simulate-btn" onclick="simulateQR()">🎭 Simular</button>
                    <button id="camera-btn" onclick="startCamera()" disabled>📷 Iniciar Càmera</button>
                    <button id="stop-btn" onclick="stopCamera()" disabled style="display:none;">⏹️ Aturar</button>
                </div>
                
                <div id="scanner-container">
                    <div id="qr-reader"></div>
                </div>
                
                <div id="result"></div>
                
                <a href="{self.context.absolute_url()}" class="back-link">← Tornar a l'activitat</a>
            </div>

            <!-- Html5Qrcode Library -->
            <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
            
            <script>
                let html5QrCode = null;
                let isScanning = false;
                
                // Elements
                const statusEl = document.getElementById('status');
                const cameraStatusEl = document.getElementById('camera-status');
                const libStatusEl = document.getElementById('lib-status');
                const resultEl = document.getElementById('result');
                const cameraBtn = document.getElementById('camera-btn');
                const stopBtn = document.getElementById('stop-btn');
                
                console.log('🚀 Iniciant escàner QR...');
                
                // Funcions d'utilitat
                function updateStatus(message) {{
                    statusEl.textContent = message;
                    console.log('Status:', message);
                }}
                
                function showResult(type, title, message) {{
                    resultEl.className = type;
                    resultEl.style.display = 'block';
                    resultEl.innerHTML = `<h3>${{title}}</h3><p>${{message}}</p>`;
                    console.log(type + ':', title, message);
                }}
                
                function hideResult() {{
                    resultEl.style.display = 'none';
                }}
                
                // Test bàsic
                function testFunction() {{
                    console.log('🧪 Test executat');
                    showResult('success', '✅ Test OK', 
                        'JavaScript funciona correctament!<br>' +
                        'Hora: ' + new Date().toLocaleString() + '<br>' +
                        'Navegador: ' + navigator.userAgent.split(' ')[0]
                    );
                }}
                
                // Simular lectura QR
                function simulateQR() {{
                    console.log('🎭 Simulant QR...');
                    hideResult();
                    
                    const qrData = {{
                        "type": "upcarts_inscripcio",
                        "activitat_id": "activitat-123",
                        "inscripcio_id": "inscripcio-456", 
                        "activitat_title": "Taller de Sostenibilitat",
                        "nom": "Maria García",
                        "email": "maria.garcia@upc.edu",
                        "collectiu": "ESTUDIANT"
                    }};
                    
                    const qrString = JSON.stringify(qrData);
                    console.log('📄 QR simulat:', qrString);
                    
                    // Processar QR simulat
                    processQRCode(qrString);
                }}
                
                // Processar codi QR llegit
                function processQRCode(qrCodeMessage) {{
                    console.log('🔍 Processant QR:', qrCodeMessage);
                    
                    try {{
                        const qrData = JSON.parse(qrCodeMessage);
                        
                        // Validar format UPCArts
                        if (qrData.type !== 'upcarts_inscripcio') {{
                            throw new Error('QR no és d\\'UPCArts');
                        }}
                        
                        // Enviar a API de validació
                        validateQRCode(qrData);
                        
                    }} catch (error) {{
                        console.error('❌ Error processant QR:', error);
                        showResult('error', '❌ QR Invàlid', 
                            'Error: ' + error.message + '<br>' +
                            'Contingut: ' + qrCodeMessage.substring(0, 100) + '...'
                        );
                    }}
                }}
                
                // Validar QR amb API
                async function validateQRCode(qrData) {{
                    console.log('🌐 Validant amb API...', qrData);
                    
                    showResult('info', '⏳ Validant...', 'Registrant assistència...');
                    
                    try {{
                        const apiUrl = '{self.context.absolute_url()}/@@qr_validation';
                        console.log('📡 URL API:', apiUrl);
                        console.log('📤 Enviant dades:', JSON.stringify(qrData, null, 2));
                        
                        const response = await fetch(apiUrl, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify(qrData)
                        }});
                        
                        console.log('📡 Response status:', response.status);
                        console.log('📡 Response headers:', response.headers);
                        
                        const result = await response.json();
                        console.log('📡 Resposta API:', result);
                        
                        if (result.success) {{
                            showResult('success', '✅ Assistència Registrada!', 
                                `<strong>Activitat:</strong> ${{qrData.activitat_title}}<br>` +
                                `<strong>Participant:</strong> ${{qrData.nom}}<br>` +
                                `<strong>Email:</strong> ${{qrData.email}}<br>` +
                                `<strong>Col·lectiu:</strong> ${{qrData.collectiu}}<br>` +
                                `<strong>Hora:</strong> ${{new Date().toLocaleString()}}<br>` +
                                `<strong>Missatge:</strong> ${{result.message || 'Registre completat'}}`
                            );
                        }} else {{
                            showResult('error', '❌ Error de Validació', 
                                result.message || 'No s\\'ha pogut validar el QR'
                            );
                        }}
                        
                    }} catch (error) {{
                        console.error('🚨 Error API:', error);
                        showResult('error', '🚨 Error de Connexió', 
                            'No s\\'ha pogut connectar amb el servidor.<br>' +
                            'Error: ' + error.message
                        );
                    }}
                }}
                
                // Iniciar càmera
                async function startCamera() {{
                    console.log('📷 Iniciant càmera...');
                    hideResult();
                    
                    if (isScanning) {{
                        console.log('⚠️ Ja s\\'està escanejant');
                        return;
                    }}
                    
                    try {{
                        updateStatus('Iniciant càmera...');
                        
                        html5QrCode = new Html5Qrcode("qr-reader");
                        
                        const config = {{
                            fps: 10,
                            qrbox: {{ width: 250, height: 250 }},
                            aspectRatio: 1.0
                        }};
                        
                        await html5QrCode.start(
                            {{ facingMode: "environment" }}, // Càmera posterior
                            config,
                            (decodedText, decodedResult) => {{
                                console.log('📱 QR llegit:', decodedText);
                                processQRCode(decodedText);
                                // No aturem l'escàner automàticament per permetre múltiples lectures
                            }},
                            (errorMessage) => {{
                                // Errors normals d'escaneig, no els mostrem
                                // console.log('Escaneig...', errorMessage);
                            }}
                        );
                        
                        isScanning = true;
                        updateStatus('Escàner actiu - Apunta la càmera al QR');
                        cameraStatusEl.textContent = 'Activa ✅';
                        
                        cameraBtn.style.display = 'none';
                        stopBtn.style.display = 'inline-block';
                        
                        showResult('info', '📷 Càmera Activa', 
                            'Apunta la càmera al codi QR per registrar assistència'
                        );
                        
                    }} catch (error) {{
                        console.error('❌ Error iniciant càmera:', error);
                        updateStatus('Error amb la càmera');
                        showResult('error', '❌ Error de Càmera', 
                            'No s\\'ha pogut accedir a la càmera.<br>' +
                            'Assegura\\'t que:<br>' +
                            '• Has donat permisos de càmera<br>' +
                            '• Estàs usant HTTPS o localhost<br>' +
                            '• La càmera no està en ús per altra app<br><br>' +
                            'Error: ' + error.message
                        );
                    }}
                }}
                
                // Aturar càmera
                async function stopCamera() {{
                    console.log('⏹️ Aturant càmera...');
                    
                    if (html5QrCode && isScanning) {{
                        try {{
                            await html5QrCode.stop();
                            html5QrCode = null;
                            isScanning = false;
                            
                            updateStatus('Càmera aturada');
                            cameraStatusEl.textContent = 'Aturada';
                            
                            cameraBtn.style.display = 'inline-block';
                            stopBtn.style.display = 'none';
                            
                            hideResult();
                            
                        }} catch (error) {{
                            console.error('Error aturant càmera:', error);
                        }}
                    }}
                }}
                
                // Inicialització
                window.addEventListener('load', function() {{
                    console.log('📄 Pàgina carregada');
                    
                    // Verificar si Html5Qrcode està disponible
                    setTimeout(() => {{
                        if (typeof Html5Qrcode !== 'undefined') {{
                            console.log('✅ Html5Qrcode carregat');
                            libStatusEl.textContent = 'Carregada ✅';
                            updateStatus('Llest per escanejar');
                            cameraBtn.disabled = false;
                            
                            // Verificar càmeres disponibles
                            Html5Qrcode.getCameras().then(cameras => {{
                                if (cameras && cameras.length > 0) {{
                                    console.log('📷 Càmeres detectades:', cameras.length);
                                    cameraStatusEl.textContent = `Detectada (${{cameras.length}}) ✅`;
                                }} else {{
                                    console.log('⚠️ No s\\'han detectat càmeres');
                                    cameraStatusEl.textContent = 'No detectada ⚠️';
                                }}
                            }}).catch(err => {{
                                console.error('Error detectant càmeres:', err);
                                cameraStatusEl.textContent = 'Error detectant ❌';
                            }});
                            
                        }} else {{
                            console.error('❌ Html5Qrcode no s\\'ha carregat');
                            libStatusEl.textContent = 'Error carregant ❌';
                            updateStatus('Error carregant llibreria');
                            showResult('error', '❌ Error de Llibreria', 
                                'No s\\'ha pogut carregar la llibreria d\\'escaneig QR.<br>' +
                                'Verifica la connexió a internet.'
                            );
                        }}
                    }}, 1000);
                }});
                
                // Gestió de sortida de pàgina
                window.addEventListener('beforeunload', function() {{
                    if (isScanning) {{
                        stopCamera();
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        return html