#!/usr/bin/env python3
"""Construye presentation/index.html: deck autocontenido y sin internet.

Las figuras se incrustan en base64 en lugar de referenciarse con una ruta. Un
HTML que apunta a ../analysis/figures/*.png se ve roto si el archivo se mueve a
otra computadora, y esta presentacion puede presentarse desde la USB o desde el
portatil de otra persona. Con base64 no hay rutas que dependan del disco.

Las cifras se leen de analysis/evidencia_vendedores.json. Si una cifra cambia,
se corre generate_report.py, luego generar_evidencia_vendedor.py, luego este
script: el deck nunca se edita a mano.

Uso:
    python3 scripts/build_presentation.py
"""

import base64
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ANALISIS = RAIZ / "analysis"
FIGURAS = ANALISIS / "figures"
EVIDENCIA = ANALISIS / "evidencia_vendedores.json"
PLANTILLA = RAIZ / "presentation" / "plantilla.html"
SALIDA = RAIZ / "presentation" / "index.html"


def fig(nombre: str) -> str:
    """Devuelve un tag <img> con la figura incrustada en base64."""
    ruta = FIGURAS / nombre
    if not ruta.exists():
        return (
            '<div class="fig-faltante">Figura no encontrada: '
            f"{nombre}</div>"
        )
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return (
        f'<img class="fig" src="data:image/png;base64,{datos}" '
        f'alt="{nombre}">'
    )


def miles(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def dinero(n) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


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

    # Marcas ordenadas por volumen: la primera y la de mediana mas baja among
    # las de volumen relevante son el contraste de precio que se explica.
    marcas = pre["marcas"]
    marcas_texto = "".join(
        f"<tr><td>{m['marca']}</td><td class='num'>{miles(m['anuncios'])}</td>"
        f"<td class='num'>{dinero(m['mediana_usd'])} USD</td>"
        f"<td class='num'>{dinero(m['p10_usd'])}–{dinero(m['p90_usd'])}</td></tr>"
        for m in marcas[:8]
    )

    municipios = "".join(
        f"<tr><td>{m['municipio']}</td><td class='num'>{miles(m['anuncios'])}</td>"
        f"<td class='num'>{dinero(m['mediana_usd'])} USD</td></tr>"
        for m in ubi["por_municipio"][:8]
    )

    advertencias = "".join(f"<li>{a}</li>" for a in lim["advertencias"])


    reemplazos = {
        "{{TOTAL_VEHICULOS}}": miles(inv["vehiculos"]),
        "{{VEHICULOS_REALES}}": miles(inv["vehiculos_reales"]),
        "{{SIN_MARCA}}": miles(inv["reales_sin_marca"]),
        "{{PCT_SIN_MARCA}}": inv["pct_reales_sin_marca"],
        "{{PCT_SIN_MARCA_BICI}}": inv["por_categoria"]["Bicicletas"]["pct_sin_marca"],
        "{{SIN_MARCA_BICI}}": miles(inv["por_categoria"]["Bicicletas"]["sin_marca"]),
        "{{BICI_TOTAL}}": miles(inv["por_categoria"]["Bicicletas"]["anuncios"]),
        "{{PCT_SIN_CIFRA}}": tit["pct_sin_cifra"],
        "{{SIN_CIFRA}}": miles(tit["sin_cifra"]),
        "{{TITULOS_VACIOS}}": miles(tit["vacias"]),
        "{{PCT_TITULOS_VACIOS}}": tit["pct_vacias"],
        "{{SIN_UBICACION}}": ubi["sin_ubicacion_pct"],
        "{{CON_UBICACION}}": ubi["pct_con_provincia"],
        "{{PCT_WHATSAPP}}": con["pct_whatsapp"],
        "{{WHATSAPP}}": miles(con["whatsapp"]),
        "{{CORREOS}}": con["correo"],
        "{{PCT_CON_PRECIO}}": pre["pct_con_precio"],
        "{{PATINETES}}": hue["patinetes"],
        "{{BICICLETAS}}": hue["bicicletas"],
        "{{PIEZAS}}": miles(hue["piezas_archivo"]),
        "{{MUNI_TOP}}": ubi["municipio_mas_anuncios"],
        "{{MUNI_TOP_PCT}}": ubi["pct_del_total_habana"],
        "{{TOTAL_HABANA}}": miles(ubi["anuncios_habana_con_municipio_y_precio"]),
        "{{SIN_TITULO}}": miles(lim["sin_titulo"]),
        "{{PCT_SIN_TITULO}}": lim["pct_sin_titulo"],
        "{{SIN_SENAL}}": miles(lim["sin_senal_tipo"]),
        "{{PCT_SIN_SENAL}}": lim["pct_sin_senal"],
        "{{TABLA_MARCAS}}": marcas_texto,
        "{{TABLA_MUNICIPIOS}}": municipios,
        "{{ADVERTENCIAS}}": advertencias,
        "{{FIG_COBERTURA}}": fig("02_cobertura_informacion.png"),
        "{{FIG_MARCAS_MOTORES}}": fig("03_marcas_motores.png"),
        "{{FIG_MUNICIPIOS}}": fig("10_municipios_habana.png"),
        "{{FIG_FUENTES}}": fig("12_publicaciones_por_fuente.png"),
    }

    faltan = []
    for clave, valor in reemplazos.items():
        if clave not in html:
            faltan.append(clave)
            continue
        html = html.replace(clave, str(valor))

    # Ninguna URL externa debe sobrevivir: el deck tiene que abrir sin internet.
    externas = re.findall(r'(?:src|href)="(https?:)?//[^"]+"', html)
    if externas:
        raise SystemExit(f"El deck tiene recursos externos: {externas[:5]}")

    sobrantes = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if sobrantes:
        raise SystemExit(f"Placeholders sin sustituir: {sorted(set(sobrantes))}")
    if faltan:
        raise SystemExit(f"Placeholders inexistentes en la plantilla: {faltan}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(html, encoding="utf-8")

    kb = len(html.encode("utf-8")) / 1024
    diapositivas = html.count('<section class="slide')
    print(f"[ok] {SALIDA.relative_to(RAIZ)} ({kb:.0f} KB, {diapositivas} diapositivas)")
    print("[ok] Sin recursos externos: funciona sin internet")


if __name__ == "__main__":
    main()