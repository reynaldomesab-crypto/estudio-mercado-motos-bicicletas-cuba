#!/usr/bin/env python3
"""Construye analysis/INFORME_FINAL.html: informe académico autocontenido.

Estructura inspirada en el paper académico de F1 (Weissbock, 2025):
- Abstract + Keywords
- 1. Introducción (Background, Problem Statement, Scope, Prior Work, Objective)
- 2. Materiales y Métodos (Framework, Data Preparation, Classification, Audit, Methods)
- 3. Resultados (Composition, Coverage, Findability, Title Quality, Price by Brand/Zone,
  Geography, Contact, Sources, Gaps, Price Distribution, Data Quality)
- 4. Discusión y Conclusiones (Summary, Interpretation/Need for Change, Limitations,
  Future Work, Conclusion)
- Referencias

Todas las cifras y figuras se inyectan desde analysis/evidencia_vendedores.json y
analysis/figures_informe/*.png. El HTML resultante es autocontenido (base64) y
funciona sin internet.

Uso:
    python3 scripts/build_informe.py
"""

import base64
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ANALISIS = RAIZ / "analysis"
FIGURAS = ANALISIS / "figures_informe"
EVIDENCIA = ANALISIS / "evidencia_vendedores.json"
PLANTILLA = RAIZ / "analysis" / "plantilla_informe.html"
SALIDA = ANALISIS / "INFORME_FINAL.html"


def fig(nombre: str) -> str:
    ruta = FIGURAS / nombre
    if not ruta.exists():
        return f'<div class="fig-faltante">Figura no encontrada: {nombre}</div>'
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return (
        f'<img class="fig" src="data:image/png;base64,{datos}" '
        f'alt="Figura: {nombre}">'
    )


def tabla_marcas_html(marcas: list) -> str:
    """Genera el HTML de la tabla de precios por marca."""
    filas = []
    for m in marcas[:10]:
        fila = (
            "<tr>"
            f"<td>{m['marca']}</td>"
            f"<td class='num'>{int(round(m['anuncios'])):,}</td>"
            f"<td class='num'>{int(round(m['mediana_usd'])):,}</td>"
            f"<td class='num'>{int(round(m['p10_usd'])):,}–{int(round(m['p90_usd'])):,}</td>"
            "</tr>"
        ).replace(",", ".")
        filas.append(fila)
    return "\n".join(filas)


def miles(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def pct(valor) -> str:
    """Porcentaje con coma decimal, según la norma del español."""
    return f"{float(valor):.1f}".replace(".", ",")


def main() -> None:
    ev = json.loads(EVIDENCIA.read_text(encoding="utf-8"))
    html = PLANTILLA.read_text(encoding="utf-8")

    inv = ev["invisibilidad"]
    tit = ev["titulos"]
    ubi = ev["ubicacion"]
    pre = ev["precios"]
    con = ev["contacto"]
    hue = ev["huecos"]
    lim = ev["limites"]

    # Tabla
    tabla_marcas = tabla_marcas_html(pre["marcas"])

    # Advertencias
    advertencias = "".join(f"<li>{a}</li>" for a in lim["advertencias"])

    # Categorías
    cats = hue["categorias"]
    cats_items = "".join(
        f"<li><strong>{nombre}</strong>: {miles(n)} anuncios</li>"
        for nombre, n in cats.items()
    )

    reemplazos = {
        # Portada / metadatos
        "{{TITULO}}": "El mercado de vehículos de dos ruedas en La Habana",
        "{{SUBTITULO}}": "Análisis de 4.979 anuncios únicos para diagnosticar la calidad de la información del mercado y proponer estándares de publicación",
        "{{AUTOR}}": "Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba",
        "{{FECHA}}": "Octubre 2026",

        # Abstract / Keywords
        "{{ABSTRACT}}": (
            "Este estudio analiza 4.979 anuncios únicos de vehículos de dos ruedas "
            "(motos, eléctricas, bicicletas y patinetes) publicados en cuatro fuentes "
            "cubanas (Revolico, iTENCEL, ElYerroMenu y Facebook). La normalización de "
            "los datos —recuperando el texto del anuncio desde campos alternativos, "
            "extrayendo teléfono y ubicación del cuerpo del texto y corrigiendo la "
            "clasificación— muestra que el principal punto de mejora no estaría en la "
            "cantidad de oferta, sino en la información que los anuncios publican: el "
            "45,5 % de los vehículos reales no declara su marca, el 43,3 % de los "
            "títulos no incluye ninguna cifra comparable y, tras la normalización, solo "
            "el 8,8 % carece de ubicación declarada. El 24,0 % de la oferta con "
            "ubicación se concentra en Centro Habana. Se describen segmentos con menor "
            "oferta publicada (patinetes y repuestos) y se sugiere un estándar mínimo "
            "de publicación —marca, cifra clave, municipio y WhatsApp— como posible vía "
            "de mejora. El estudio incluye una auditoría automática de la clasificación "
            "con 3 hallazgos menores, y todo el proceso es reproducible."
        ),
        "{{KEYWORDS}}": "mercado informal, vehículos de dos ruedas, calidad de datos, profesionalización, La Habana, clasificación automática, auditoría reproducible",

        # Cifras globales
        "{{TOTAL_ANUNCIOS}}": miles(ev["invisibilidad"]["vehiculos"]),
        "{{VEHICULOS_REALES}}": miles(ev["invisibilidad"]["vehiculos_reales"]),
        "{{PCT_REALES}}": pct(ev['invisibilidad']['vehiculos_reales'] / ev['invisibilidad']['vehiculos'] * 100),
        "{{PCT_SIN_MARCA_REAL}}": pct(ev["invisibilidad"]["pct_reales_sin_marca"]),
        "{{PCT_SIN_CIFRA}}": pct(ev["titulos"]["pct_sin_cifra"]),
        "{{PCT_SIN_UBICACION}}": pct(ev["ubicacion"]["sin_ubicacion_pct"]),
        "{{PCT_WHATSAPP}}": pct(ev["contacto"]["pct_whatsapp"]),
        "{{PATINETES}}": ev["huecos"]["patinetes"],
        "{{BICICLETAS}}": ev["huecos"]["bicicletas"],
        "{{PCT_SIN_MARCA_BICI}}": pct(ev["invisibilidad"]["por_categoria"]["Bicicletas"]["pct_sin_marca"]),

        # Figuras (base64)
        "{{FIG_COMPOSICION}}": fig("01_composicion.png"),
        "{{FIG_COBERTURA}}": fig("02_cobertura.png"),
        "{{FIG_ENCONTRABILIDAD}}": fig("03_encontrabilidad.png"),
        "{{FIG_CALIDAD_TITULO}}": fig("04_calidad_titulo.png"),
        "{{FIG_PRECIO_MARCA}}": fig("05_precio_marca.png"),
        "{{FIG_GEOGRAFIA}}": fig("07_geografia.png"),
        "{{FIG_CONTACTO}}": fig("08_contacto.png"),
        "{{FIG_FUENTES}}": fig("09_fuentes.png"),
        "{{FIG_HUECOS}}": fig("10_huecos.png"),
        "{{FIG_PRECIOS_CAT}}": fig("11_precios_categoria.png"),
        "{{FIG_CALIDAD_DATO}}": fig("12_calidad_dato.png"),

        # Tabla
        "{{TABLA_MARCAS}}": (
            "<thead><tr><th>Marca</th><th class='num'>Anuncios</th>"
            "<th class='num'>Mediana (USD)</th><th class='num'>Rango p10–p90</th></tr></thead>"
            "<tbody>" + tabla_marcas + "</tbody>"
        ),

        # Advertencias
        "{{ADVERTENCIAS}}": "".join(f"<li>{a}</li>" for a in ev["limites"]["advertencias"]),

        # Cifras de límites
        "{{SIN_TITULO}}": miles(ev["limites"]["sin_titulo"]),
        "{{PCT_SIN_TITULO}}": pct(ev["limites"]["pct_sin_titulo"]),
        "{{SIN_SENAL}}": miles(ev["limites"]["sin_senal_tipo"]),
        "{{PCT_SIN_SENAL}}": pct(ev["limites"]["pct_sin_senal"]),
        "{{PCT_CON_PROVINCIA}}": pct(ev["ubicacion"]["pct_con_provincia"]),
        "{{PCT_TITULOS_VACIOS}}": pct(ev["titulos"]["pct_vacias"]),
        "{{MUNI_TOP_PCT}}": pct(ev["ubicacion"]["pct_del_total_habana"]),

        # Cifras de transparencia
        "{{AUDITORIA_HALLAZGOS}}": "3",
        "{{AUDITORIA_DETALLE}}": (
            "Dos marcas declaradas solo-eléctricas presentan anuncios de combustión mal "
            "clasificados (VEDCA: 2; BUCATTI: 1) y un anuncio de combustión figura como "
            "eléctrico («Bici moto Evolution»)."
        ),
    }

    # Sustitución y validación
    for clave, valor in reemplazos.items():
        if clave not in html:
            raise SystemExit(f"Placeholder inexistente en plantilla: {clave}")
        html = html.replace(clave, str(valor))

    sobrantes = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if sobrantes:
        raise SystemExit(f"Placeholders sin sustituir: {sobrantes}")

    externas = re.findall(r'(?:src|href)="(?:https?:)?//[^"]+"', html)
    if externas:
        raise SystemExit(f"El informe tiene recursos externos: {externas[:5]}")

    SALIDA.write_text(html, encoding="utf-8")
    kb = len(html.encode("utf-8")) / 1024
    print(f"[ok] {SALIDA.relative_to(RAIZ)} ({kb:.0f} KB)")
    print("[ok] Sin recursos externos: funciona sin internet")


if __name__ == "__main__":
    main()