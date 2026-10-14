# Sistema QR per UPCArts - Prova de Concepte

Aquest document descriu la implementació completa del sistema de codis QR per a les inscripcions d'activitats UPCArts en Plone 6 Classic.

## Funcionalitats Implementades

### ✅ Content Types
- **Activitat**: Nou content type amb camps per inscripcions i Passaport Cultural
- **Inscripcio**: Content type per gestionar inscripcions amb dades personals i QR

### ✅ Generació QR
- Utilitat `QRGenerator` que crea codis QR amb dades JSON
- Imatges QR en format base64 per facilitar l'enviament per email
- Validació de format i integritat dels codis QR

### ✅ API REST
- Endpoint `/++api++/qr_validation` per validar QR i registrar assistència
- Endpoint `/++api++/qr_stats` per obtenir estadístiques d'assistència
- Respostes JSON amb informació detallada

### ✅ Escàner Web
- Pàgina `/qr_scanner` que utilitza la càmera del dispositiu
- Llibreria `html5-qrcode` per llegir codis QR
- Interfície responsive per mòbils i tablets
- Estadístiques en temps real

### ✅ Formulari d'Inscripció
- Pàgina `/inscripcio_form` amb tots els camps requerits
- Validació de duplicats per email
- Generació automàtica de QR després de la inscripció
- Pàgina de confirmació amb QR visible

## Estructura de Fitxers Creats

```
genweb6.core/src/genweb6/core/
├── content/
│   ├── activitat.py          # Content type Activitat
│   └── inscripcio.py         # Content type Inscripcio
├── utils/
│   └── qr_generator.py       # Utilitat per generar QR
├── api/
│   └── qr_validation.py      # API REST per validació
├── browser/
│   ├── qr_scanner.py         # Vista escàner QR
│   ├── qr_scanner.pt         # Template escàner
│   ├── inscripcio_form.py    # Formulari inscripció
│   ├── inscripcio_form.pt    # Template formulari
│   ├── inscripcio_confirmacio.pt # Template confirmació
│   └── qr_system.zcml        # Configuració ZCML
└── profiles/default/types/
    ├── types.xml             # Registre content types
    ├── Activitat.xml         # Configuració Activitat
    └── Inscripcio.xml        # Configuració Inscripcio
```

## Instal·lació i Configuració

### 1. Dependències
```bash
pip install qrcode[pil]==7.4.2
```

### 2. Configuració ZCML
Afegir a `configure.zcml` principal:
```xml
<include package=".browser" file="qr_system.zcml" />
```

### 3. Actualitzar Profile
Executar l'upgrade del profile de genweb6.core per crear els nous content types.

## Com Provar el Sistema

### 1. Crear una Activitat
1. Anar a "Afegir nou" → "Activitat UPCArts"
2. Omplir els camps bàsics (títol, descripció, data)
3. Marcar "Permet inscripcions" = True
4. Opcionalment marcar "Passaport Cultural" i hores
5. Guardar

### 2. Provar la Inscripció
1. Anar a la pàgina de l'activitat
2. Clicar "Inscriure's" (apareix si permet_inscripcions=True)
3. Omplir el formulari amb dades de prova
4. Enviar → Redirigeix a pàgina de confirmació amb QR

### 3. Provar l'Escàner QR
1. Anar a `/qr_scanner` des de qualsevol pàgina
2. Clicar "Iniciar Escàner" (cal permisos de càmera)
3. Apuntar la càmera al QR generat
4. Veure com es registra l'assistència automàticament

### 4. Verificar Estadístiques
1. Després d'escanejar un QR, les estadístiques apareixen automàticament
2. També es pot accedir via API: `/++api++/qr_stats?activitat_uid=XXX`

## Format del Codi QR

Els codis QR contenen JSON amb aquesta estructura:
```json
{
  "type": "upcarts_inscripcio",
  "activitat_id": "uuid-activitat",
  "inscripcio_id": "uuid-inscripcio", 
  "activitat_title": "Nom activitat",
  "nom": "Nom Cognoms",
  "email": "email@upc.edu",
  "collectiu": "ESTUDIANT",
  "data_inscripcio": "2026-03-05T10:30:00",
  "timestamp": "2026-03-05T10:30:15"
}
```

## URLs Disponibles

- `/inscripcio_form` - Formulari d'inscripció (només en activitats)
- `/inscripcio_confirmacio?inscripcio_id=XXX` - Confirmació amb QR
- `/qr_scanner` - Escàner de codis QR
- `/qr_validate_ajax` - Validació AJAX de QR
- `/qr_stats_ajax?activitat_uid=XXX` - Estadístiques AJAX
- `/++api++/qr_validation` - API REST validació
- `/++api++/qr_stats` - API REST estadístiques

## Característiques Tècniques

### Seguretat
- Validació de format JSON dels QR
- Verificació que la inscripció pertany a l'activitat
- Control de duplicats d'assistència
- Timestamps per auditoria

### Compatibilitat Mòbil
- Interfície responsive
- Accés automàtic a càmera en dispositius mòbils
- Llibreria html5-qrcode optimitzada per mòbils
- Funciona amb HTTPS (requerit per accés a càmera)

### Rendiment
- Codis QR generats una sola vegada i guardats
- Imatges en base64 per evitar fitxers addicionals
- AJAX per validacions ràpides sense recarregar pàgina
- Caching automàtic de Plone per a les vistes

## Possibles Millores Futures

1. **Integració Email**: Configurar SMTP real per enviar QR per email
2. **Notificacions Push**: Avisos automàtics als organitzadors
3. **Exportació Dades**: CSV/Excel de les inscripcions i assistència
4. **App Mòbil**: App nativa per escanejar QR més ràpidament
5. **Integració Calendari**: Sincronització amb Google Calendar/Outlook
6. **Pagaments**: Integració amb plataformes de pagament
7. **Llistes d'Espera**: Gestió de places limitades

## Suport i Resolució de Problemes

### Error: "No s'ha pogut accedir a la càmera"
- Verificar que el lloc utilitza HTTPS
- Donar permisos de càmera al navegador
- Provar amb un navegador diferent

### Error: "QR no vàlid"
- Verificar que el QR és del tipus correcte
- Comprovar que no està corrupte o parcialment llegit
- Assegurar-se que la inscripció existeix

### Error: "Inscripció no trobada"
- Verificar que l'UID de la inscripció és correcte
- Comprovar que no s'ha eliminat la inscripció
- Revisar els permisos d'accés

Aquest sistema proporciona una base sòlida per implementar el sistema complet descrit als requeriments UPCArts.