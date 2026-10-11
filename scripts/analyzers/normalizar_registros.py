"""Normalización de los registros crudos antes de clasificarlos.

Tres de las cuatro fuentes no usan el campo `title` para el texto del anuncio:

- Facebook publica el cuerpo de la publicación en `text`.
- ElYerro es un catálogo de productos y guarda el nombre en `name`.
- Revolico sí usa `title`.

Sin esta normalización, 606 anuncios únicos quedan sin texto, y el informe
acaba atribuyendo al vendedor una omisión que en realidad es del proceso de
extracción. Es exactamente el tipo de error que separa un análisis riguroso de
uno que culpa al dato por lo que el dato no dice.

La normalización también recupera teléfono y provincia desde el cuerpo del
anuncio cuando el origen no los expone como campos estructurados.

No inventa contenido: solo mueve al campo `title` el texto que el anuncio ya
tenía en otro campo.
"""

from __future__ import annotations

import re

# Facebook sustituye el texto por una descripción del contenido cuando la
# publicación es solo imagen. No es información del vendedor y ensucia la
# detección de marca y de cifras.
RUIDO_FACEBOOK = re.compile(r"^\s*may be an image of .*?\s*$", re.IGNORECASE | re.DOTALL)

# Teléfonos cmakeiltanos: 8 dígitos empezando por 5 o 7, o enlaces wa.me.
TELEFONO_TEXTO = re.compile(r"\b(?:5\d{7}|7\d{7})\b")
WHATSAPP_ENLACE = re.compile(r"wa\.me/(\d{6,})")

# Provincias y municipios que aparecen en texto libre o en el campo `location`.
PROVINCIAS = [
    "La Habana", "Habana", "Pinar del Río", "Matanzas", "Villa Clara",
    "Cienfuegos", "Sancti Spíritus", "Ciego de Ávila", "Camagüey",
    "Cárdenas", "Holguín", "Granma", "Santiago de Cuba", "Guantánamo",
    "Artemisa", "Mayabeque", "Isla de la Juventud", "Las Tunas",
]

MUNICIPIOS_HABANA = [
    "Habana Vieja", "Centro Habana", "La Habana Vieja", "Plaza de la Revolución",
    "Plaza", "Habana del Este", "San Miguel del Padrón", "Guanabacoa",
    "Diez de Octubre", "La Lisa", "Marianao", "Boyeros", "Cerro", "Playa",
    "Arroyo Naranjo", "Cotorro", "Regla", "Gócales", "Víbora", "Alamar",
]


def texto_util(item: dict) -> str:
    """Devuelve el texto del anúncio desde el campo que lo contiene."""
    for clave in ("title", "text", "name"):
        valor = item.get(clave)
        if isinstance(valor, str) and valor.strip():
            limpio = RUIDO_FACEBOOK.sub("", valor).strip()
            if limpio:
                return limpio
    return ""


def telefono(item: dict, texto: str) -> str | None:
    """Recupera un teléfono del texto si el origen no expone el campo."""
    if item.get("phone_1"):
        return item["phone_1"]
    enlace = WHATSAPP_ENLACE.search(texto)
    if enlace:
        return enlace.group(1)
    encontrado = TELEFONO_TEXTO.search(texto)
    return encontrado.group(0) if encontrado else None


def provincia(item: dict, texto: str) -> str | None:
    """Recupera la provincia del campo `location` o del propio texto."""
    if item.get("province_name"):
        return item["province_name"]
    campo = item.get("location")
    if isinstance(campo, str):
        for nombre in PROVINCIAS:
            if nombre.lower() in campo.lower():
                return nombre
    for nombre in PROVINCIAS:
        if re.search(rf"\b{re.escape(nombre)}\b", texto, re.IGNORECASE):
            return nombre
    return None


def municipio(item: dict, texto: str) -> str | None:
    """Municipio, solo para La Habana, donde es donde se concentra el estudio."""
    if item.get("municipality_name"):
        return item["municipality_name"]
    if (item.get("province_name") or "") != "La Habana":
        return None
    for nombre in MUNICIPIOS_HABANA:
        if re.search(rf"\b{re.escape(nombre)}\b", texto, re.IGNORECASE):
            return nombre
    return None


def normalizar(item: dict) -> dict:
    """Devuelve una copia del registro con el texto y la ubicación poblados."""
    salida = dict(item)
    texto = texto_util(item)

    salida["title"] = texto
    salida["texto_fuente"] = (
        "title" if item.get("title") else
        "text" if item.get("text") else
        "name" if item.get("name") else "ninguno"
    )

    tel = telefono(item, texto)
    salida["phone_1"] = tel
    salida["phone_1_whatsapp"] = tel
    if tel and not salida.get("contact_info_type"):
        salida["contact_info_type"] = "PHONE"

    prov = provincia(item, texto)
    if prov:
        salida["province_name"] = prov
        salida["province_id"] = salida.get("province_id") or prov
    muni = municipio(item, texto)
    if muni:
        salida["municipality_name"] = muni

    return salida


def normalizar_todos(items: list[dict]) -> list[dict]:
    return [normalizar(i) for i in items]