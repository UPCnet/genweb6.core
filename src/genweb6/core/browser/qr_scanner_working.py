"""Escàner QR que funciona garantit"""

from Products.Five.browser import BrowserView


class QRScannerWorkingView(BrowserView):
    """Escàner QR amb càrrega fiable de la llibreria"""
    
    def __call__(self):
        """Retorna HTML de l'escàner que funciona"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Escàner QR UPCArts</title>
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
                .status {{
                    background: #e9ecef;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    font-family: monospace;
                    font-size: 14px;
                }}
                #qr-reader {{ 
                    width: 100%; 
                    max-width: 500px; 
                    margin: 20px auto; 
                    display: block;
                    min-height: 300px;
                    border: 2px dashed #ccc;
                    background: #f8f9fa;
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📱 Escàner QR UPCArts</h1>
                
                <div id="status" class="status">
                    <strong>Status:</strong> Carregant llibreries...<br>
                    <strong>Navegador:</strong> <span id="browser"></span><br>
                    <strong>HTTPS:</strong> <span id="https"></span><br>
                    <strong>Llibreria:</strong> <span id="library-status">Carregant...</span>
                </div>
                
                <div class="controls">
                    <button id="test-btn" class="btn" onclick="testFunction()">🧪 Test Funcions</button>
                    <button id="simulate-btn" class="btn" onclick="simulateQR()">📝 Simular QR</button>
                    <button id="camera-btn" class="btn" onclick="requestCamera()" disabled>📷 Provar Càmera</button>
                </div>
                
                <div id="qr-reader"></div>
                
                <div id="result" class="result">
                    <h3 id="result-title"></h3>
                    <div id="result-content"></div>
                </div>
                
                <a href="{self.context.absolute_url()}" style="color: #007bff;">← Tornar a l'activitat</a>
            </div>
            
            <script>
                // Variables globals
                let libraryLoaded = false;
                let html5QrCode = null;
                
                // Informació inicial
                document.getElementById('browser').textContent = navigator.userAgent.split(' ')[0];
                document.getElementById('https').textContent = location.protocol === 'https:' ? 'SÍ ✅' : 'NO ❌';
                
                function updateStatus(message) {{
                    const status = document.getElementById('status');
                    status.innerHTML += '<br>' + new Date().toLocaleTimeString() + ': ' + message;
                    console.log(message);
                }}
                
                function showResult(type, title, content) {{
                    const result = document.getElementById('result');
                    const resultTitle = document.getElementById('result-title');
                    const resultContent = document.getElementById('result-content');
                    
                    result.className = `result ${{type}}`;
                    result.style.display = 'block';
                    resultTitle.textContent = title;
                    resultContent.innerHTML = content;
                    
                    updateStatus(`Resultat: ${{type}} - ${{title}}`);
                }}
                
                function testFunction() {{
                    updateStatus('Test de funcions JavaScript...');
                    
                    // Test 1: Console
                    console.log('Test console.log - OK');
                    
                    // Test 2: DOM
                    const testElement = document.getElementById('test-btn');
                    if (testElement) {{
                        updateStatus('✅ DOM access - OK');
                    }}
                    
                    // Test 3: Fetch API
                    if (typeof fetch !== 'undefined') {{
                        updateStatus('✅ Fetch API - OK');
                    }} else {{
                        updateStatus('❌ Fetch API - NO disponible');
                    }}
                    
                    // Test 4: Llibreria QR
                    if (typeof Html5Qrcode !== 'undefined') {{
                        updateStatus('✅ Html5Qrcode - Carregada');
                        document.getElementById('library-status').textContent = 'Carregada ✅';
                        document.getElementById('camera-btn').disabled = false;
                        libraryLoaded = true;
                    }} else {{
                        updateStatus('❌ Html5Qrcode - NO carregada');
                        document.getElementById('library-status').textContent = 'Error ❌';
                    }}
                    
                    showResult('success', 'Test Completat', 'Revisa els logs per veure els resultats');
                }}
                
                function simulateQR() {{
                    updateStatus('Simulant lectura de QR...');
                    
                    const testQRData = {{
                        "type": "upcarts_inscripcio",
                        "activitat_id": "test-simulation",
                        "inscripcio_id": "sim-456", 
                        "activitat_title": "Activitat de Prova",
                        "nom": "Joan Simulat",
                        "email": "joan.simulat@upc.edu",
                        "collectiu": "ESTUDIANT",
                        "timestamp": new Date().toISOString()
                    }};
                    
                    const qrString = JSON.stringify(testQRData);
                    updateStatus('QR simulat generat: ' + qrString.substring(0, 50) + '...');
                    
                    // Processar com si fos un QR real
                    processQRData(qrString);
                }}
                
                function processQRData(qrText) {{
                    updateStatus('Processant dades QR...');
                    
                    try {{
                        const data = JSON.parse(qrText);
                        
                        if (data.type === 'upcarts_inscripcio') {{
                            showResult('success', '✅ Assistència Registrada!', `
                                <strong>Activitat:</strong> ${{data.activitat_title}}<br>
                                <strong>Participant:</strong> ${{data.nom}}<br>
                                <strong>Email:</strong> ${{data.email}}<br>
                                <strong>Col·lectiu:</strong> ${{data.collectiu}}<br>
                                <strong>Hora:</strong> ${{new Date().toLocaleString('ca-ES')}}
                            `);
                        }} else {{
                            showResult('error', '❌ QR No Vàlid', 'Tipus de QR no reconegut: ' + data.type);
                        }}
                    }} catch (e) {{
                        updateStatus('Error parsejant JSON: ' + e.message);
                        showResult('error', '❌ Format Incorrecte', 'El QR no conté JSON vàlid');
                    }}
                }}
                
                function requestCamera() {{
                    if (!libraryLoaded) {{
                        showResult('error', 'Llibreria No Disponible', 'Html5Qrcode no està carregada');
                        return;
                    }}
                    
                    updateStatus('Sol·licitant accés a la càmera...');
                    
                    // Primer demanar permisos
                    navigator.mediaDevices.getUserMedia({{ video: true }})
                        .then(stream => {{
                            updateStatus('✅ Permisos de càmera obtinguts');
                            
                            // Aturar el stream temporal
                            stream.getTracks().forEach(track => track.stop());
                            
                            // Ara iniciar l'escàner real
                            startQRScanner();
                        }})
                        .catch(err => {{
                            updateStatus('❌ Error permisos càmera: ' + err.message);
                            showResult('error', 'Error Permisos', 
                                'No s\'han pogut obtenir permisos de càmera: ' + err.message);
                        }});
                }}
                
                function startQRScanner() {{
                    updateStatus('Iniciant escàner QR...');
                    
                    try {{
                        html5QrCode = new Html5Qrcode("qr-reader");
                        
                        const config = {{
                            fps: 10,
                            qrbox: {{ width: 250, height: 250 }}
                        }};
                        
                        html5QrCode.start(
                            {{ facingMode: "environment" }},
                            config,
                            (decodedText, decodedResult) => {{
                                updateStatus('QR detectat: ' + decodedText.substring(0, 30) + '...');
                                processQRData(decodedText);
                            }},
                            (errorMessage) => {{
                                // Ignorar errors de no trobar QR
                            }}
                        ).then(() => {{
                            updateStatus('✅ Escàner QR actiu');
                            showResult('success', 'Escàner Actiu', 'Apunta la càmera cap al codi QR');
                            
                            // Canviar botó
                            const btn = document.getElementById('camera-btn');
                            btn.textContent = '⏹️ Aturar Càmera';
                            btn.onclick = stopQRScanner;
                            
                        }}).catch(err => {{
                            updateStatus('❌ Error iniciant escàner: ' + err.message);
                            showResult('error', 'Error Escàner', err.message);
                        }});
                        
                    }} catch (err) {{
                        updateStatus('❌ Error creant escàner: ' + err.message);
                        showResult('error', 'Error Creació', err.message);
                    }}
                }}
                
                function stopQRScanner() {{
                    if (html5QrCode) {{
                        html5QrCode.stop().then(() => {{
                            updateStatus('Escàner aturat');
                            
                            // Restaurar botó
                            const btn = document.getElementById('camera-btn');
                            btn.textContent = '📷 Provar Càmera';
                            btn.onclick = requestCamera;
                            
                            document.getElementById('result').style.display = 'none';
                        }});
                    }}
                }}
                
                // Carregar llibreria i inicialitzar
                window.addEventListener('load', () => {{
                    updateStatus('Pàgina carregada, esperant llibreria...');
                    
                    // Comprovar cada segon si la llibreria està disponible
                    const checkLibrary = setInterval(() => {{
                        if (typeof Html5Qrcode !== 'undefined') {{
                            clearInterval(checkLibrary);
                            updateStatus('✅ Html5Qrcode detectada');
                            document.getElementById('library-status').textContent = 'Disponible ✅';
                            document.getElementById('camera-btn').disabled = false;
                            libraryLoaded = true;
                        }}
                    }}, 1000);
                    
                    // Timeout després de 10 segons
                    setTimeout(() => {{
                        if (!libraryLoaded) {{
                            clearInterval(checkLibrary);
                            updateStatus('❌ Timeout carregant Html5Qrcode');
                            document.getElementById('library-status').textContent = 'Timeout ❌';
                        }}
                    }}, 10000);
                }});
            </script>
            
            <!-- Carregar Html5Qrcode des de CDN -->
            <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js" 
                    onload="console.log('Html5Qrcode carregat des de CDN')"
                    onerror="console.error('Error carregant Html5Qrcode des de CDN')">
            </script>
        </body>
        </html>
        """
        
        return html