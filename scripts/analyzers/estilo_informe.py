"""Sistema visual del informe.

Las figuras de generate_report.py usan el estilo por defecto de seaborn, que es
legible pero generico: no comunica una intencion. Aqui se define una paleta
reductionista, una jerarquia tipografica y unas reglas de anotacion que hacen que
todas las figuras del informe se vean como parte del mismo documento.

Las fuentes son DejaVu Serif y DejaVu Sans, presentes en cualquier Linux y con
metricas compatibles con las que sustituyen en Windows y macOS. No se dependede
Google Fonts porque el informe tiene que abrirse sin internet.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

# Paleta. Un tinta profunda para lo estructural, un ambar electrico para el
# acento (el color de la categoria que domina el mercado), y un rojo apagado
# reservado para los datos que representan un problema.
TINTA = "#1B3A57"
TINTA_SUAVE = "#5A7794"
AMBAR = "#D98E04"
AMBAR_SUAVE = "#F0C674"
ROJO = "#9B2226"
ROJO_SUAVE = "#D98C8C"
VERDE = "#3F6B4E"
PANTALLA = "#FFFFFF"
TINTA_TEXTO = "#1A1A1A"
GRIS = "#6E6E6E"
REGLA = "#D9D5CC"
FONDO_SUAVE = "#F4F2ED"

# Un color por categoria, del azul al ambar, para que la serie tenga recorrido.
COLOR_CATEGORIA = {
    "Motores": TINTA,
    "Eléctricos": AMBAR,
    "Bicicletas": VERDE,
    "Patinetes Eléctricos": TINTA_SUAVE,
    "Otros": "#9C9A93",
}

SERIE = [TINTA, AMBAR, VERDE, TINTA_SUAVE, ROJO, "#6B7A8F", "#8C7A5B"]

BASE_FIG = 11.5


def aplicar() -> None:
    """Fija el estilo global. Se llama una vez antes de dibujar."""
    mpl.rcParams.update(
        {
            "figure.facecolor": PANTALLA,
            "axes.facecolor": PANTALLA,
            "savefig.facecolor": PANTALLA,
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"],
            "font.size": BASE_FIG,
            "axes.edgecolor": REGLA,
            "axes.linewidth": 0.9,
            "axes.labelcolor": TINTA_TEXTO,
            "axes.titlecolor": TINTA,
            "axes.labelsize": BASE_FIG - 0.5,
            "axes.titlesize": BASE_FIG + 3,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 16,
            "axes.labelpad": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "grid.color": REGLA,
            "grid.linewidth": 0.7,
            "xtick.color": GRIS,
            "ytick.color": GRIS,
            "xtick.labelsize": BASE_FIG - 1.5,
            "ytick.labelsize": BASE_FIG - 1.5,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "legend.frameon": False,
            "legend.fontsize": BASE_FIG - 1.5,
            "figure.dpi": 200,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.32,
        }
    )


def titulo(ax, texto: str, subtitulo: str | None = None) -> None:
    """Titulo a la izquierda, con bajada opcional en gris."""
    ax.set_title(texto, loc="left", pad=30 if subtitulo else 16)
    if subtitulo:
        ax.annotate(
            subtitulo,
            xy=(0, 1.0),
            xycoords="axes fraction",
            xytext=(0, 9),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=BASE_FIG - 2,
            color=GRIS,
        )


def barras_horizontales(
    etiquetas,
    valores,
    eje,
    colores=None,
    formato=lambda v: f"{v:,.0f}".replace(",", "."),
    sufijo=None,
    *,
    xlabel=None,
    maximo=None,
):
    """Barras horizontales con el valor a la derecha del extremo.

    Se prefiernen horizontales porque las etiquetas del estudio son palabras
    largas (nombres de marca y de municipio) y en vertical no caben.

    `sufijo` es una lista de textos alineados con `valores`, para anotar cada
    barra con un dato propio (por ejemplo el número de anuncios que la sostiene).
    """
    colores = colores or [TINTA] * len(valores)
    barras = eje.barh(etiquetas, valores, color=colores, height=0.62)
    maximo = maximo or max(valores) * 1.22
    for i, (barra, valor) in enumerate(zip(barras, valores)):
        x = barra.get_width() + maximo * 0.015
        texto = formato(valor)
        if sufijo and sufijo[i]:
            texto = f"{texto}   {sufijo[i]}"
        eje.text(
            x, barra.get_y() + barra.get_height() / 2, texto,
            va="center", ha="left", fontsize=BASE_FIG - 2, color=TINTA_TEXTO,
            fontweight="bold" if not sufijo or not sufijo[i] else "normal",
        )
    eje.set_xlim(0, maximo)
    if xlabel:
        eje.set_xlabel(xlabel)
    eje.invert_yaxis()
    return barras


def pie_de_nota(texto: str) -> None:
    """Nota al pie, alineada a la derecha y sin chocar con el eje."""
    plt.figtext(
        0.995, -0.02, texto, ha="right", va="top",
        fontsize=BASE_FIG - 2.5, color=GRIS, wrap=True,
    )


def nueva_figura(ancho=9.4, alto=5.0):
    fig, eje = plt.subplots(figsize=(ancho, alto))
    return fig, eje


def guardar(fig, ruta) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta.name