"""
cuit_lookup.py

Lógica de consulta al padrón de ARCA (ex AFIP) por CUIT.

Fuente: endpoint REST público NO oficial de ARCA:
    https://soa.afip.gob.ar/sr-padron/v2/persona/{cuit}

⚠️ Es experimental, no documentado oficialmente, y puede fallar o cambiar
sin aviso. Para producción, migrar al webservice SOAP oficial (WSAA +
ws_sr_padron_a5/a13) o a un proveedor que lo envuelva (ej. AfipSDK).
"""

import re
import requests

ENDPOINT = "https://soa.afip.gob.ar/sr-padron/v2/persona/{cuit}"
TIMEOUT_SEGUNDOS = 10


class CuitInvalido(ValueError):
    pass


class ConsultaError(RuntimeError):
    pass


def validar_cuit(cuit: str) -> str:
    """Deja solo dígitos y valida longitud básica (11 dígitos)."""
    limpio = re.sub(r"\D", "", cuit or "")
    if len(limpio) != 11:
        raise CuitInvalido(f"CUIT inválido: '{cuit}' — debe tener 11 dígitos (sin guiones).")
    return limpio


def consultar_cuit(cuit: str) -> dict:
    """Consulta el padrón y devuelve el dict 'data' de la respuesta."""
    cuit = validar_cuit(cuit)
    url = ENDPOINT.format(cuit=cuit)

    try:
        resp = requests.get(url, timeout=TIMEOUT_SEGUNDOS, headers={"User-Agent": "buscar-cuit/0.1"})
    except requests.RequestException as e:
        raise ConsultaError(
            "No se pudo contactar el endpoint de ARCA. Puede estar caído "
            "(es experimental) o hay un problema de red."
        ) from e

    if resp.status_code != 200:
        raise ConsultaError(f"ARCA respondió {resp.status_code}. ¿CUIT inexistente?")

    try:
        payload = resp.json()
    except ValueError as e:
        raise ConsultaError("Respuesta no es JSON válido — el endpoint puede haber cambiado.") from e

    data = payload.get("data")
    if not data:
        raise ConsultaError("El CUIT no devolvió datos (posiblemente no existe en el padrón).")
    return data


def formatear_dict(data: dict) -> dict:
    """Aplana la respuesta cruda a los 4 campos que nos interesan: nombre, cuit, domicilio, datos fiscales."""
    dom = data.get("domicilioFiscal", {}) or {}
    monotributo = data.get("monotributo", {}) or {}
    impuestos = data.get("impuestos", []) or []
    regimen_general = data.get("regimenGeneral", []) or []
    actividades = data.get("actividades", []) or []

    if monotributo:
        condicion_iva = "Monotributo"
    elif impuestos or regimen_general:
        condicion_iva = "Responsable Inscripto"
    else:
        condicion_iva = "Sin datos"

    return {
        "nombre": data.get("nombre", "—"),
        "cuit": data.get("idPersona", "—"),
        "tipo_persona": data.get("tipoPersona", "—"),
        "estado": data.get("estadoClave", "—"),
        "domicilio": {
            "direccion": dom.get("direccion", "—"),
            "localidad": dom.get("localidad", "—"),
            "provincia": dom.get("descripcionProvincia", dom.get("idProvincia", "—")),
            "codigo_postal": dom.get("codPostal", "—"),
        },
        "datos_fiscales": {
            "condicion_iva": condicion_iva,
            "actividades": [a.get("descripcionActividad", "—") for a in actividades],
        },
    }
