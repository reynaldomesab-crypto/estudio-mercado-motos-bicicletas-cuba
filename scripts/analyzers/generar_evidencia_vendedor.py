#!/usr/bin/env python3
"""Calcula las cifras que sostienen la guia y la presentacion para vendedores.

Toda la divulgacion del proyecto debe poder rastrearse hasta el dato. Este
script no estima ni rellena: solo cuenta sobre el CSV de clasificacion, que ya
fue producido y auditado por generate_report.py y auditar_clasificaciones.py.
Si una cifra no se puede calcular, no aparece en la salida, y la presentacion
la declara como limite en vez de rellenarla.

Salida:
    analysis/evidencia_vendedores.json

Uso:
    python3 scripts/analyzers/generar_evidencia_vendedor.py
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CLASIFICADOS = RAIZ / "data" / "processed" / "vehiculos_clasificados.csv"
PARTES = RAIZ / "data" / "curated" / "parts_curated.json"
SALIDA = RAIZ / "analysis" / "evidencia_vendedores.json"

ORDEN_CATEGORIAS = [
    "Motores",
    "Eléctricos",
    "Bicicletas",
    "Patinetes Eléctricos",
    "Otros",
]

# Un titulo sirve para comparar si trae al menos una cifra (cc, voltaje, km...).
CIFRAS = r"\d"


def cargar() -> pd.DataFrame:
    df = pd.read_csv(CLASIFICADOS)
    df["title"] = df["title"].fillna("")
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    return df


def seccion_invisibilidad(df):
    """Cuantos anuncios no se pueden encontrar al buscar por marca."""
    total = len(df)
    sin_marca = int(df["marca_detectada"].isna().sum())

    # El denominador que importa para un vendedor son los vehiculos reales.
    # "Otros" mezcla titulos vacios y anuncios sin senal de tipo, que no son
    # vehiculos: incluirlos inflaria artificialmente el porcentaje de listings
    # sin marca.
    reales = df[df["categoria"].isin(ORDEN_CATEGORIAS[:-1])]
    reales_sin_marca = int(reales["marca_detectada"].isna().sum())

    por_categoria = {}
    for cat in ORDEN_CATEGORIAS:
        sub = df[df["categoria"] == cat]
        if sub.empty:
            continue
        faltan = int(sub["marca_detectada"].isna().sum())
        por_categoria[cat] = {
            "anuncios": int(len(sub)),
            "sin_marca": faltan,
            "pct_sin_marca": round(faltan / len(sub) * 100, 1),
        }
    return {
        "vehiculos": total,
        "sin_marca": sin_marca,
        "pct_sin_marca": round(sin_marca / total * 100, 1),
        "vehiculos_reales": int(len(reales)),
        "reales_sin_marca": reales_sin_marca,
        "pct_reales_sin_marca": round(reales_sin_marca / len(reales) * 100, 1),
        "por_categoria": por_categoria,
    }


def seccion_titulos(df):
    """Calidad del titulo: es lo unico que ve el comprador antes de contactar."""
    titulos = df["title"]
    total = len(df)
    vacios = int((titulos.str.strip() == "").sum())
    sin_cifra = int((~titulos.str.contains(CIFRAS, regex=True, na=False)).sum())
    return {
        "total": total,
        "vacias": vacios,
        "pct_vacias": round(vacios / total * 100, 1),
        "sin_cifra": sin_cifra,
        "pct_sin_cifra": round(sin_cifra / total * 100, 1),
    }


def seccion_ubicacion(df):
    """Solo la mitad de los anuncios dice donde esta el vehiculo."""
    total = len(df)
    con_provincia = int(df["province_name"].notna().sum())
    con_municipio = int(df["municipality_name"].notna().sum())

    precios = df[(df["province_name"] == "La Habana") & df["municipality_name"].notna()]
    precios = precios.dropna(subset=["price_usd"])

    por_municipio = [
        {
            "municipio": nombre,
            "anuncios": int(len(sub)),
            "mediana_usd": float(round(sub["price_usd"].median())),
        }
        for nombre, sub in precios.groupby("municipality_name")
    ]
    por_municipio.sort(key=lambda x: x["anuncios"], reverse=True)

    top = por_municipio[0] if por_municipio else {"anuncios": 0}
    referencia = len(precios)
    return {
        "total": total,
        "con_provincia": con_provincia,
        "pct_con_provincia": round(con_provincia / total * 100, 1),
        "sin_ubicacion_pct": round((total - con_provincia) / total * 100, 1),
        "anuncios_habana_con_municipio_y_precio": int(referencia),
        "municipio_mas_anuncios": top["municipio"],
        "pct_del_total_habana": round(top["anuncios"] / referencia * 100, 1) if referencia else 0.0,
        "por_municipio": por_municipio,
    }


def seccion_precios(df):
    """Mediana por marca: donde esta parado cada vendedor hoy."""
    con_precio = df.dropna(subset=["price_usd"])
    marcas = [
        {
            "marca": nombre,
            "anuncios": int(len(sub)),
            "mediana_usd": float(round(sub["price_usd"].median())),
            "p10_usd": float(round(sub["price_usd"].quantile(0.10))),
            "p90_usd": float(round(sub["price_usd"].quantile(0.90))),
        }
        for nombre, sub in con_precio.groupby("marca_detectada")
        if len(sub) >= 20
    ]
    marcas.sort(key=lambda x: x["anuncios"], reverse=True)
    return {
        "anuncios_con_precio": int(len(con_precio)),
        "pct_con_precio": round(len(con_precio) / len(df) * 100, 1),
        "anuncios_con_precio_sin_marca": int(con_precio["marca_detectada"].isna().sum()),
        "marcas": marcas,
    }


def seccion_contacto(df):
    """Por donde realmente se compra en este mercado."""
    total = len(df)
    whatsapp = int(df["phone_1_whatsapp"].notna().sum())
    correo = int((df["contact_info_type"] == "EMAIL_PHONE").sum())
    return {
        "total": total,
        "whatsapp": whatsapp,
        "pct_whatsapp": round(whatsapp / total * 100, 1),
        "correo": correo,
        "sin_tipo_contacto": int(df["contact_info_type"].isna().sum()),
    }


def seccion_huecos(df):
    """Categorias con escasa oferta: la oportunidad del vendedor."""
    conteo = df["categoria"].value_counts().to_dict()
    piezas = json.loads(PARTES.read_text(encoding="utf-8"))["items"] if PARTES.exists() else []
    return {
        "categorias": {str(k): int(v) for k, v in conteo.items()},
        "patinetes": int(conteo.get("Patinetes Eléctricos", 0)),
        "bicicletas": int(conteo.get("Bicicletas", 0)),
        "piezas_archivo": len(piezas),
    }


def seccion_limites(df):
    """Lo que el estudio NO puede afirmar. Se declara, no se disimula."""
    total = len(df)
    sin_titulo = int((df["title"].str.strip() == "").sum())
    sin_senal = int(df["categoria"].eq("Otros").sum())
    return {
        "sin_titulo": sin_titulo,
        "pct_sin_titulo": round(sin_titulo / total * 100, 1),
        "sin_senal_tipo": sin_senal,
        "pct_sin_senal": round(sin_senal / total * 100, 1),
        "advertencias": [
            "Publicar más no equivale a vender más: el estudio no observa ventas, solo anuncios.",
            "Los precios son los que declara el vendedor; no constituyen un avalúo.",
            "No existe un campo de condición (nuevo o usado): no es posible distinguirla.",
            "No hay fecha por anuncio: no se puede afirmar una tendencia ni estacionalidad.",
            "La deduplicación se realiza por URL: un vehículo publicado en dos sitios cuenta como dos.",
        ],
    }


def seccion_sesgos(df):
    """Separa lo que refleja la plataforma de lo que refleja la conducta.

    Cada fuente usa un formulario distinto. Cuando una plataforma exige un dato
    (provincia, marca), el cien por cien de sus anuncios lo tiene, y eso no dice
    nada sobre quien publica: dice algo sobre el formulario. A la inversa, si la
    plataforma no expone el campo, el cero por cien tampoco es una omision.

    Esta seccion es la base para no atribuir a las personas lo que en realidad
    es un efecto del formulario de la plataforma.
    """
    reales = df[df["categoria"].isin(ORDEN_CATEGORIAS[:-1])]

    campos = {
        "marca": "marca_detectada",
        "provincia": "province_name",
        "telefono": "phone_1_whatsapp",
    }

    por_fuente = {}
    for fuente, sub in reales.groupby("source"):
        fila = {"anuncios": int(len(sub))}
        for nombre, columna in campos.items():
            con = int(sub[columna].notna().sum())
            fila[f"{nombre}_n"] = con
            fila[f"{nombre}_pct"] = round(con / len(sub) * 100, 1)
        sin_cifra = int((~sub["title"].str.contains(CIFRAS, regex=True, na=False)).sum())
        fila["sin_cifra_pct"] = round(sin_cifra / len(sub) * 100, 1)
        por_fuente[fuente] = fila

    return {
        "por_fuente": por_fuente,
        "nota": (
            "Una ausencia solo es interpretable cuando la plataforma pide el dato. "
            "Provincia y marca son obligatorias en unas fuentes y no existen en "
            "otras, de modo que la comparacion entre fuentes no es homogenea."
        ),
    }


def main():
    df = cargar()
    evidencia = {
      "generado_por": "scripts/analyzers/generar_evidencia_vendedor.py",
      "nota": "Cifras de divulgacion. Deben coincidir con analysis/resultados.json.",
        "invisibilidad": seccion_invisibilidad(df),
   "titulos": seccion_titulos(df),
        "ubicacion": seccion_ubicacion(df),
      "precios": seccion_precios(df),
    "contacto": seccion_contacto(df),
        "huecos": seccion_huecos(df),
        "limites": seccion_limites(df),
        "sesgos": seccion_sesgos(df),
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")

    inv, tit, ubi, con, hue = (
        evidencia["invisibilidad"], evidencia["titulos"],
        evidencia["ubicacion"], evidencia["contacto"], evidencia["huecos"],
    )
    print(f"Vehiculos: {inv['vehiculos']} | sin marca {inv['sin_marca']} ({inv['pct_sin_marca']}%)")
    print(f"Titulos sin cifra: {tit['pct_sin_cifra']}% | vacios: {tit['pct_vacias']}%")
    print(f"Con provincia: {ubi['pct_con_provincia']}% | sin ubicacion: {ubi['sin_ubicacion_pct']}%")
    print(f"Whatsapp: {con['pct_whatsapp']}% | correo: {con['correo']}")
    print(f"Patinetes: {hue['patinetes']} | piezas en archivo: {hue['piezas_archivo']}")
    print(f"Escrito: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()