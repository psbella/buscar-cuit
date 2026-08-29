# buscar-cuit

Prototipo básico: buscador de CUIT (nombre, CUIT, domicilio, datos fiscales)
usando datos del padrón de ARCA (ex AFIP).

## ⚠️ Estado del proyecto

Esto es un **prototipo para probar la idea**, no una base de producción:

- Usa el endpoint REST **no oficial** de ARCA (`soa.afip.gob.ar/sr-padron/v2`),
  que es experimental, no documentado, y puede fallar o cambiar sin aviso.
- Sin caché, sin rate limiting propio, sin manejo de reintentos.
- Alcance de datos: **solo información pública** (padrón de ARCA) — nivel 1
  del proyecto más amplio. No incluye BCRA, datos crediticios ni nada que
  requiera verificación de interés legítimo (ver notas del proyecto).

Antes de exponerlo a otras personas o depender de él, migrar al webservice
SOAP oficial (WSAA + `ws_sr_padron_a5`/`a13`) o a un proveedor que lo envuelva.

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

Abrí `http://127.0.0.1:5000` en el navegador, ingresá un CUIT (11 dígitos,
sin guiones) y buscá.

## Estructura

```
buscar-cuit/
├── app.py             # servidor Flask (web + API)
├── cuit_lookup.py      # lógica de consulta a ARCA (reutilizable)
├── requirements.txt
├── templates/
│   └── index.html      # frontend
└── static/
    └── style.css
```

## API

`GET /api/cuit/<cuit>` → JSON:

```json
{
  "ok": true,
  "resultado": {
    "nombre": "...",
    "cuit": "...",
    "tipo_persona": "...",
    "estado": "...",
    "domicilio": { "direccion": "...", "localidad": "...", "provincia": "...", "codigo_postal": "..." },
    "datos_fiscales": { "condicion_iva": "...", "actividades": ["..."] }
  }
}
```

En caso de error: `{"ok": false, "error": "..."}` con status 400 (CUIT
inválido) o 502 (falla al consultar ARCA).
