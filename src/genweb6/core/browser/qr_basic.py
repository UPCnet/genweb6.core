"""Escàner QR ultra bàsic que funciona"""

from Products.Five.browser import BrowserView


class QRBasicView(BrowserView):
    """Escàner QR ultra simple"""
    
    def __call__(self):
        """Retorna HTML ultra bàsic"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>QR Bàsic</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                button {{ 
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 15px 25px; 
                    margin: 10px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    font-size: 16px;
                }}
                button:hover {{ background: #0056b3; }}
                #result {{ 
                    margin: 20px 0; 
                    padding: 15px; 
                    background: #f8f9fa; 
                    border-radius: 5px; 
                    display: none;
                }}
                #result.success {{ background: #d4edda; color: #155724; }}
                #result.error {{ background: #f8d7da; color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 Test QR Bàsic</h1>
                
                <p><strong>Navegador:</strong> <span id="browser-info"></span></p>
                <p><strong>JavaScript:</strong> <span id="js-status">Carregant...</span></p>
                
                <button onclick="testBasic()">Test JavaScript</button>
                <button onclick="simulateQR()">Simular QR</button>
                <button onclick="showAlert()">Test Alert</button>
                
                <div id="result"></div>
                
                <a href="{self.context.absolute_url()}">← Tornar</a>
                
                <script>
                    // Test bàsic JavaScript
                    console.log('JavaScript carregat');
                    
                    // Informació del navegador
                    document.getElementById('browser-info').textContent = navigator.userAgent.split(' ')[0];
                    document.getElementById('js-status').textContent = 'Funcionant ✅';
                    
                    function showResult(type, message) {{
                        const result = document.getElementById('result');
                        result.className = type;
                        result.style.display = 'block';
                        result.innerHTML = '<h3>' + type.toUpperCase() + '</h3><p>' + message + '</p>';
                        console.log(type + ': ' + message);
                    }}
                    
                    function testBasic() {{
                        console.log('Test bàsic executat');
                        showResult('success', 'JavaScript funciona correctament!<br>Data: ' + new Date().toLocaleString());
                    }}
                    
                    function simulateQR() {{
                        console.log('Simulant QR...');
                        
                        const qrData = {{
                            "type": "upcarts_inscripcio",
                            "activitat_id": "test-basic",
                            "inscripcio_id": "basic-456",
                            "activitat_title": "Test Bàsic",
                            "nom": "Usuari Test",
                            "email": "test@upc.edu",
                            "collectiu": "ESTUDIANT"
                        }};
                        
                        try {{
                            const jsonString = JSON.stringify(qrData);
                            console.log('QR JSON:', jsonString);
                            
                            // Simular processament
                            showResult('success', 
                                '<strong>✅ QR Processat Correctament!</strong><br><br>' +
                                '<strong>Activitat:</strong> ' + qrData.activitat_title + '<br>' +
                                '<strong>Participant:</strong> ' + qrData.nom + '<br>' +
                                '<strong>Email:</strong> ' + qrData.email + '<br>' +
                                '<strong>Col·lectiu:</strong> ' + qrData.collectiu + '<br>' +
                                '<strong>Hora registre:</strong> ' + new Date().toLocaleString()
                            );
                        }} catch (e) {{
                            console.error('Error:', e);
                            showResult('error', 'Error processant QR: ' + e.message);
                        }}
                    }}
                    
                    function showAlert() {{
                        alert('Test Alert: JavaScript funciona!');
                        console.log('Alert mostrat');
                    }}
                    
                    // Test automàtic en carregar
                    window.addEventListener('load', function() {{
                        console.log('Pàgina carregada completament');
                        setTimeout(function() {{
                            console.log('Test automàtic després de 2 segons');
                        }}, 2000);
                    }});
                </script>
            </div>
        </body>
        </html>
        """
        
        return html