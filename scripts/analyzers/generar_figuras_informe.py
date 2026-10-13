#!/usr/bin/env python3
"""Genera las figuras del informe final.

Las figuras de generate_report.py responden a la pregunta "que hay en el
mercado". Estas responden a otra distinta: "por que ese mercado no funciona
bien". Son las que sostienen el argumento del informe, asi que se generan
aparte y no se tocan las del analisis general.

Todas se dibujan con el estilo de estilo_informe.py, de modo que el informe se
ve como un documento unico.

Salida:
    analysis/figures_informe/*.png

Uso:
    python3 scripts/analyzers/generar_figuras_informe.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts" / "analyzers"))

import estilo_informe as E  # noqa: E402

CLASIFICADOS = RAIZ / "data" / "processed" / "vehiculos_clasificados.csv"
FIG = RAIZ / "analysis" / "figures_informe"

CATEGORIAS = ["Motores", "Eléctricos", "Bicicletas", "Patinetes Eléctricos"]
CIFRAS = r"\d"


def cargar() -> pd.DataFrame:
    df = pd.read_csv(CLASIFICADOS)
    df["title"] = df["title"].fillna("")
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    return df


def _guardar(fig, nombre: str) -> str:
    return E.guardar(fig, FIG / nombre)


# --------------------------------------------------------------------------


def fig_composicion(df: pd.DataFrame) -> str:
    """Como se reparte el mercado. Contexto antes del problema."""
    conteo = df["categoria"].value_counts()
    orden = [c for c in CATEGORIAS if c in conteo] + (
        ["Otros"] if "Otros" in conteo else []
    )
    valores = [conteo[c] for c in orden]
    colores = [E.COLOR_CATEGORIA[c] for c in orden]

    fig, ax = E.nueva_figura(9.4, 4.4)
    E.barras_horizontales(
        orden, valores, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=[f"{v / len(df) * 100:.1f} %" for v in valores],
        xlabel="Anuncios",
    )
    E.titulo(
        ax,
        "El mercado se concentra en vehículos eléctricos",
        "Anuncios únicos por categoría, sobre un total de "
        f"{len(df):,}".replace(",", ".") + " publicaciones",
    )
    E.pie_de_nota("Fuente: elaboración propia a partir de anuncios públicos de cuatro fuentes.")
    return _guardar(fig, "01_composicion.png")


def fig_cobertura(df: pd.DataFrame) -> str:
    """Que datos existen y cuales no. La cifra clave del argumento."""
    total = len(df)
    con_marca = df["marca_detectada"].notna().sum()
    con_zona = df["province_name"].notna().sum()
    con_precio = df["price_usd"].notna().sum()
    con_cifra = df["title"].str.contains(CIFRAS, regex=True, na=False).sum()

    etiquetas = ["Precio publicado", "Zona declarada", "Marca declarada", "Alguna cifra en el título"]
    valores = [con_precio, con_zona, con_marca, con_cifra]

    fig, ax = E.nueva_figura(9.4, 4.6)
    colores = [E.VERDE, E.ROJO, E.ROJO, E.ROJO]
    E.barras_horizontales(
        etiquetas, valores, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=[f"{v / total * 100:.1f} %" for v in valores],
        xlabel="Anuncios",
    )
    E.titulo(
        ax,
        "El precio se publica; la información que permite comparar, no",
        "Disponibilidad de cada dato en los títulos y fichas de los anuncios",
    )
    E.pie_de_nota(
        "Un anuncio sin marca, zona ni cifra es difícil de comparar con otros. "
        "Eso puede dificultar que llegue a los compradores interesados."
    )
    return _guardar(fig, "02_cobertura.png")


def fig_encontrabilidad(df: pd.DataFrame) -> str:
    """Figura central del informe.

    Un anuncio es encontrable si dice su marca, dice su zona y trae alguna cifra
    con la que se pueda filtrar. Se calcula la proporcion de anuncios que
    cumplen las tres cosas, y la de cada requisito por separado, para separar
    "no publica marca" de "no publica zona", que son problemas distintos.
    """
    reales = df[df["categoria"].isin(CATEGORIAS)].copy()
    reales["marca"] = reales["marca_detectada"].notna()
    reales["zona"] = reales["province_name"].notna()
    reales["cifra"] = reales["title"].str.contains(CIFRAS, regex=True, na=False)
    reales["completo"] = reales["marca"] & reales["zona"] & reales["cifra"]

    filas = []
    for cat in CATEGORIAS:
        sub = reales[reales["categoria"] == cat]
        if len(sub) < 30:
            continue
        filas.append(
            {
                "cat": cat,
                "n": len(sub),
                "marca": sub["marca"].mean() * 100,
                "zona": sub["zona"].mean() * 100,
                "cifra": sub["cifra"].mean() * 100,
                "completo": sub["completo"].mean() * 100,
            }
        )
    filas.append(
        {
            "cat": "Todas las categorías",
            "n": len(reales),
            "marca": reales["marca"].mean() * 100,
            "zona": reales["zona"].mean() * 100,
            "cifra": reales["cifra"].mean() * 100,
            "completo": reales["completo"].mean() * 100,
        }
    )

    fig, ax = E.nueva_figura(9.6, 5.0)
    x = np.arange(len(filas))
    ancho = 0.19
    series = [
        ("marca", "Declara marca", E.TINTA),
        ("zona", "Declara zona", E.TINTA_SUAVE),
        ("cifra", "Trae una cifra", E.AMBAR),
        ("completo", "Cumple las tres", E.ROJO),
    ]
    for i, (clave, etiqueta, color) in enumerate(series):
        vals = [f[clave] for f in filas]
        barras = ax.bar(x + (i - 1.5) * ancho, vals, ancho, label=etiqueta, color=color)
        for barra, v in zip(barras, vals):
            ax.text(
                barra.get_x() + barra.get_width() / 2, v + 1.4,
                f"{v:.0f}", ha="center", va="bottom",
                fontsize=E.BASE_FIG - 3, color=E.TINTA_TEXTO,
                fontweight="bold" if clave == "completo" else "normal",
            )

    ax.set_xticks(x)
    ax.set_xticklabels([f"{f['cat']}\nn={f['n']:,}".replace(",", ".") for f in filas])
    ax.set_ylabel("% de anuncios")
    ax.set_ylim(0, 118)
    ax.yaxis.grid(True, color=E.REGLA, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.20))
    E.titulo(
        ax,
        "Un anuncio solo es encontrable si dice marca, zona y una cifra",
        "Porcentaje de anuncios que cumple cada requisito, por categoría",
    )
    E.pie_de_nota(
        "Las barras rojas resumen los anuncios que declaran los tres datos a la vez; "
        "el resto carece de al menos uno de ellos."
    )
    return _guardar(fig, "03_encontrabilidad.png")


def fig_calidad_titulo(df: pd.DataFrame) -> str:
    """El titulo es el unico vendedor del anuncio."""
    reales = df[df["categoria"].isin(CATEGORIAS)].copy()
    reales["cifra"] = reales["title"].str.contains(CIFRAS, regex=True, na=False)
    reales["vacio"] = reales["title"].str.strip() == ""

    filas = []
    for cat in CATEGORIAS:
        sub = reales[reales["categoria"] == cat]
        filas.append(
            {
                "cat": cat,
                "n": len(sub),
                "cifra": sub["cifra"].mean() * 100,
                "vacio": sub["vacio"].mean() * 100,
            }
        )
    filas.append(
        {
            "cat": "Todas",
            "n": len(reales),
            "cifra": reales["cifra"].mean() * 100,
            "vacio": reales["vacio"].mean() * 100,
        }
    )

    fig, ax = E.nueva_figura(9.4, 4.6)
    x = np.arange(len(filas))
    ancho = 0.32
    con = [f["cifra"] for f in filas]
    vacio = [f["vacio"] for f in filas]
    b1 = ax.bar(x - ancho / 2, con, ancho, label="Incluye al menos una cifra", color=E.TINTA)
    b2 = ax.bar(x + ancho / 2, vacio, ancho, label="Sin título alguno", color=E.ROJO)
    for barras, vals in [(b1, con), (b2, vacio)]:
        for barra, v in zip(barras, vals):
            ax.text(
                barra.get_x() + barra.get_width() / 2, v + 1.4, f"{v:.1f} %",
                ha="center", va="bottom", fontsize=E.BASE_FIG - 3, color=E.TINTA_TEXTO,
            )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{f['cat']}\nn={f['n']:,}".replace(",", ".") for f in filas])
    ax.set_ylabel("% de anuncios")
    ax.set_ylim(0, 118)
    ax.yaxis.grid(True, color=E.REGLA, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    E.titulo(
        ax,
        "La mayoría de los títulos no dice cuánto, ni de qué",
        "Cifras ausentes y títulos completamente vacíos, por categoría",
    )
    E.pie_de_nota(
        "Un título sin cifra (autonomía, cilindrada, voltaje o kilómetros) dificulta "
        "filtrar o comparar el anuncio con otros de la misma categoría."
    )
    return _guardar(fig, "04_calidad_titulo.png")


def fig_precio_marca(df: pd.DataFrame) -> str:
    """Referencia de precio por marca: donde esta parado cada vendedor."""
    con = df.dropna(subset=["price_usd"])
    marcas = [
        (nombre, sub)
        for nombre, sub in con.groupby("marca_detectada")
        if len(sub) >= 20
    ]
    marcas.sort(key=lambda par: par[1]["price_usd"].median(), reverse=True)
    marcas = marcas[:12]
    nombres = [m[0] for m in marcas]
    medianas = [m[1]["price_usd"].median() for m in marcas]
    p10 = [m[1]["price_usd"].quantile(0.10) for m in marcas]
    p90 = [m[1]["price_usd"].quantile(0.90) for m in marcas]
    n = [len(m[1]) for m in marcas]

    fig, ax = E.nueva_figura(9.6, 5.4)
    y = np.arange(len(nombres))
    for i in range(len(nombres)):
        ax.plot(
            [p10[i], p90[i]], [y[i], y[i]], color=E.AMBAR_SUAVE,
            linewidth=7, solid_capstyle="round", zorder=2,
        )
    colores = [E.TINTA if m >= 100 else E.TINTA_SUAVE for m in n]
    ax.scatter(medianas, y, s=95, color=colores, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{nombre}  (n={c})" for nombre, c in zip(nombres, n)])
    ax.invert_yaxis()
    ax.set_xlabel("Precio declarado (USD)")
    ax.xaxis.grid(True, color=E.REGLA, linewidth=0.7)
    ax.set_axisbelow(True)
    for i, v in enumerate(medianas):
        ax.annotate(
            f"{v:,.0f}".replace(",", "."), (v, y[i]),
            xytext=(10, 0), textcoords="offset points",
            va="center", fontsize=E.BASE_FIG - 2.5, color=E.TINTA_TEXTO,
            fontweight="bold",
        )
    ax.set_xlim(0, max(p90) * 1.16)
    E.titulo(
        ax,
        "Las marcas abarcan dos órdenes de magnitud de precio",
        "Mediana y rango percentil 10–90 del precio declarado, por marca con 20 o más anuncios",
    )
    E.pie_de_nota(
        "Los puntos oscuros son marcas con más de 100 anuncios. La dispersión "
        "dentro de cada marca es amplia, lo que sugiere que la marca, por sí sola, "
        "no determina el precio."
    )
    return _guardar(fig, "05_precio_marca.png")


def fig_precio_municipio(df: pd.DataFrame) -> str:
    """La zona pesa mas que la marca. Hallazgo accionable."""
    hab = df[(df["province_name"] == "La Habana") & df["municipality_name"].notna()]
    hab = hab.dropna(subset=["price_usd"])
    datos = [
        (nombre, sub["price_usd"].median(), len(sub))
        for nombre, sub in hab.groupby("municipality_name")
        if len(sub) >= 50
    ]
    datos.sort(key=lambda t: t[1])
    nombres = [d[0] for d in datos]
    medianas = [d[1] for d in datos]
    n = [d[2] for d in datos]

    fig, ax = E.nueva_figura(9.4, 5.0)
    maximo = max(medianas) * 1.20
    colores = [E.AMBAR if v <= min(medianas) + (max(medianas) - min(medianas)) * 0.33
               else (E.TINTA_SUAVE if v >= min(medianas) + (max(medianas) - min(medianas)) * 0.66
                     else E.TINTA) for v in medianas]
    E.barras_horizontales(
        nombres, medianas, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=[f"n={c:,}".replace(",", ".") for c in n],
        xlabel="Mediana del precio declarado (USD)",
    )
    E.titulo(
        ax,
        "En una misma ciudad, el precio cambia según dónde esté el vehículo",
        "Municipios de La Habana con 50 o más anuncios y precio declarado",
    )
    E.pie_de_nota(
        f"La diferencia entre el extremo más barato y el más caro es de "
        f"{max(medianas) / min(medianas):.1f} veces, mayor que la variación entre marcas."
    )
    return _guardar(fig, "06_precio_municipio.png")


def fig_geografia(df: pd.DataFrame) -> str:
    """Concentracion geografica."""
    hab = df[(df["province_name"] == "La Habana") & df["municipality_name"].notna()]
    conteo = hab["municipality_name"].value_counts().head(10)
    total = len(hab)

    fig, ax = E.nueva_figura(9.4, 4.8)
    colores = [E.TINTA if i == 0 else E.TINTA_SUAVE for i in range(len(conteo))]
    E.barras_horizontales(
        conteo.index, conteo.values, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=[f"{v / total * 100:.1f} %" for v in conteo.values],
        xlabel="Anuncios",
    )
    E.titulo(
        ax,
        "Un cuarto del mercado se publica en un solo municipio",
        f"Anuncios con ubicación declarada en La Habana ({total:,}".replace(",", ".")
        + " en total)",
    )
    E.pie_de_nota(
        "La concentración no implica una ausencia de mercado fuera de esa zona, "
        "sino un menor volumen de publicación."
    )
    return _guardar(fig, "07_geografia.png")


def fig_contacto(df: pd.DataFrame) -> str:
    """El canal real."""
    total = len(df)
    whatsapp = df["phone_1_whatsapp"].notna().sum()
    correo = (df["contact_info_type"] == "EMAIL_PHONE").sum()
    sin = total - whatsapp

    fig, ax = E.nueva_figura(9.0, 3.4)
    partes = [whatsapp, correo, sin]
    colores = [E.VERDE, E.TINTA, E.ROJO]
    etiquetas = ["Publica WhatsApp", "Publica correo electrónico", "Sin medio de contacto"]
    wedges, _ = ax.pie(
        partes, colors=colores, startangle=90, counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": E.PANTALLA, "linewidth": 2},
    )
    ax.text(
        0, 0.08, f"{whatsapp / total * 100:.0f} %", ha="center", va="center",
        fontsize=30, color=E.TINTA, fontweight="bold",
    )
    ax.text(0, -0.16, "con WhatsApp", ha="center", va="center", fontsize=11, color=E.GRIS)
    ax.set(aspect="equal")
    leyenda = "\n".join(
        f"{e}  ·  {v:,}".replace(",", ".") + f"  ({v / total * 100:.1f} %)"
        for e, v in zip(etiquetas, partes)
    )
    ax.legend(wedges, [t.replace("  ·  ", "\n") for t in leyenda.split("\n")],
              loc="center left", bbox_to_anchor=(1.0, 0.5), labelspacing=1.4)
    E.titulo(
        ax,
        "El WhatsApp predomina como medio de contacto",
        "Medio de contacto declarado en los anuncios",
    )
    return _guardar(fig, "08_contacto.png")


def fig_fuentes(df: pd.DataFrame) -> str:
    """De donde viene el mercado y su cobertura de informacion."""
    conteo = df["source"].value_counts()
    total = len(df)
    colores = [E.SERIE[i % len(E.SERIE)] for i in range(len(conteo))]

    fig, ax = E.nueva_figura(9.4, 4.2)
    E.barras_horizontales(
        conteo.index, conteo.values, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=[f"{v / total * 100:.1f} %" for v in conteo.values],
        xlabel="Anuncios únicos",
    )
    E.titulo(
        ax,
        "Cuatro fuentes con distintos niveles de detalle",
        "Anuncios únicos por fuente de publicación",
    )
    E.pie_de_nota(
        "Facebook aporta el mayor volumen, aunque parte de sus anuncios requiere "
        "normalización del texto. Las fuentes no son equivalentes: cada una presenta "
        "distintos niveles de detalle."
    )
    return _guardar(fig, "09_fuentes.png")


def fig_huecos(df: pd.DataFrame) -> str:
    """La cara optimista: donde hay hueco hay oportunidad."""
    conteo = df["categoria"].value_counts()
    filas = [
        ("Eléctricos", conteo.get("Eléctricos", 0), "Oferta alta"),
        ("Motores", conteo.get("Motores", 0), "Oferta media"),
        ("Bicicletas", conteo.get("Bicicletas", 0), "Oferta baja"),
        ("Patinetes", conteo.get("Patinetes Eléctricos", 0), "Oferta muy baja"),
    ]

    fig, ax = E.nueva_figura(9.4, 4.2)
    nombres = [f[0] for f in filas]
    valores = [f[1] for f in filas]
    colores = [E.AMBAR, E.TINTA, E.VERDE, E.ROJO]
    E.barras_horizontales(
        nombres, valores, ax, colores,
        formato=lambda v: f"{v:,.0f}".replace(",", "."),
        sufijo=["oferta alta", "oferta media", "oferta baja", "oferta muy baja"],
        xlabel="Anuncios",
    )
    E.titulo(
        ax,
        "Segmentos con menor oferta publicada",
        "Volumen por segmento según los anuncios recopilados",
    )
    E.pie_de_nota(
        "En los segmentos con poca oferta publicada podría haber más espacio para "
        "nuevos anuncios."
    )
    return _guardar(fig, "10_huecos.png")


def fig_precios_categoria(df: pd.DataFrame) -> str:
    """Distribucion, no solo mediana: el mercado es mas ancho de lo que parece."""
    fig, ax = E.nueva_figura(9.6, 4.8)
    datos, colores, nombres = [], [], []
    for cat in CATEGORIAS:
        sub = df[(df["categoria"] == cat) & df["price_usd"].notna()]["price_usd"]
        if len(sub) < 30:
            continue
        datos.append(sub.to_numpy())
        colores.append(E.COLOR_CATEGORIA[cat])
        nombres.append(f"{cat}\nn={len(sub):,}".replace(",", "."))

    caja = ax.boxplot(
        datos, orientation="vertical", patch_artist=True, widths=0.5,
        showfliers=False, medianprops={"color": E.PANTALLA, "linewidth": 2.2},
        whiskerprops={"color": E.GRIS, "linewidth": 1.1},
        capprops={"color": E.GRIS, "linewidth": 1.1},
    )
    for parche, color in zip(caja["boxes"], colores):
        parche.set_facecolor(color)
        parche.set_edgecolor(color)
        parche.set_linewidth(0)
    ax.set_xticks(range(1, len(nombres) + 1))
    ax.set_xticklabels(nombres)
    ax.set_ylabel("Precio declarado (USD)")
    ax.yaxis.grid(True, color=E.REGLA, linewidth=0.7)
    ax.set_axisbelow(True)
    E.titulo(
        ax,
        "Dentro de cada categoría el precio se mueve en un rango amplio",
        "Distribución del precio declarado por categoría, sin valores atípicos",
    )
    E.pie_de_nota(
        "La mediana resume el centro, pero el intervalo entre cuartiles es ancho: "
        "fijar precio por la mediana de la categoría es solo un punto de partida."
    )
    return _guardar(fig, "11_precios_categoria.png")


def fig_descartados(df: pd.DataFrame) -> str:
    """La calidad del dato es parte del argumento, no una nota al pie."""
    total = len(df)
    sin_titulo = (df["title"].str.strip() == "").sum()
    sin_senal = df["categoria"].eq("Otros").sum()
    util = total - sin_senal

    fig, ax = E.nueva_figura(9.0, 3.2)
    ax.barh(
        ["Utilizables\n(vehículo identificado)", "Sin señal de tipo\n(clasificados como «Otros»)"],
        [util, sin_senal], color=[E.TINTA, E.ROJO], height=0.5,
    )
    for i, v in enumerate([util, sin_senal]):
        ax.text(
            v + total * 0.012, i, f"{v:,}".replace(",", "."),
            va="center", fontsize=E.BASE_FIG - 1, color=E.TINTA_TEXTO, fontweight="bold",
        )
    ax.set_xlim(0, total * 1.22)
    ax.set_xlabel("Anuncios")
    ax.invert_yaxis()
    E.titulo(
        ax,
        f"{sin_senal:,}".replace(",", ".") + " anuncios no permiten identificar el vehículo",
        "Volumen descartado por falta de información, no por error del estudio",
    )
    E.pie_de_nota(
        f"De ellos, {sin_titulo:,}".replace(",", ".")
        + " anuncios no tienen título alguno. Clasificarlos por fuerza habría sido inventar información."
    )
    return _guardar(fig, "12_calidad_dato.png")


FIGURAS = [
    fig_composicion, fig_cobertura, fig_encontrabilidad, fig_calidad_titulo,
    fig_precio_marca, fig_precio_municipio, fig_geografia, fig_contacto,
    fig_fuentes, fig_huecos, fig_precios_categoria, fig_descartados,
]


def main() -> None:
    E.aplicar()
    df = cargar()
    for funcion in FIGURAS:
        nombre = funcion(df)
        print(f"  [ok] figures_informe/{nombre}")


if __name__ == "__main__":
    main()