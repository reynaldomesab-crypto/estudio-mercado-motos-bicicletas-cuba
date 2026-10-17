#!/usr/bin/env python3
"""Anonimiza el conjunto de datos para poder versionarlo sin exponer a personas.

El estudio describe el contenido de anuncios públicos, pero esos anuncios
identifican a personas concretas: nombres de perfil, identificadores de Facebook
y números de teléfono. Publicar el conjunto en un repositorio abierto convierte
una observación sobre el mercado en un dato personal localizable.

Este script genera una copia anonimizada aplicando una lista blanca: se conservan
únicamente los campos que el análisis necesita y se descarta todo lo demás, de
modo que un campo nuevo que se añada al scraper no se filtre por olvido.

Campos que se conservan (contenido y agregados):
    categoría, marca, precio, provincia, municipio, título y texto,
    procedencia y marca de tiempo de la captura

Campos que se descartan o seudonimizan (identifican a una persona):
    nombres de perfil e identificadores de Facebook, identificadores de
    anuncio, teléfonos, enlaces al anuncio y a las personas, imágenes,
   ningún dato de contacto dato de contacto incrustado en el texto

Uso:
    python3 scripts/privacy/sanitizar_datos.py [--sal <cadena>]

Salida:
    data/publico/vehiculos_clasificados.csv
    data/publico/curated/*.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CURATED = RAIZ / "data" / "curated"
PROCESADO = RAIZ / "data" / "processed" / "vehiculos_clasificados.csv"
DESTINO = RAIZ / "data" / "publico"

SALT = "estudio-mercado-motos-bicicletas-cuba-v1"

# Lista blanca: todo lo que no aparece aquí se descarta del conjunto público.
CAMPOS_PERMITIDOS = {
    # procedencia
    "source", "source_id", "scraped_at", "processed_at", "group_title",
    # contenido
    "title", "text", "name", "is_shared_post", "images_count",
    # clasificación
    "category", "category_class", "category_detected", "vehicle_category",
    "vehicle_type", "part_category", "brand",
    # precio
    "price", "price_usd", "price_original", "currency", "currency_original",
    # geografía (agregados)
    "province", "province_name", "municipality", "municipality_name",
}

# Campos de texto donde puede haber datos de contacto incrustados.
CAMPOS_TEXTO = ("title", "text", "name")

# Teléfonos, enlaces de contacto, correos y rutas. Se sustituyen por una marca.
# Se conservan los números que describen el producto (cilindrada, autonomía,
# voltaje, kilometraje) porque son parte del contenido analizado: por eso se
# exige un mínimo de ocho dígitos, que en este corpus corresponde a un móvil y
# no a una especificación.
PATRON_CONTACTO = re.compile(
    r"""(?:
        wa\.me\s*/?\s*\+?\s*\d(?:[\d\s.-]?\d){4,14}   # enlaces wa.me, con o sin barra
      | (?:https?://)?wa\.me/\S+
      | \+?53[\s.-]*\d(?:[\d\s.-]?\d){7,14}
      | (?<!\d)\d(?:[\s-]?\d){7,14}(?!\d)              # bloque de 8 o más dígitos
      | \b[\w.+-]+@[\w-]+\.[\w.-]+\b                  # correo electrónico
      | \b(?:https?://|www\.)\S+                        # enlaces
      | @[\w.-]{3,}                                    # menciones
    )""",
    re.VERBOSE | re.IGNORECASE,
)


def seudonimo(valor: str) -> str:
    """Identificador estable e irreversible para un valor identificable."""
    if not valor:
        return ""
    resumen = hashlib.sha256(f"{SALT}|{valor}".encode("utf-8")).hexdigest()
    return f"id_{resumen[:12]}"


def limpiar_texto(texto: str) -> str:
    """Sustituye teléfonos, correos, enlaces y menciones por una marca neutra."""
    if not texto:
        return ""
    limpio = PATRON_CONTACTO.sub("[contacto]", texto)
    return re.sub(r"\s{2,}", " ", limpio).strip()


def anonimizar_curated() -> list[str]:
    """Anonimiza los JSON de data/curated conservando solo la lista blanca."""
    generados = []
    destino_curated = DESTINO / "curated"
    destino_curated.mkdir(parents=True, exist_ok=True)

    for origen in sorted(CURATED.glob("*.json")):
        datos = json.loads(origen.read_text(encoding="utf-8"))
        items = datos.get("items", []) if isinstance(datos, dict) else datos

        limpios = []
        for item in items:
            limpio = {k: v for k, v in item.items() if k in CAMPOS_PERMITIDOS}
            for campo in CAMPOS_TEXTO:
                if isinstance(limpio.get(campo), str):
                    limpio[campo] = limpiar_texto(limpio[campo])
            limpios.append(limpio)

        if isinstance(datos, dict):
            datos["items"] = limpios
            datos["nota_privacidad"] = (
                "Copia anonimizada: sin nombres de perfil, identificadores, "
                "teléfonos ni enlaces. Generada por scripts/privacy/sanitizar_datos.py."
            )
            salida = datos
        else:
            salida = limpios

        destino = destino_curated / origen.name
        destino.write_text(
            json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        generados.append(str(destino.relative_to(RAIZ)))
    return generados


def anonimizar_csv() -> tuple[str, int]:
    """Anonimiza el CSV clasificado conservando las columnas del análisis."""
    DESTINO.mkdir(parents=True, exist_ok=True)
    destino = DESTINO / "vehiculos_clasificados.csv"

    columnas_publicas = [
        "title", "source", "categoria_fuente", "marca_detectada", "categoria",
        "price_usd", "currency", "province_name", "municipality_name",
        "anuncio_id", "telefono_id", "tiene_whatsapp",
    ]

    total = 0
    with PROCESADO.open(encoding="utf-8") as f, destino.open(
        "w", encoding="utf-8", newline=""
    ) as salida:
        lector = csv.DictReader(f)
        escritor = csv.DictWriter(salida, fieldnames=columnas_publicas)
        escritor.writeheader()
        for fila in lector:
            total += 1
            escritor.writerow(
                {
                    "title": limpiar_texto(fila.get("title") or ""),
                    "source": fila.get("source", ""),
                    "categoria_fuente": fila.get("categoria_fuente", ""),
                    "marca_detectada": fila.get("marca_detectada", ""),
                    "categoria": fila.get("categoria", ""),
                    "price_usd": fila.get("price_usd", ""),
                    "currency": fila.get("currency", ""),
                    "province_name": fila.get("province_name", ""),
                    "municipality_name": fila.get("municipality_name", ""),
                    "anuncio_id": seudonimo(fila.get("source_url", "")),
                    "telefono_id": seudonimo(fila.get("phone_1_whatsapp", "")),
                    "tiene_whatsapp": "1" if fila.get("phone_1_whatsapp") else "0",
                }
            )

    return str(destino.relative_to(RAIZ)), total


def main() -> None:
    global SALT

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sal", default=SALT, help="sal para el hash seudónimo")
    args = ap.parse_args()
    SALT = args.sal

    print("[anonimizando] curated...")
    for ruta in anonimizar_curated():
        print(f"  [ok] {ruta}")

    print("[anonimizando] csv clasificado...")
    ruta, total = anonimizar_csv()
    print(f"  [ok] {ruta} ({total} anuncios)")

    print()
    print("El contenido identificable queda solo en data/, fuera del repositorio.")


if __name__ == "__main__":
    main()
