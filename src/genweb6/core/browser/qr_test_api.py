"""Vista per testejar l'API de validació QR"""

from Products.Five.browser import BrowserView
from plone import api
import json


class QRTestAPIView(BrowserView):
    """Vista per testejar l'API"""
    
    def __call__(self):
        """Testa l'API de validació"""
        
        self.request.response.setHeader('Content-Type', 'text/html; charset=utf-8')
        
        # Buscar inscripció demo
        inscripcions = self.context.listFolderContents(
            contentFilter={'portal_type': 'Inscripcio'}
        )
        
        inscripcio_demo = None
        for inscripcio in inscripcions:
            if inscripcio.email == 'demo@upc.edu':
                inscripcio_demo = inscripcio
                break
        
        if not inscripcio_demo:
            return """
            <html><body>
                <h1>Error</h1>
                <p>No s'ha trobat la inscripció demo. Ves primer a @@qr_simple_demo</p>
                <a href="@@qr_simple_demo">Crear Demo</a>
            </body></html>
            """
        
        # Dades de test
        qr_data = {
            "type": "upcarts_inscripcio",
            "activitat_id": self.context.UID(),
            "inscripcio_id": inscripcio_demo.UID(),
            "activitat_title": self.context.title,
            "nom": f"{inscripcio_demo.nom} {inscripcio_demo.cognoms}",
            "email": inscripcio_demo.email,
            "collectiu": inscripcio_demo.collectiu
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Test API QR</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                button {{ 
                    background: #007bff; color: white; border: none; 
                    padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; 
                }}
                button:hover {{ background: #0056b3; }}
                .result {{ 
                    margin: 20px 0; padding: 15px; border-radius: 5px; 
                    background: #f8f9fa; border: 1px solid #dee2e6;
                }}
                .success {{ background: #d4edda; border-color: #c3e6cb; }}
                .error {{ background: #f8d7da; border-color: #f5c6cb; }}
                pre {{ background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 Test API QR</h1>
                
                <h3>📋 Dades de Test:</h3>
                <pre>{json.dumps(qr_data, indent=2, ensure_ascii=False)}</pre>
                
                <button onclick="testAPI()">🚀 Test API</button>
                <button onclick="testGET()">📄 Test GET</button>
                <button onclick="window.location.href='@@qr_simple_demo'">🎫 Tornar al Demo</button>
                
                <div id="result" class="result" style="display:none;"></div>
                
                <script>
                    const qrData = {json.dumps(qr_data)};
                    const apiUrl = '{self.context.absolute_url()}/@@qr_validation';
                    
                    function showResult(type, content) {{
                        const result = document.getElementById('result');
                        result.className = 'result ' + type;
                        result.style.display = 'block';
                        result.innerHTML = content;
                    }}
                    
                    async function testAPI() {{
                        console.log('🚀 Testejant API POST...');
                        console.log('URL:', apiUrl);
                        console.log('Dades:', qrData);
                        
                        try {{
                            showResult('', '⏳ Enviant petició...');
                            
                            const response = await fetch(apiUrl, {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                }},
                                body: JSON.stringify(qrData)
                            }});
                            
                            console.log('Response status:', response.status);
                            console.log('Response headers:', [...response.headers.entries()]);
                            
                            const result = await response.text();
                            console.log('Response text:', result);
                            
                            try {{
                                const jsonResult = JSON.parse(result);
                                showResult('success', 
                                    '<h3>✅ Resposta API (Status: ' + response.status + ')</h3>' +
                                    '<pre>' + JSON.stringify(jsonResult, null, 2) + '</pre>'
                                );
                            }} catch (e) {{
                                showResult('error', 
                                    '<h3>❌ Resposta no és JSON (Status: ' + response.status + ')</h3>' +
                                    '<pre>' + result + '</pre>'
                                );
                            }}
                            
                        }} catch (error) {{
                            console.error('Error:', error);
                            showResult('error', 
                                '<h3>🚨 Error de Connexió</h3>' +
                                '<p>' + error.message + '</p>'
                            );
                        }}
                    }}
                    
                    async function testGET() {{
                        console.log('📄 Testejant API GET...');
                        
                        try {{
                            showResult('', '⏳ Enviant GET...');
                            
                            const response = await fetch(apiUrl, {{
                                method: 'GET'
                            }});
                            
                            const result = await response.text();
                            console.log('GET Response:', result);
                            
                            try {{
                                const jsonResult = JSON.parse(result);
                                showResult('success', 
                                    '<h3>📄 GET Response (Status: ' + response.status + ')</h3>' +
                                    '<pre>' + JSON.stringify(jsonResult, null, 2) + '</pre>'
                                );
                            }} catch (e) {{
                                showResult('error', 
                                    '<h3>❌ GET Resposta no és JSON (Status: ' + response.status + ')</h3>' +
                                    '<pre>' + result + '</pre>'
                                );
                            }}
                            
                        }} catch (error) {{
                            console.error('GET Error:', error);
                            showResult('error', 
                                '<h3>🚨 GET Error</h3>' +
                                '<p>' + error.message + '</p>'
                            );
                        }}
                    }}
                </script>
            </div>
        </body>
        </html>
        """
        
        return html