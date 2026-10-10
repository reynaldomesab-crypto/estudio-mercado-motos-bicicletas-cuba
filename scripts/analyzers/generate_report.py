"""Genera graficos y reporte estadistico del dataset curado.

Uso:
    python3 scripts/analyzers/generate_report.py

Salidas:
    analysis/figures/*.png
    analysis/resultados.json
    analysis/REPORTE.md
"""

from __future__ import annotations

import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "curated"
OUT = ROOT / "analysis"
FIG = OUT / "figures"

VEHICLES_FILE = DATA / "vehicles_curated.json"
FACEBOOK_FILE = DATA / "facebook_curated_20261002.json"
PARTS_FILE = DATA / "parts_curated.json"

# ==========================================================================
# PALETAS DE COLOR PERSONALIZADAS
# ==========================================================================
PALETAS = {
    "oceano": [
        "#0B1E3F", "#14477A", "#1F6FB2", "#3FA0D4", "#7FC8E8",
        "#B8E1F2", "#E8F6FB",
    ],
    "desierto": [
        "#3D0C02", "#7A2E12", "#B85C24", "#E08A3C", "#F2B96A",
        "#F7D9A0", "#FCEFD1",
    ],
    "selva": [
        "#0D2818", "#1B4D2E", "#2E7D4F", "#4CAF7A", "#7FCFA0",
        "#B6E5C8", "#E4F5EA",
    ],
    "cyberpunk": [
        "#0D0221", "#3A0CA3", "#7209B7", "#F72585", "#FF6B35",
        "#FFD60A", "#00F5D4",
    ],
    "vinos": [
        "#2B0B0B", "#5A1A1A", "#8B2E2E", "#B8651B", "#D9A441",
        "#E8C77E", "#F5E6C8",
    ],
    "pastel": [
        "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
        "#E0BBE4", "#FFC8DD",
    ],
    "vibrante": [
        "#E63946", "#F1A208", "#2A9D8F", "#264653", "#9B5DE5",
        "#F15BB5", "#00BBF9",
    ],
    "minimal": [
        "#1C1C1E", "#3A3A3C", "#5C5C5E", "#8E8E93",
        "#AEAEB2", "#C7C7CC", "#E5E5EA",
    ],
}

# Paleta por tipo de grafico. "vibrante" para categorias porque separa bien
# bloques vecinos; "oceano" para lo geografico.
PALETA_CATEGORICA = "vibrante"
PALETA_GEOGRAFICA = "oceano"

# En los graficos circulares laporcion mayor recibe el color mas saturado
# para que la vista vaya ahi primero, y la menor un tono apagado del mismo
# matiz. Por eso no basta con tomar dos colores seguidos de la paleta.
COLOR_ATENCION = "#8B2E2E"   # vinos: porcion dominante
COLOR_SECUNDARIO = "#E8C77E"  # vinos: porcion menor
COLOR_ATENCION_USD = "#2E7D4F"  # selva
COLOR_SECUNDARIO_USD = "#C7C7CC"  # minimal
COLOR_AUSENTE = "#E5E5EA"  # minimal: dato no declarado


def colores(n: int, nombre: str = PALETA_CATEGORICA) -> list[str]:
    """Devuelve n colores de la paleta indicada, cycling si hacen falta."""
    paleta = PALETAS[nombre]
    return [paleta[i % len(paleta)] for i in range(n)]

# Categoria unica para los vehiculos electricos de dos ruedas. Motorinas y
# Bicicletas Electricas se fusionan porque los datos no permiten separarlas de
# forma fiable: el mismo vendedor rotula indistintamente "bicimoto" y "motico"
# para el mismo producto electrico, y las plataformas clasifican por catalogo,
# no por el tipo real del vehiculo.
ELECTRICAS = "Eléctricos"

# Taxonomia normalizada del estudio: Motores, Electricas, Bicicletas,
# Patinetes Electricos y Otros.
CATEGORIA_MAP = {
    "Moto": "Motores",
    "Moto Combustión": "Motores",
    "Moto Eléctrica": ELECTRICAS,
    "Mototrina": ELECTRICAS,
    "Bicicleta Eléctrica": ELECTRICAS,
    "Bicicleta": "Bicicletas",
    "Patinete Eléctrico": "Patinetes Eléctricos",
    "Otro": "Otros",
    "Parte/Accesorio": "Partes y Accesorios",
}

# Marcas que solo comercializan vehiculos electricos y que las fuentes etiquetan
# como "Moto"/"Moto Combustion", mezclandolas con los motores de combustion
# reales. Verificado revisando los titulos uno a uno:
#   TOPMAQ     -> EXCLUIDA a proposito: es marca mixta. De sus 351 anuncios,
#                 128 son solo electricos (Bicimoto Evolution, Shikra) pero hay
#                 16 de combustion inequivocos ("Motos de Combustion TOPMAQ
#                 TANK 200cc", "TOPMAQ GN 150", "TOPMAQ RAPTOR DE COMBUSTION",
#                 "TOPMAQ AVISPON 200cc"). Forzarla a Electricos metia esas 16
#                 motos de gasolina entre las electricas, asi que se decide
#                 anuncio por anuncio con las senales de tipo de los titulos.
#   VEDCA      -> Bicimoto S1, N3, Grillo, A1, 800w, 60V30A
#   CHALLENGER -> Bicimotos X1, Prontezza, Corleone, 2000W/60V/20Ah
#   MAF        -> Bicimoto Eagle, 800W/72V20Ah, patineta electrica
#   YOAZAKY    -> "Bicimoto Yoazaky 707", 3000W/48V/50Ah, Evolution Galactica
# Se reclasifican por marca, que resulta mas fiable que la etiqueta heredada
# de cada plataforma.
# Marcas que solo comercializan vehiculos electricos y que las fuentes etiquetan
# como "Moto"/"Moto Combustion", mezclandolas con los motores de combustion
# reales. La lista no es una suposicion: se clasifico contando, en los titulos
# de cada marca, cuantos casos traen senales electricas (electrica, bicimoto,
# vataje, 0km) frente a senales de combustion (combustion, gasolina, cc).
# Veredicto medido, con el porcentaje electrico de cada una:
#   BUCATTI 88.9% | JMD 97.4% | KVITOVA 89.1% | PANDA 96.3% | INFINITY 100%
#   TRANK 100%   | VORTAX 80%   | JINGHAN 86.7% | TOPMAQ 82.6% | VEDCA 90.4%
#   CHALLENGER 69.3% | MAF 66%   | YOAZAKY 64.9%
#   TST/DEEPOWER/G29 100% (bicicletas electricas)
# Se quedan fuera por ser mixtas: AVA (54/45), XMOX (55.6/38.9), SUZUKI,
# IZUKI (62.7/22) y RALI, que venden combustion y electricos.
MARCA_SOLO_MOTORINAS = {
    "VEDCA",
    "CHALLENGER",
    "MAF",
    "YOAZAKY",
    "JMD",
    "BUCATTI",
    "KVITOVA",
    "PANDA",
    "INFINITY",
    "TRANK",
    "VORTAX",
    "JINGHAN",
    "TST",
    "DEEPOWER",
    "G29",
}

# Correcciones por marca que solo aplican a los registros que la fuente dejo en
# "Motores", porque la misma marca aparece legitimamente en otras categorias:
#   ONEBOT -> fabricante chino de bicicletas electricas; los casos que iTENCEL
#             etiquetaba como "Moto" dicen "bicicleta" o "bicimoto" en el
#             titulo (con parte de las letras en Unicode: BICICLETA).
MARCA_DESDE_MOTORES = {
    "ONEBOT": ELECTRICAS,
}

ORDEN_CATEGORIAS = [
    "Motores",
    ELECTRICAS,
    "Bicicletas",
    "Patinetes Eléctricos",
    "Otros",
]
# Umbral de muestra minima. Un grafico cuyo conjunto de datos no llega a
# este numero de elementos no se genera: con conteos tan bajos las diferencias
    # entre barras son ruido y no sostienen conclusiones. Ejemplo: las marcas de Bicicletas
# (21 publicaciones con marca) o Bicicletas Electricas (12) se descartan.
MIN_ELEMENTOS = 30

# Cuantas marcas se muestran como maximo en los graficos de marcas por
# categoria. El resto se omite para que las barras mas petites sigan siendo
# legibles.
TOP_MARCAS = 5

sns.set_theme(style="whitegrid", context="notebook")

MARCA_PATTERNS = [
    # Motores de combustion
    "TRECK", "MOTORSTRECK", "JOMAR", "KATZU", "SOUKA", "JIN", "JINCHEN",
    "UNISON", "RESTREPA", "KRATHOS", "LIFAN", "SUZUKI", "KAWASAKI", "KTM",
    "DUCATI", "HARLEY", "KEEWAY", "ZNEN", "LONCIN", "YAMAHA", "MONDIAL",
    "WYS", "VIKING", "ITALY",
    # Electricas
    "TOPMAQ", "VEDCA", "CHALLENGER", "MAF", "YOAZAKY", "MIKAZUKI", "JMD",
    "BUCATTI", "KVITOVA", "PANDA", "INFINITY", "TRANK", "VORTAX", "JINGHAN",
    "ONEBOT", "TST", "DEEPOWER", "G29", "GS", "FLY", "RAINBOW", "VOLTA",
    "FENIX", "MZ",
    # Mixtas
    "AVA", "XMOX", "IZUKI", "RALI", "MIDHA", "ORIS", "TORVAN", "LAITUNING",
    "OIM", "DCMLZ", "CHAGENGUER", "RAIBONW", "CAROMA", "ULENDO", "HALCON",
    # Bicicletas electricas (confirmadas en internet: movcan.com, dttzh.com,
    # trevalixbikes.com y eskute.com son fabricantes con dominio propio)
    "MOVCAN", "DTTZH", "TREVALIX", "ESKUTE", "VOLTRIDE",
    # Bicicletas
    "VIVAMAX", "HUFFY", "SANY", "LIMA", "BTWIN", "PORTOBELLO", "SILVERBIKE",
]

# "MOTICO" no es una marca: en los titulos es la palabra que nombra el tipo de
# vehiculo, y la marca real va justo despues
# ("MOTICO CHALLENGER CORLEONE", "MOTICO MAF 2026", "BICIMOTO / MOTICO LAITUNING").
# Se usa como senal de categoria, nunca como marca.
PALABRA_TIPO_MOTICO = re.compile(r"\bMOTICO\b", re.IGNORECASE)

# "BICIMOTO" es lo mismo: nombre del tipo, no de la marca. Aparece en 1094
# titulos y solo 2 mencionan cc o gasolina (y ambos son posts que anuncian
# ambas categorias a la vez), asi que identifica vehiculo electrico.
PALABRA_TIPO_BICIMOTO = re.compile(r"\bBICIMOTOS?\b", re.IGNORECASE)

# Senal de combustion en el titulo. Necesaria para las marcas mixtas: permite
# que "Motos de Combustion TOPMAQ TANK 200cc" seReconozca como moto de
# gasolina aunque la plataforma la archivara como electrica, y para lo mismo con
# cualquier otra marca que tenga las dos gamas.
#   350cc, 150CC, COMBUSTION, COMBUSTIBLE, GASOLINA, 4 TIEMPO, 4T
PALABRA_TIPO_COMBUSTION = re.compile(
    r"\b\d{2,3}\s*CC\b|\bCOMBUSTI\w*\b|\bGASOLINA\b|\b4\s*TIEMPOS?\b|\b4T\b|\bKM\s*/\s*L\b",
    re.IGNORECASE,
)

# Modelos que deben atribuirse a su marca. Solo se incluyen los que tienen una
# unica marca madre verificada en los titulos:
#   CORLEONE, PRONTEZZA, ELEGANT -> CHALLENGER ("MOTICO CHALLENGER CORLEONE",
#      "BICIMOTO CHALLENGER PRONTEZZA"); PROTENZZA es la errata de PRONTEZZA.
#   NOVA, MOUNTAIN -> HALCON ("Bicimotos HALCON NOVA 17 GEN 2026",
#      "Venta de Bicimoto Eléctrica marca HALCON MOUNTAIN 2026").
# NO se mapean EVOLUTION, TANK, S90, SHIKRA, GRILLO, EAGLE ni ENGLE porque son
# modelos de varias marcas a la vez: GRILLO es de MIKAZUKI, JMD y VEDCA; TANK
# de TOPMAQ, YOAZAKY y XMOX; EAGLE de MIKAZUKI, MAF y MIDHA (y ENGLE es su
# errata, siempre detras de MAF). Con esos la marca correcta es la que este en
# el titulo, no una marca fija.
MODELO_A_MARCA = {
    "CORLEONE": "CHALLENGER",
    "PRONTEZZA": "CHALLENGER",
    "PROTENZZA": "CHALLENGER",
    "ELEGANT": "CHALLENGER",
    "NOVA": "HALCON",
    "MOUNTAIN": "HALCON",
    # DAKAR es modelo de HALCON, confirmado en ficha tecnica publicada:
    # "Marca: HALCON | Modelo: DAKAR PRO 150CC".
    "DAKAR": "HALCON",
    # COCUYO es modelo de MZ ("BICIMOTO MZ COCUYO").
    "COCUYO": "MZ",
}

# Palabras que aparecen junto a una marca y que NO son marcas: son modelos o
# sufijos. No se capturan como marca, y la marca correcta es la que este en el
# titulo:
#   EVOLUTION, TANK, S90, SHIKRA  -> modelos de TOPMAQ, YOAZAKY, XMOX
#   GRILLO, ULTRA                 -> modelos de MIKAZUKI, JMD, VEDCA
#   EAGLE, ENGLE                  -> modelos de MIKAZUKI, MAF, MIDHA
#   RACING                       -> modelo de GS y de FLY
#   SPORT, SUPER, MAX, POWER, NAKED, PRO
#   PORTO                        -> forma parte de PORTO BELLO, no una marca
#
# FURIA no se agrupa: pese a que la Furia 250cc de combustion coincide con la
# Kasinski Furia, internet muestra que FURIA es un nombre de modelo reutilizado
# por varios fabricantes sin relacion (Kasinski en motos, JAVA en bicicletas,
# Holyya). Sin una marca madre unica no se puede atribuir, y se deja sin
# marca en lugar de inventar una pertenencia.

# Palabras que jamas deben capturarse como marca porque son palabras del
# tipo de vehiculo, no nombres de fabricante.
PALABRAS_NO_MARCA = {
    "MOTICO", "MOTICOS", "BICIMOTO", "BICIMOTOS", "MOTO", "MOTOS",
    "BICICLETA", "BICICLETAS", "PATINETA", "PATINETAS", "PATINETE",
    "ELECTRICA", "ELECTRICAS", "ELECTRICO", "COMBUSTION", "GASOLINA",
    "MODELO", "MARCA", "NUEVA", "NUEVO", "NUEVAS", "MOTOR", "POTENCIA",
}

# Tokens que son modelos y cuya marca madre se calcula a partir de los propios
# datos: se cuentan los titulos donde el modelo aparece junto a una marca ya
# identificada y solo se agrupa si una marca domina claramente. Asi no se
# codifica a mano ninguna atribucion que los datos no respalden.
TOKENS_MODELO = [
    "RX", "COMBAT", "EVOLUTION", "GRILLO", "ULTRA", "TANK", "SHIKRA",
    "S90", "VOLT", "SPORT", "RACING", "EAGLE", "ENGLE", "FURIA", "NAKED",
    "SUPER", "MAX", "POWER", "SHARK", "GOLDEN", "FLAMINGO", "CHEETAH",
    "SNAPDRAGON", "PRO", "SCOOTER", "MOUNTAIN", "NOVA", "CORLEONE",
]
# Una marca debe reunir al menos este porcentaje de las apariciones del modelo
# para que el modelo se le atribuya. Por debajo, el modelo se comparte entre
# marcas y se deja sin atribuir.
UMBRAL_DOMINIO_MODELO = 0.90

# Ademas el modelo debe aparecer junto a esa marca en al menos este numero de
# titulos. Sin este minimo, "SUPER" (5 casos junto a YOAZAKY) se atribuiria a
# YOAZAKY y se llevaria por delante titulos ajenos como "BICIMOTO SUPER FAST".
MIN_MUESTRAS_MODELO = 10

# El scraper agrupo bajo "Repuesto Generico" un cajon de sastre que no son
# solo repuestos: incluye vehiculos completos mal archivados y bicicletas con
# accesorios. Estas reglas describen que se anuncia realmente en cada anuncio,
# para poder enseñarlo en vez de llamar "generico" a todo.
# El orden importa: se evalua de mas especifico a mas general.
CONTENIDO_REPUESTO = [
    (
        "Baterías",
        re.compile(r"\b(BATERI\w*|ACUMULADOR\w*)\b"),
        "baterías de litio, gel o LiFePo4",
    ),
    (
        "Cargadores",
        re.compile(r"\b(CARGADOR\w*)\b"),
        "cargadores y balanceadores",
    ),
    (
        "Motores",
        re.compile(r"\b(MOTORES?|MOTORCITO\w*)\b"),
        "motores sueltos de 48V",
    ),
    (
        "Extensores de rango",
        re.compile(r"\b(EXTENSOR\w*|ALARGADOR\w*)\b"),
        "extensores y accelerators",
    ),
    (
        "Neumáticos y otros accesorios",
        re.compile(r"\b(NEUMATIC\w*|NEUMAT\w*|AROS?|GOMAS?|FRENOS?|BUJES?)\b"),
        "neumáticos, aros, frenos y bujes",
    ),
]

# Palabras que nombran el vehiculo completo. Para saber si el anuncio vende el
# vehiculo o una pieza para el, hay que mirar el contexto: "cargador DE
# bicimoto" es un repuesto, "bicimotos pequenas marca JMD" es el vehiculo.
PALABRA_VEHICULO = re.compile(
    r"\b(BICIMOTOS?|MOTORINAS?|MOTOS?|PATINETAS?|BICICLETAS?)\b"
)
# Contexto que convierte la palabra siguiente en "pieza para este vehiculo".
# Solo preposiciones, admitiendo un articulo: "para LA moto", "de LOS bicimotos".
# No se incluyen articulos sueltos ni conjunciones ("una bicimoto" y "y
# bicimoto" siguen siendo el vehiculo), porque "se vende una bicimoto" es un
# vehiculo completo aunque el titulo mencione la palabra bateria.
CONTEXTO_DE_PIEZA = re.compile(
    r"\b(DE|DEL|PARA|CON|EN)\b\s*(?:(LA|LOS|LAS|EL)\b\s*)?$"
)


def clasificar_contenido_generico(titulo: str) -> str:
    """Describe que se anuncia realmente en un anuncio de 'Repuesto Generico'.

    Decide si el vehiculo es el producto o solo el contexto de una pieza. Si el
    anuncio empieza nombrando una pieza, es una pieza aunque despues mencione
    el vehiculo al que se destina ("CARGADORES DE MOTO Y BICIMOTO").
    """
    normalizado = normalizar_para_acentos(titulo)
    if not normalizado:
        return "Accesorios y otros"

    # Regla 1: la pieza encabeza el anuncio.
    primeras = " ".join(normalizado.split()[:3])
    for nombre, patron, _ in CONTENIDO_REPUESTO:
        if patron.search(primeras):
            return nombre

    # Regla 2: aparece una especificacion tipica de bateria sin nombrarla.
    # Admite los tres separadores que usan los vendedores: 72V x 35Ah, 72V*35Ah
    # y 72V×35Ah (signo de multiplicacion).
    if re.search(r"\d+\s*V\s*[X*×]?\s*\d+\s*(?:HA|AH)\b", normalizado):
        return "Baterías"

    # Regla 3: el vehiculo es el producto y no el contexto de una pieza.
    if any(
        not CONTEXTO_DE_PIEZA.search(normalizado[: m.start()])
        for m in PALABRA_VEHICULO.finditer(normalizado)
    ):
        return "Vehículos completos mal archivados"

    for nombre, patron, _ in CONTENIDO_REPUESTO:
        if patron.search(normalizado):
            return nombre
    return "Accesorios y otros"


def normalizar_para_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn").upper()

# Mapa modelo -> marca madre calculado en runtime a partir de los titulos.
# Se llena en main() con calcular_padre_de_modelos() y solo contiene los modelos
# con una marca madre inequivoca. Vive en un modulo para que extract_brand()
# pueda consultarlo sin recibir parametros.
MAPA_MODELO_A_MARCA: dict[str, str] = {}

# Erratas de tecleo que atribuyen mal la marca.
ERRATA_A_MARCA = {
    "CHALENGER": "CHALLENGER",
    "CALLENGER": "CHALLENGER",
    "CHANLLENGER": "CHALLENGER",
    "CHALLANGER": "CHALLENGER",
    "CHELENGER": "CHALLENGER",
    "CHALENGERE": "CHALLENGER",
    "MHIDA": "MIDHA",
    "YOAZAKI": "YOAZAKY",
    "MISHOZUKI": "MIKAZUKI",
    "MIZOZHUKI": "MIKAZUKI",
    "MISHUKI": "MIKAZUKI",
    "UNIZUKI": "IZUKI",
    "UNSION": "UNISON",
    "ALCÓN": "HALCON",
    "ALCON": "HALCON",
    "HALC": "HALCON",
    "YOASAKY": "YOAZAKY",
    "DCMZL": "DCMLZ",
    "DCMZLZ": "DCMLZ",
    "PORTO BELLO": "PORTOBELLO",
    "SILVER BIKE": "SILVERBIKE",
}


def calcular_padre_de_modelos(titulos: list[str]) -> dict[str, dict]:
    """Deduce la marca madre de cada token de modelo a partir de los datos.

    Para cada token se cuentan los titulos en los que aparece junto a una marca
    ya identificada. El token solo se agrupa si una unica marca alcanza
    UMBRAL_DOMINIO_MODELO de las apariciones; en caso contrario se queda sin
    atribuir. Devuelve la evidencia (conteo y porcentaje) para poder auditarlo.
    """
    evidencia: dict[str, dict] = {}
    for token in TOKENS_MODELO:
        patron = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
        _with_marca: Counter = Counter()
        sin_marca = 0
        for titulo in titulos:
            if not patron.search(titulo):
                continue
            marca = extract_brand(titulo)
            if marca:
                _with_marca[marca] += 1
            else:
                sin_marca += 1
        if not _with_marca:
            evidencia[token] = {
                "marca_madre": None,
                "motivo": "el modelo nunca aparece junto a una marca identificada",
                "titulos_sin_marca": sin_marca,
            }
            continue
        total = sum(_with_marca.values())
        dominante, conteo = _with_marca.most_common(1)[0]
        cuota = conteo / total
        if cuota >= UMBRAL_DOMINIO_MODELO and conteo >= MIN_MUESTRAS_MODELO:
            evidencia[token] = {
                "marca_madre": dominante,
                "confianza_pct": round(cuota * 100, 1),
                "titulos_con_marca": total,
                "titulos_atribuidos": sin_marca,
                "otras_marcas": {k: v for k, v in _with_marca.most_common()[1:]},
            }
        else:
            if conteo < MIN_MUESTRAS_MODELO and cuota >= UMBRAL_DOMINIO_MODELO:
                motivo = (
                    f"aparece junto a {dominante} solo {conteo} veces "
                    f"(< {MIN_MUESTRAS_MODELO} muestras)"
                )
            else:
                motivo = (
                    "el modelo se comparte entre marcas: "
                    + ", ".join(f"{k} {v}" for k, v in _with_marca.most_common())
                )
            evidencia[token] = {
                "marca_madre": None,
                "motivo": motivo,
                "titulos_sin_marca": sin_marca,
            }
    return evidencia


def load_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload.get("items", [])
    return payload


def normalizar_texto(texto: str) -> str:
    """Normaliza erratas de tecleo y modelos antes de buscar la marca."""
    normalizado = texto.upper()
    for errata, correcto in ERRATA_A_MARCA.items():
        if errata in normalizado:
            normalizado = re.sub(
                rf"\b{re.escape(errata)}\b", correcto, normalizado
            )
    return normalizado


def extract_brand(title: str) -> str | None:
    """Extrae la marca real del titulo.

    Tres casos que requieren mas que una busqueda literal:
      1. "MOTICO" es la palabra del tipo de vehiculo, no la marca. La marca
         real va despues ("MOTICO CHALLENGER CORLEONE").
      2. Los modelos se atribuyen a su marca (CORLEONE -> CHALLENGER).
      3. Las erratas de tecleo se corrigen antes de comparar (CHALENGER).
    """
    if not isinstance(title, str) or not title.strip():
        return None
    normalizado = normalizar_texto(title)

    # 1. Cuando la marca va inmediatamente despues de "MOTICO", es la que vale:
    #    "MOTICO CHALLENGER PRONTEZZA" -> CHALLENGER, no la palabra MOTICO.
    tras_motico = re.search(
        r"\bMOTICO\b\s*(?:ELECTRICA|ELECTRICO|MARCA|DE)?\s*([A-Z]+)",
        normalizado,
    )
    if tras_motico:
        candidata = tras_motico.group(1)
        if candidata in MODELO_A_MARCA:
            return MODELO_A_MARCA[candidata]
        if candidata in MARCA_PATTERNS:
            return candidata

    # 2. Un modelo sin marca explicita se atribuye a su marca madre.
    for modelo, marca in MODELO_A_MARCA.items():
        if re.search(rf"\b{modelo}\b", normalizado):
            return marca

    # 3. Busqueda directa de marca.
    for brand in MARCA_PATTERNS:
        if re.search(rf"\b{re.escape(brand)}\b", normalizado):
            return brand

    # 4. Ultimo recurso: el titulo solo nombra un modelo, pero ese modelo tiene
    #    una unica marca madre en el corpus (mapa calculado en runtime, no fijo).
    for modelo, marca in MAPA_MODELO_A_MARCA.items():
        if re.search(rf"\b{re.escape(modelo)}\b", normalizado):
            return marca
    return None


def dedup(items: list[dict], clave: str) -> list[dict]:
    """Elimina duplicados conservando la primera aparicion de cada clave.

    Sin esto los conteos estan inflados: `parts_curated.json` repite iTENCEL
    cuatro veces y `vehicles_curated.json` ya contiene los posts de Facebook.
    """
    vistos: set = set()
    únicos: list[dict] = []
    for item in items:
        valor = item.get(clave)
        if not isinstance(valor, str) or not valor.strip():
            únicos.append(item)
            continue
        normalizado = valor.strip().rstrip("/")
        if normalizado in vistos:
            continue
        vistos.add(normalizado)
        únicos.append(item)
    return únicos


def to_frame(items: list[dict], origen: str) -> pd.DataFrame:
    df = pd.DataFrame(items)
    df["_dataset"] = origen
    return df


def price_stats(series: pd.Series) -> dict:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {}
    return {
        "n": int(clean.size),
        "min": round(float(clean.min()), 2),
        "mediana": round(float(clean.median()), 2),
        "media": round(float(clean.mean()), 2),
        "max": round(float(clean.max()), 2),
    }


def nota_al_pie(ax, lineas: list[str]) -> None:
    """Nota informativa en columna, abajo a la derecha y sin tapar el eje X.

    Se escribe por debajo del eje X (coordenadas negativas del eje) y en varias
    lineas, para que no se solape con la etiqueta "Publicaciones" ni con las
    barras. El color gris y el tamano pequeno evitan que compita con los datos.
    """
    for i, linea in enumerate(lineas):
        ax.text(
            0.99,
            -0.17 - 0.06 * i,
            linea,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=7,
            color="#777777",
        )


def save(fig, nombre: str) -> str:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / nombre
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {path.relative_to(ROOT)}")
    return str(path.relative_to(ROOT))


# --------------------------------------------------------------------------
# Reportes en texto. Se escriben aparte de los graficos porque responden a
# preguntas de lectura, no de comparacion visual.
# --------------------------------------------------------------------------

REGLAS_KM_POR_DOLAR = {
    "potencia": re.compile(r"(\d{2,5})\s*(?:W|WATTS|WAT)\b"),
    "autonomia": re.compile(r"(\d{2,3})\s*KM"),
    "bateria": re.compile(r"(\d{2,3})\s*AH\b"),
    "combustion": PALABRA_TIPO_COMBUSTION,
}


def auditar_datos_electricos(veh: pd.DataFrame) -> dict:
    """Mide cuanto se sabe de potencia y autonomia en los titulos.

    Devuelve el porcentaje de anuncios con cada dato para poder decidir, con
    numeros, si un calculo de kilometraje por dolar es representativo.
    """
    electricos = veh[veh["categoria"] == ELECTRICAS]
    total = int(len(electricos))
    con_potencia, con_autonomia, con_precio = [], [], []
    for _, fila in electricos.iterrows():
        titulo = normalizar_para_acentos(fila.get("title") or "")
        if REGLAS_KM_POR_DOLAR["potencia"].search(titulo):
            con_potencia.append(fila.get("title"))
        if REGLAS_KM_POR_DOLAR["autonomia"].search(titulo):
            con_autonomia.append(fila.get("title"))
        if pd.notna(fila.get("price_usd")):
            con_precio.append(fila.get("title"))
    audit = {
        "anuncios_electricos": total,
        "con_potencia": len(con_potencia),
        "con_potencia_pct": round(len(con_potencia) / total * 100, 1)
        if total
        else 0.0,
        "con_autonomia": len(con_autonomia),
        "con_autonomia_pct": round(len(con_autonomia) / total * 100, 1)
        if total
        else 0.0,
        "con_precio": len(con_precio),
        "con_precio_pct": round(len(con_precio) / total * 100, 1)
        if total
        else 0.0,
        # Se necesitan las tres cosas a la vez para dividir precio por autonomia.
        "con_los_tres": len(
            [1 for t in set(con_potencia) if t in set(con_autonomia)]
        ),
    }
    audit["con_los_tres_pct"] = round(audit["con_los_tres"] / total * 100, 1) if total else 0.0
    return audit


def escribir_reporte_kilometraje(veh: pd.DataFrame, ruta: Path) -> dict:
    """Kilometros por dolar en los vehiculos electricos.

    Solo se calcula si la proporcion de anuncios con los datos necesarios llega
    al 10% acordado. Si no llega, el reporte explica por que no se publica la
    cifra en vez de publicar una estimate poco fiable.
    """
    audit = auditar_datos_electricos(veh)
    lineas = [
        "# Reporte: kilometros por dolar en vehiculos electricos",
        "",
        "Generado por `scripts/analyzers/generate_report.py`.",
        "",
        "## Conclusion",
        "",
    ]

    minimo = MIN_ELEMENTOS
    if audit["con_los_tres_pct"] < 10.0:
        lineas += [
            "**No se publica esta cifra.** Los datos no alcanzan el 10% minimo que",
            "se fijó para no dar por valido un calculo construido sobre una muestra",
            "minima.",
            "",
            "| Dato disponible | Anuncios | % de los eléctricos |",
            "| --- | ---: | ---: |",
            f"| Potencia en vatios | {audit['con_potencia']} | {audit['con_potencia_pct']}% |",
            f"| Autonomia en km | {audit['con_autonomia']} | {audit['con_autonomia_pct']}% |",
            f"| Precio | {audit['con_precio']} | {audit['con_precio_pct']}% |",
            f"| **Los tres a la vez** | **{audit['con_los_tres']}** | **{audit['con_los_tres_pct']}%** |",
            "",
            f"Solo {audit['con_los_tres']} de {audit['anuncios_electricos']} anuncios eléctricos",
            "declaran a la vez potencia, autonomia y precio, que es el minimo para",
            "poder dividir distancia entre precio. Con esa proporcion, cualquier",
            "mediana de kilometros por dolar seria ruido: un unico anuncio caro o mal",
            "escrito cambiaria el resultado.",
            "",
            "Ademas, la autonomia solo aparece cuando el vendedor la escribe en el",
            "titulo, y no como campo estructurado. Los que no la ponen no son",
            "vehiculos sin autonomia, sino anuncios que no la declaran, asi que",
            "cualquier promedio calculable estaria sesgado hacia los vendedores que",
            "mejor describen su producto.",
            "",
            "Que hace falta para que este reporte sea posible: que las plataformas",
            "expongan autonomia y potencia como campos, o ampliar el scraping a las",
            "fichas completas de producto en lugar de solo al titulo.",
        ]
    else:
        electricos = veh[veh["categoria"] == ELECTRICAS].copy()
        filas = []
        for _, fila in electricos.iterrows():
            titulo = normalizar_para_acentos(fila.get("title") or "")
            autonomia = REGLAS_KM_POR_DOLAR["autonomia"].search(titulo)
            precio = pd.to_numeric(pd.Series([fila.get("price_usd")]), errors="coerce").iloc[0]
            if autonomia and pd.notna(precio) and float(precio) > 0:
                filas.append(float(autonomia.group(1)) / float(precio))
        if filas:
            filas.sort()
            mediana = filas[len(filas) // 2]
            lineas += [
                f"Kilometros por dolar (mediana de {len(filas)} anuncios): "
                f"**{mediana:.3f} km/USD**",
            ]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return audit


def _marca_legible(valor) -> str:
    """Convierte NaN o vacio en un texto legible para los reportes."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "no declarada"
    texto = str(valor).strip()
    return texto if texto and texto.lower() != "nan" else "no declarada"


def escribir_reporte_precios(veh: pd.DataFrame, ruta: Path, top: int = 10) -> list:
    """Los anuncios mas caros, con los motivos que explican su precio.

    Los motivos no se inventan: se leen de las señales presentes en el propio
    titulo (potencia, autonomia, marca, condicion de nueva,) y se lista lo que
    el anuncio dice, para que el lector pueda contrastarlo.
    """
    datos = veh.copy()
    datos["price_usd"] = pd.to_numeric(datos["price_usd"], errors="coerce")
    datos = datos.dropna(subset=["price_usd"]).sort_values(
        "price_usd", ascending=False
    )
    top_datos = datos.head(top)
    mediana = float(datos["price_usd"].median())

    senales = [
        ("Potencia elevada", REGLAS_KM_POR_DOLAR["potencia"]),
        ("Autonomia declarada", REGLAS_KM_POR_DOLAR["autonomia"]),
        ("Bateria a la venta", re.compile(r"BATERI")),
        ("Modelo o linea reconocible", re.compile(r"PREDATOR|RAPTOR|EVO\w*|SHIKRA|GRILLO|AVISP|SPORT|RACING|TANK")),
        ("Marca de referencia", re.compile(r"YAMAHA|HONDA|SUZUKI|LIFAN|IZUKI|DUCATI|HARLEY|KTM", re.IGNORECASE)),
        ("Anunciado como nuevo", re.compile(r"0KM|NUEVA|NUEVO|ESTRE|A ESTRENAR|EN CAJA", re.IGNORECASE)),
    ]

    lineas = [
        f"# Reporte: los {top} anuncios mas caros",
        "",
        "Generado por `scripts/analyzers/generate_report.py`.",
        "",
        f"Mediana de precio de todo el dataset: {mediana:.0f} USD.",
        "",
        "Los motivos se leen de las señales escritas en el propio titulo del",
        "anuncio. No son un juicio sobre el producto: son lo que el anuncio dice",
        "y por que puede costar mas que la mediana.",
        "",
    ]
    filas = []
    for _, fila in top_datos.iterrows():
        titulo = fila.get("title") or ""
        normalizado = normalizar_para_acentos(titulo)
        motivos = [nombre for nombre, patron in senales if patron.search(normalizado)]
        filas.append(
            {
                "precio_usd": float(fila["price_usd"]),
                "titulo": titulo,
                "marca": _marca_legible(fila.get("marca_detectada")),
                "categoria": fila.get("categoria"),
                "fuente": fila.get("source"),
                "url": fila.get("source_url"),
                "motivos": motivos,
            }
        )
        lineas += [
            f"## {int(fila['price_usd'])} USD — {titulo[:90]}",
            "",
            f"- Marca detectada: {_marca_legible(fila.get('marca_detectada'))}",
            f"- Categoría: {fila.get('categoria')}",
            f"- Fuente: {fila.get('source')}",
            f"- Precio: {int(fila['price_usd'])} USD "
            f"({fila['price_usd'] / mediana:.1f} veces la mediana)",
            f"- Señales en el título: {', '.join(motivos) if motivos else 'ninguna detectada'}",
            f"- Enlace: {fila.get('source_url')}",
            "",
        ]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return filas


def escribir_apendice_porcentajes(
    resultados: dict, marcas_veh: pd.DataFrame
) -> None:
    """Apendice en markdown con los porcentajes sobre el total de cada categoria.

    Los graficos muestran conteos absolutos. Aqui se documenta que porcentaje
    representa cada marca dentro de su categoria, dato que solo puede calcularse
    cuando se conoce el total de la categoria (y que por eso no cabe en las
    etiquetas de las barras).
    """
    lineas: list[str] = [
        "# Apendice: porcentajes sobre el maximo representable",
        "",
        "Generado por `scripts/analyzers/generate_report.py`. Los graficos de",
        "`figures/` ya muestran el porcentaje de cada barra respecto al maximo",
        "representable; aqui se documenta el detalle completo, incluida la",
        "cobertura de la deteccion de marcas.",
        "",
        f"Umbral de muestra minima aplicado: {MIN_ELEMENTOS} elementos.",
        f"Marcas mostradas por grafico: top {TOP_MARCAS} con mas de un elemento.",
        "",
        "> El porcentaje se calcula sobre el maximo representable (el primer",
        "> numero), no sobre el total de la categoria. Por eso las cifras no",
        "> suman 100% del total: la mayoria de las publicaciones no menciona",
        "> marca en el titulo.",
        "",
    ]

    for categoria in ORDEN_CATEGORIAS:
        total_cat = int((resultados.get("categorias_vehiculo") or {}).get(categoria, 0))
        if not total_cat or categoria == "Otros":
            continue
        sub = marcas_veh[marcas_veh["categoria"] == categoria]
        if len(sub) < MIN_ELEMENTOS:
            lineas += [
                f"## {categoria}",
                "",
                f"Publicaciones en la categoria: {total_cat}.",
                f"Con marca detectable: {len(sub)} ({len(sub) / total_cat * 100:.1f}% de la "
                f"categoria).",
                "",
                f"Se omite el detalle por marca: no alcanza el minimo de "
                f"{MIN_ELEMENTOS} elementos.",
                "",
            ]
            continue
        conteo = sub["marca_detectada"].value_counts()
        representables = conteo[conteo > 1]
        conteo_plot = representables.head(TOP_MARCAS)
        maximo = int(representables.sum())
        lineas += [
            f"## {categoria}",
            "",
            f"Total de entradas de la categoria: {total_cat}. Con marca detectable: "
            f"{len(sub)} ({len(sub) / total_cat * 100:.1f}% de la categoria).",
            f"Máximo representable (todas las marcas con mas de un elemento, antes "
            f"del corte de las {TOP_MARCAS} mas publicadas): {maximo} "
            f"({maximo / total_cat * 100:.1f}% de la categoria).",
            "",
            "Los porcentajes de la tabla son sobre el máximo representable, que es el "
            "primer número.",
            "",
            f"| Marca | Publicaciones | % del máximo representable |",
            f"| --- | ---: | ---: |",
        ]
        for marca, n in conteo_plot.items():
            lineas.append(f"| {marca} | {int(n)} | {n / maximo * 100:.2f}% |")
        lineas += [
            "",
            f"**Suma de las {len(conteo_plot)} marcas mostradas:** "
            f"{int(conteo_plot.sum())} publicaciones "
            f"({conteo_plot.sum() / maximo * 100:.1f}% del máximo representable).",
            "",
        ]

    lineas += [
        "## Graficos excluidos por falta de muestra",
        "",
        "| Gráfico | Elementos | Motivo |",
        "| --- | ---: | --- |",
    ]
    for item in resultados.get("descartados_por_muestra", []):
        lineas.append(
            f"| {item['grafico']} | {item['elementos']} | {item['motivo']} |"
        )
    lineas.append("")

    ruta = OUT / "APENDICE_PORCENTAJES.md"
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    print(f"  [ok] {ruta.relative_to(ROOT)}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    veh_raw = load_json(VEHICLES_FILE)
    veh_items = dedup(veh_raw, "source_url")
    parts_items = dedup(load_json(PARTS_FILE), "source_url")

    # El mapa modelo -> marca madre se deduce de estos mismos titulos antes de
    # extraer marcas, para que los titulos que solo nombran un modelo ("Bicimoto
    # Grillo") tambien se puedan atribuir.
    global MAPA_MODELO_A_MARCA
    MAPA_MODELO_A_MARCA = {
        token: ev["marca_madre"]
        for token, ev in calcular_padre_de_modelos(
            [i.get("title") or "" for i in veh_items + parts_items]
        ).items()
        if ev.get("marca_madre")
    }

    veh = to_frame(veh_items, "vehicles_curated")
    parts = to_frame(parts_items, "parts_curated")

    if "brand" not in veh.columns:
        veh["brand"] = None

    veh["marca_detectada"] = veh["brand"].where(
        ~veh["brand"].astype(str).str.fullmatch(
            r"\s*moticos?\s*(electrica|electrico)?\s*", case=False, na=True
        )
    )
    veh["marca_detectada"] = veh["marca_detectada"].fillna(
        veh["title"].map(extract_brand)
    )
    veh["marca_detectada"] = veh["marca_detectada"].str.upper()
    parts["marca_detectada"] = parts["title"].map(extract_brand).str.upper()
    veh["categoria"] = veh["vehicle_type"].map(CATEGORIA_MAP).fillna("Otros")
    veh["categoria_original"] = veh["categoria"]
    titulos = veh["title"].fillna("")

    # "MOTICO" y "BICIMOTO" en el titulo identifican un vehiculo electrico de
    # dos ruedas, aunque la plataforma lo haya guardado en otra categoria
    # ("Moto", "Moto Combustion", "Otro"). Es la misma senal que ahora agrupa
    # motorinas y bicicletas electricas en la categoria ELECTRICAS.
    es_tipo_electrico = titulos.str.contains(
        f"{PALABRA_TIPO_MOTICO.pattern}|{PALABRA_TIPO_BICIMOTO.pattern}",
        case=False,
        regex=True,
    )
    veh.loc[es_tipo_electrico, "categoria"] = ELECTRICAS

    # La senal de combustion manda cuando el titulo la menciona, para las marcas
    # de dos gamas. Se aplica despues de la electrica y antes de la marca, de
    # modo que "MOTORES DE BICIMOTOS..." sin cc siga siendo pieza electrica y
    # "Motos de Combustion TOPMAQ TANK 200cc" acabe en Motores.
    es_tipo_combustion = titulos.str.contains(
        PALABRA_TIPO_COMBUSTION.pattern, case=False, regex=True
    )
    solo_combustion = es_tipo_combustion & ~es_tipo_electrico
    combustion_a_motores = solo_combustion & (veh["categoria"] == ELECTRICAS)
    veh.loc[combustion_a_motores, "categoria"] = "Motores"

    # Reclasificacion por marca: VEDCA, CHALLENGER y MAF solo comercializan
    # electricos, aunque la fuente las etiquete como moto de combustion.
    es_motorina = veh["marca_detectada"].isin(MARCA_SOLO_MOTORINAS)
    veh.loc[es_motorina & ~es_tipo_combustion, "categoria"] = ELECTRICAS
    reclasificadas = int(
        (es_motorina & (veh["categoria_original"] == "Motores")).sum()
    )
    por_motico = int((es_tipo_electrico & (veh["categoria_original"] == "Motores")).sum())

    # Correcciones por marca que solo tocan lo que la fuente dejo en "Motores".
    detalle_correccion: dict[str, int] = {}
    for marca, destino in MARCA_DESDE_MOTORES.items():
        mascara = (veh["marca_detectada"] == marca) & (
            veh["categoria_original"] == "Motores"
        )
        detalle_correccion[marca] = int(mascara.sum())
        veh.loc[mascara, "categoria"] = destino
    parts["categoria"] = parts["part_category"].map(CATEGORIA_MAP).fillna(
        parts["part_category"]
    )

    todos_veh = veh
    resultados: dict = {
        "volumen": {
            "vehicles_curated_bruto": int(len(veh_raw)),
            "vehiculos_deduplicados": int(len(veh)),
            "duplicados_vehiculos": int(len(veh_raw) - len(veh)),
            "repuestos_bruto": int(len(load_json(PARTS_FILE))),
            "repuestos_deduplicados": int(len(parts)),
        },
        "reclasificacion_marcas_motorinas": {
            "marcas": sorted(MARCA_SOLO_MOTORINAS),
            "de_motores_a_electricas": reclasificadas,
        },
        "senal_tipo_electrico_en_titulo": {
            "total": int(es_tipo_electrico.sum()),
            "de_motores_a_electricas": por_motico,
        },
        "senal_tipo_combustion_en_titulo": {
            "titulos_con_senal": int(es_tipo_combustion.sum()),
            # Anuncios de marcas que solo vendian electricos pero cuyo titulo
            # delata un motor de combustion: son los que la reclasificacion
            # por marca habria mandado a la categoria equivoca.
            "exentos_por_marca_solo_electrica": int(
                (es_motorina & es_tipo_combustion).sum()
            ),
            "marcas_mixtas_detectadas": ["TOPMAQ"],
        },
        "reclasificacion_desde_motores": {
            marca: {"destino": destino, "registros": n}
            for marca, destino in MARCA_DESDE_MOTORES.items()
            for n in [detalle_correccion[marca]]
        },
    }

    print("Generando graficos...")

    # 01 Distribucion por categoria de vehiculo (taxonomia normalizada)
    conteo_tipo = (
        todos_veh["categoria"].value_counts().reindex(ORDEN_CATEGORIAS).dropna()
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=conteo_tipo.values,
        y=conteo_tipo.index,
        ax=ax,
        palette=colores(len(conteo_tipo)),
    )
    for i, v in enumerate(conteo_tipo.values):
        ax.text(v + 10, i, f"{v} ({v / len(todos_veh) * 100:.1f}%)", va="center")
    ax.set_title("Distribución de publicaciones por categoría de vehículo")
    ax.set_xlabel("Publicaciones")
    ax.set_ylabel("Categoría")
    resultados["categorias_vehiculo"] = conteo_tipo.to_dict()
    save(fig, "01_tipos_vehiculo.png")

    # 01.1 Mismo desglose, un panel por fuente. Cada panel muestra el conteo y
    # el porcentaje dentro de esa fuente, porque las fuentes tienen volumenes muy
    # distintos (itencel 1711 vs elyerro 210) y la escala absoluta
    # aplasta a las pequenas. Los dos scrapers de ElYerroMenu se agregan en un
    # solo panel porque son la misma plataforma con dos catalogos.
    todos_veh = todos_veh.assign(
        _fuente=todos_veh["source"].replace(
            {"elyerro_motos": "elyerro", "elyerro_bicicletas": "elyerro"}
        )
    )
    # Cada fuente se guarda como PNG independiente dentro de una carpeta propia:
    # sirven como fichas de plataforma y permiten compararlas una a una.
    FUENTES_DIR = FIG / "categorias_por_fuente"
    detalle_fuentes: dict = {}
    for fuente in todos_veh["_fuente"].value_counts().index.tolist():
        sub = todos_veh[todos_veh["_fuente"] == fuente]
        conteo = sub["categoria"].value_counts().reindex(ORDEN_CATEGORIAS).fillna(0)
        total_fuente = int(len(sub))
        fig, ax = plt.subplots(figsize=(11, 6))
        sns.barplot(
            x=conteo.values,
            y=conteo.index,
            ax=ax,
            palette=colores(len(conteo)),
        )
        for i, v in enumerate(conteo.values):
            if v:
                ax.text(
                    v + total_fuente * 0.012,
                    i,
                    f"{int(v)} ({v / total_fuente * 100:.1f}%)",
                    va="center",
                    fontsize=9,
                )
        ax.set_title(
            f"{fuente}: distribución de categorías\n"
            f"n={total_fuente} publicaciones, porcentaje dentro de la fuente",
            fontsize=13,
        )
        ax.set_xlabel("Publicaciones")
        ax.set_ylabel("Categoría")
        ax.set_xlim(0, conteo.max() * 1.35 if conteo.max() else 1)
        ax.text(
            0.99,
            -0.16,
            f"Fuente: {fuente} | n={total_fuente} | parte de {len(todos_veh)} publicaciones del estudio",
            transform=ax.transAxes,
            ha="right",
            fontsize=8,
            color="#555555",
        )
        detalle_fuentes[fuente] = {
            "total": total_fuente,
            "categorias": {k: int(v) for k, v in conteo.items() if v},
        }
        FUENTES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            FUENTES_DIR / f"{fuente}.png", dpi=140, bbox_inches="tight"
        )
        plt.close(fig)
        print(f"  [ok] {(FUENTES_DIR / f'{fuente}.png').relative_to(ROOT)}")

    resultados["categorias_por_fuente_detalle"] = detalle_fuentes

    # El antiguo 02 (categorias apiladas por fuente) se elimino: el grafico
    # 01.1 ya muestra el mismo cruce fuente x categoria con mas detalle
    # (conteos, porcentajes y escala propia por fuente).

    # 03 Marcas por categoria. Solo se generan las categorias que superan
    # MIN_ELEMENTOS publicaciones con marca detectable; las demas se listan en
    # `descartados_por_muestra` para que queden documentadas.
    marcas_veh = todos_veh.dropna(subset=["marca_detectada"])
    descartados: list[dict] = []
    if not marcas_veh.empty:
        detalle_marcas: dict = {}
        for categoria in ORDEN_CATEGORIAS:
            # "Otros" no se grafica: mezcla categorias sin identificar y sus
            # marcas no significan nada como grupo.
            if categoria == "Otros":
                continue
            sub = marcas_veh[marcas_veh["categoria"] == categoria]
            total_cat = int((todos_veh["categoria"] == categoria).sum())
            if len(sub) < MIN_ELEMENTOS:
                descartados.append(
                    {
                        "grafico": f"03_marcas_{categoria}",
                        "categoria": categoria,
                        "elementos": int(len(sub)),
                        "motivo": f"menos de {MIN_ELEMENTOS} publicaciones con marca",
                    }
                )
                print(
                    f"  [descartado] marcas de {categoria}: "
                    f"{len(sub)} publicaciones con marca (< {MIN_ELEMENTOS})"
                )
                continue
            conteo = sub["marca_detectada"].value_counts()
            # Se retiran las marcas con un solo elemento (ruido de la extraccion
            # por titulo) y se muestran solo las TOP_MARCAS mas publicadas.
            # El maximo representable es lo que se podria mostrar sin el corte
            # de 10 marcas, no lo que acaba pintado: asi el grafico declara
            # cuanto se deja fuera y por que las barras no suman 100%.
            representables = conteo[conteo > 1]
            conteo_plot = representables.head(TOP_MARCAS)
            maximo_representable = int(representables.sum())
            fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(conteo_plot))))
            sns.barplot(
                x=conteo_plot.values,
                y=conteo_plot.index,
                ax=ax,
                palette=colores(len(conteo_plot)),
            )
            for i, v in enumerate(conteo_plot.values):
                ax.text(
                    v + conteo_plot.max() * 0.015,
                    i,
                    f"{int(v)} ({v / maximo_representable * 100:.1f}%)",
                    va="center",
                    fontsize=9,
                )
            ax.set_title(f"Marcas detectadas — {categoria}", fontsize=13)
            ax.set_xlabel("Publicaciones")
            ax.set_ylabel("Marca")
            ax.set_xlim(0, conteo_plot.max() * 1.45)
            nota_al_pie(
                ax,
                [
                    f"Máximo representable: {maximo_representable}",
                    f"Total de entradas de la categoría: {total_cat}",
                    f"Marcas mostradas: {len(conteo_plot)} de {len(representables)}",
                ],
            )
            slug = categoria.lower().replace(" ", "_").replace("é", "e")
            detalle_marcas[categoria] = {
                "con_marca": int(len(sub)),
                "total_categoria": total_cat,
                "maximo_representable": maximo_representable,
                "mostradas": int(len(conteo_plot)),
                "representables": int(len(representables)),
                "marcas_omitidas_un_elemento": {
                    k: int(v) for k, v in conteo[conteo <= 1].items()
                },
                "marcas": {k: int(v) for k, v in conteo_plot.items()},
            }
            save(fig, f"03_marcas_{slug}.png")

        resultados["marcas_por_categoria"] = detalle_marcas
        resultados["marcas_vehiculos"] = {
            "con_marca": int(marcas_veh.shape[0]),
            "total": int(len(todos_veh)),
            "top_global": marcas_veh["marca_detectada"].value_counts().head(15).to_dict(),
        }

        # El grafico 04 (marcas apiladas por categoria) se elimino: repetia la
        # misma informacion que los 03 por categoria, que ya muestran cada
        # marca con su conteo y su porcentaje sobre el maximo representable.

    # 02 Cuanta informacion de primer orden traen los anuncios. Se anade como
    # grafico propio y no sustituye a ninguno: muestra el porcentaje de
    # publicaciones que declaran marca y las que declaran precio, que son los dos
    # datos basicos sin los cuales no se puede comparar ni marcar tendencia.
    campos_clave = {
        "Marca declarada": int(todos_veh["marca_detectada"].notna().sum()),
        "Precio declarado": int(
            pd.to_numeric(todos_veh["price_usd"], errors="coerce").notna().sum()
        ),
    }
    total_anuncios = int(len(todos_veh))
    faltantes = {
        "Marca no declarada": total_anuncios - campos_clave["Marca declarada"],
        "Precio no declarado": total_anuncios - campos_clave["Precio declarado"],
    }
    etiquetas_orden = [
        "Marca declarada",
        "Marca no declarada",
        "Precio declarada",
        "Precio no declarado",
    ]
    valores_orden = [
        campos_clave["Marca declarada"],
        faltantes["Marca no declarada"],
        campos_clave["Precio declarado"],
        faltantes["Precio no declarado"],
    ]
    # Lo declarado lleva color fuerte y lo ausente un gris apagado: la
    # comparacion que importa es cuanto se sabe frente a cuanto falta.
    colores_orden = [
        PALETAS["selva"][2],   # marca declarada
        COLOR_AUSENTE,         # marca no declarada
        PALETAS["oceano"][2],  # precio declarado
        COLOR_AUSENTE,         # precio no declarado
    ]

    fig, ax_cob = plt.subplots(figsize=(10, 6))
    barras = ax_cob.bar(
        list(range(len(etiquetas_orden))),
        valores_orden,
        color=colores_orden,
        width=0.55,
    )
    for barra, valor in zip(barras, valores_orden):
        porcentaje = valor / total_anuncios * 100
        ax_cob.text(
            barra.get_x() + barra.get_width() / 2,
            valor + total_anuncios * 0.015,
            f"{valor}\n{porcentaje:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    ax_cob.set_xticks(list(range(len(etiquetas_orden))))
    ax_cob.set_xticklabels(etiquetas_orden, fontsize=10)
    ax_cob.set_ylim(0, total_anuncios * 1.22)
    ax_cob.set_ylabel("Publicaciones")
    ax_cob.set_xlabel("Dato del anuncio")
    ax_cob.set_title(
        "Información de primer orden disponible en los anuncios",
        fontsize=13,
    )
    plt.tight_layout()
    nota_al_pie(
        ax_cob,
        [
            f"Total de anuncios: {total_anuncios}",
            f"Con marca: {campos_clave['Marca declarada']} "
            f"({campos_clave['Marca declarada'] / total_anuncios * 100:.1f}%)",
            f"Con precio: {campos_clave['Precio declarado']} "
            f"({campos_clave['Precio declarado'] / total_anuncios * 100:.1f}%)",
        ],
    )
    resultados["cobertura_informacion"] = {
        "total_anuncios": total_anuncios,
        "con_marca": campos_clave["Marca declarada"],
        "con_marca_pct": round(
            campos_clave["Marca declarada"] / total_anuncios * 100, 1
        ),
        "con_precio": campos_clave["Precio declarado"],
        "con_precio_pct": round(
            campos_clave["Precio declarado"] / total_anuncios * 100, 1
        ),
    }
    save(fig, "02_cobertura_informacion.png")

    # Los graficos 05, 06 y 07 (categorias de repuestos, marcas de repuestos y
    # marcas por categoria de repuesto) se eliminaron: la comparativa entre
    # vehiculos y repuestos queda cubierta por el grafico circular, que ademas
    # corrige el error de archivo que arrastraban.

    # 05 Comparativa de vehiculos frente a repuestos.
    #
    # No se comparan los dos archivos tal cual: la mitad de los anuncios
    # archivados como repuestos venden en realidad un vehiculo completo. Se
    # separan primero y luego se agrupan en un unico total de repuestos, de modo
    # que las dos categorias de repuestos (las piezas reales y los vehiculos mal
    # archivados) cuentan como lo que son: anuncios del archivo de repuestos.
    def es_vehiculo_completo(titulo: str) -> bool:
        normalizado = normalizar_para_acentos(titulo)
        for coincidencia in PALABRA_VEHICULO.finditer(normalizado):
            if not CONTEXTO_DE_PIEZA.search(normalizado[: coincidencia.start()]):
                return True
        return False

    vehicles_mal_archivos = int(parts["title"].map(es_vehiculo_completo).sum())
    repuestos_reales = int(len(parts) - vehicles_mal_archivos)
    total_repuestos = int(len(parts))

    # La proporcion mayor recibe el color mas saturado para que la vista vaya
    # primero ahi; la menor, un tono apagado del mismo matiz.
    segmentos = [
        ("Vehículos", int(len(todos_veh)), COLOR_ATENCION),
        ("Repuestos totales", total_repuestos, COLOR_SECUNDARIO),
    ]
    total_mercado = int(len(todos_veh) + total_repuestos)
    colores_segmento = [color for _, _, color in segmentos]
    valores = [valor for _, valor, _ in segmentos]
    porcentajes = [valor / total_mercado * 100 for valor in valores]

    fig, eje_anillo = plt.subplots(figsize=(9, 9))
    wedges, _textos = eje_anillo.pie(
        valores,
        colors=colores_segmento,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.40, "edgecolor": "white", "linewidth": 2.5},
    )

    # El porcentaje se coloca a mano y con tamano proporcional al angulo de su
    # porcion. Con un unico tamano, el texto del 5% no cabia dentro del sector
    # y se salia de el; al escalar segun la porcion, la del 95% conserva letra
    # grande y la del 5% usa una que entra sin desbordar.
    for indice, wedge in enumerate(wedges):
        angulo_medio = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        radio = 0.79
        tamano = float(np.clip(porcentajes[indice] * 2.4, 9.0, 21.0))
        eje_anillo.text(
            radio * np.cos(angulo_medio),
            radio * np.sin(angulo_medio),
            f"{porcentajes[indice]:.1f}%",
            ha="center",
            va="center",
            fontsize=tamano,
            fontweight="bold",
            color="white",
        )

    eje_anillo.text(
        0,
        0,
        f"{total_mercado:,}".replace(",", " ")
        + "\nanuncios\núnicos",
        ha="center",
        va="center",
        fontsize=15,
    )
    # El titulo va en la figura, no en el eje: asi el eje queda libre y el
    # titulo nunca compite con las etiquetas del anillo.
    fig.text(
        0.5,
        0.965,
        "Vehículos frente a repuestos",
        ha="center",
        va="center",
        fontsize=15,
    )

    manejadores = [
        plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none")
        for _, _, color in segmentos
    ]
    fig.legend(
        manejadores,
        [
            f"{nombre}  ·  {valor} anuncios  ·  {pct:.1f}%"
            for (nombre, valor, _), pct in zip(segmentos, porcentajes)
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.035),
        ncol=2,
        frameon=False,
        fontsize=11,
        handlelength=1.1,
        handleheight=1.1,
        columnspacing=3.0,
    )
    nota_al_pie(
        eje_anillo,
        [
            f"De los {total_repuestos} anuncios de repuestos, {vehicles_mal_archivos} "
            "venden un vehículo completo mal archivado.",
            f"Piezas de repuesto reales: {repuestos_reales}.",
        ],
    )
    plt.subplots_adjust(bottom=0.11, top=0.94)
    resultados["comparativa_vehiculos_repuestos"] = {
        "vehiculos": int(len(todos_veh)),
        "repuestos_totales": total_repuestos,
        "total": total_mercado,
        "porcentajes": {
            nombre: round(pct, 2)
            for (nombre, _, _), pct in zip(segmentos, porcentajes)
        },
        "detalle_repuestos": {
            "vehiculos_mal_archivados": vehicles_mal_archivos,
            "piezas_reales": repuestos_reales,
        },
    }
    save(fig, "05_comparativa_vehiculos_repuestos.png")

    # 08 Distribucion de precios por tipo de vehiculo
    precios = todos_veh.copy()
    precios["price_usd"] = pd.to_numeric(precios["price_usd"], errors="coerce")
    precios = precios.dropna(subset=["price_usd"])
    precios = precios[precios["price_usd"] <= precios["price_usd"].quantile(0.99)]
    # Cada categoria necesita al menos MIN_ELEMENTOS publicaciones con precio,
    # si no la caja no es interpretable.
    precios = precios.groupby("categoria").filter(lambda g: len(g) >= MIN_ELEMENTOS)
    # La categoria "Otros" no se representa: agrupa publicaciones sin
    # identificar, asi que su precio no describe un mercado concreto y solo
    # adds ruido al comparar. Se descarta solo del grafico, no del dataset.
    precios = precios[precios["categoria"] != "Otros"]
    if not precios.empty:
        orden = precios.groupby("categoria")["price_usd"].median().sort_values(
            ascending=False
        ).index
        resumen = precios.groupby("categoria")["price_usd"].median()

        # Dispersion de cada anuncio, coloreada por categoria. Se sustituye el
        # diagrama de caja porque este solo resumia en cinco numeros y ocultaba
        # cuantos anuncios hay, como se concentran y si hay grupos separados de
        # precios. Un segundo eje no es viable: `view_count` solo cubre el 53%
        # de los registros y `updated_at` esta vacio, asi que un dispersion
        # precio contra otra variable descartaria la mitad de los datos.
        fig, ax = plt.subplots(figsize=(13, 8))
        sns.stripplot(
            data=precios,
            x="categoria",
            y="price_usd",
            order=orden,
            hue="categoria",
            palette=colores(len(orden)),
            jitter=0.32,
            size=2.4,
            alpha=0.5,
            linewidth=0,
            ax=ax,
        )
        # Escala lineal, no logaritmica: permite leer el precio en su unidad
        # real y comparar las distancias entre categorias de forma directa.
        ax.set_title(
            "Dispersión de precios por categoría de vehículo\n"
            "cada punto es un anuncio",
            fontsize=13,
        )
        ax.set_xlabel("Categoría de vehículo")
        ax.set_ylabel("Precio USD")

        # Medianas sobre la nube de puntos, para no perder la referencia que
        # daba el diagrama de caja.
        for posicion, categoria in enumerate(orden):
            ax.plot(
                posicion,
                resumen[categoria],
                marker="_",
                markersize=26,
                markeredgewidth=2.4,
                color="#222222",
                linestyle="none",
                zorder=5,
            )

        # Fuera del eje se declara cuanto representa cada categoria, porque al
        # ser categorias distintas los puntos no se comparan entre si.
        nota_al_pie(
            ax,
            [
                f"Anuncios con precio: {len(precios)}",
                f"Máximo representable: {len(precios)}",
                f"Total de entradas: {len(todos_veh)}",
                "Barra horizontal negra: mediana de la categoría.",
            ]
            + [
                f"{c}: {resumen[c]:.0f} USD de mediana"
                for c in reversed(list(orden))
            ],
        )
        plt.tight_layout()
        resultados["precio_por_tipo"] = {
            str(k): price_stats(g["price_usd"])
            for k, g in precios.groupby("categoria")
        }
        save(fig, "08_precio_por_tipo.png")

    # El grafico 09 (histograma de precios) se elimino.

    # 10 Municipios de La Habana. Solo los 5 con mas publicaciones y sin el
    # panel de precio en escala logaritmica.
    habana = veh[veh["province_name"] == "La Habana"].copy()
    habana["price_usd"] = pd.to_numeric(habana["price_usd"], errors="coerce")
    conteo_mun = habana["municipality_name"].value_counts().head(5)
    if not conteo_mun.empty:
        fig, ax_mun = plt.subplots(figsize=(11, 6))
        sns.barplot(
            x=conteo_mun.index,
            y=conteo_mun.values,
            ax=ax_mun,
            palette=colores(len(conteo_mun), PALETA_GEOGRAFICA),
            width=0.5,
        )
        for i, valor in enumerate(conteo_mun.values):
            ax_mun.text(i, valor + conteo_mun.max() * 0.015, str(valor), ha="center")
        ax_mun.set_title("Municipios de La Habana con más publicaciones", fontsize=13)
        ax_mun.set_xlabel("Municipio")
        ax_mun.set_ylabel("Publicaciones")
        ax_mun.set_ylim(0, conteo_mun.max() * 1.15)
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        nota_al_pie(
            ax_mun,
            [
                f"Municipios mostrados: {len(conteo_mun)}",
                f"Total de anuncios de La Habana: {int(len(habana))}",
                "Municipios omitidos por tener menos de "
                f"{MIN_ELEMENTOS} publicaciones.",
            ],
        )
        resultados["municipios_habana"] = {
            "conteo": conteo_mun.to_dict(),
            "total_habana": int(len(habana)),
        }
        save(fig, "10_municipios_habana.png")

    # El grafico 11 (publicaciones por provincia) se elimino: la cobertura
    # geografica del dataset se limita a La Habana y el resto de provincias
    # suman menos de 30 anuncios cada una, asi que la barra no sostiene ningun
    # valor estadistico.

    # 12 Publicaciones por fuente. Barras horizontales y sin el panel de
    # cobertura de campos, que ahora vive en su propio grafico (02) porque la
    # cobertura de marca y precio es informacion de primer orden.
    fuentes = veh["source"].value_counts()
    fig, ax_fuente = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=fuentes.values,
        y=fuentes.index,
        ax=ax_fuente,
        palette=colores(len(fuentes)),
        width=0.5,
    )
    total_fuentes = int(fuentes.sum())
    for i, valor in enumerate(fuentes.values):
        ax_fuente.text(
            valor + fuentes.max() * 0.015,
            i,
            f"{valor} ({valor / total_fuentes * 100:.1f}%)",
            va="center",
            fontsize=9,
        )
    ax_fuente.set_title("Publicaciones por fuente", fontsize=13)
    ax_fuente.set_xlabel("Publicaciones")
    ax_fuente.set_ylabel("Fuente")
    ax_fuente.set_xlim(0, fuentes.max() * 1.28)
    plt.tight_layout()
    nota_al_pie(
        ax_fuente,
        [
            f"Total de anuncios: {total_fuentes}",
            f"Fuentes distintas: {len(fuentes)}",
        ],
    )
    resultados["fuentes"] = fuentes.to_dict()
    save(fig, "12_publicaciones_por_fuente.png")

    # 13 Moneda de las publicaciones, en dos valores. Se agrupa todo lo que no
    # es USD en "Otros" porque cada moneda alternativa (CUP, ZELLE, EUR) tiene
    # muy pocos anuncios y por separado no sostiene lectura.
    monedas = veh["currency"].dropna()
    conteo_usd = int((monedas == "USD").sum())
    conteo_otros = int(len(monedas) - conteo_usd)
    if conteo_usd + conteo_otros > 0:
        total_con_moneda = conteo_usd + conteo_otros
        segmentos_moneda = [
            ("USD", conteo_usd, COLOR_ATENCION_USD),
            ("Otros", conteo_otros, COLOR_SECUNDARIO_USD),
        ]
        # Los porcentajes van fuera del anillo: el sector de "Otros" es del
        # 1,6% y ninguna letra cabe dentro de el sin desbordarse.
        fig, ax_moneda = plt.subplots(figsize=(8, 8))
        porcentajes_moneda = [
            conteo_usd / total_con_moneda * 100,
            conteo_otros / total_con_moneda * 100,
        ]
        wedges_m, _t = ax_moneda.pie(
            [conteo_usd, conteo_otros],
            colors=[color for _, _, color in segmentos_moneda],
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.40, "edgecolor": "white", "linewidth": 2.5},
        )
        for indice, wedge in enumerate(wedges_m):
            angulo_medio = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
            radio = 1.04
            ax_moneda.text(
                radio * np.cos(angulo_medio),
                radio * np.sin(angulo_medio),
                f"{porcentajes_moneda[indice]:.1f}%",
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
                color=segmentos_moneda[indice][2],
            )
        ax_moneda.text(
            0,
            0,
            f"{total_con_moneda:,}".replace(",", " ")
            + "\nanuncios\ncon moneda",
            ha="center",
            va="center",
            fontsize=13,
        )
        ax_moneda.set_xlim(-1.45, 1.45)
        ax_moneda.set_ylim(-1.35, 1.35)
        fig.text(
            0.5,
            0.965,
            "Moneda de las publicaciones",
            ha="center",
            va="center",
            fontsize=15,
        )
        fig.legend(
            [
                plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none")
                for _, _, color in segmentos_moneda
            ],
            [
                f"{nombre}  ·  {valor} anuncios  ·  "
                f"{valor / total_con_moneda * 100:.1f}%"
                for nombre, valor, _ in segmentos_moneda
            ],
            loc="lower center",
            bbox_to_anchor=(0.5, 0.04),
            ncol=2,
            frameon=False,
            fontsize=11,
            handlelength=1.1,
            handleheight=1.1,
            columnspacing=3.0,
        )
        plt.subplots_adjust(bottom=0.11, top=0.94)
        resultados["monedas"] = {
            "USD": conteo_usd,
            "otros": conteo_otros,
            "total_con_moneda": total_con_moneda,
            "detalle_otras": {
                moneda: int(cantidad)
                for moneda, cantidad in veh["currency"]
                .dropna()
                .value_counts()
                .items()
                if moneda != "USD"
            },
        }
        save(fig, "13_monedas.png")

    # Los graficos 15 (contacto y promocion), 16 (heatmap categoria x fuente)
    # y 17 (engagement de Facebook) se eliminaron.

    resultados["descartados_por_muestra"] = descartados
    resultados["min_elementos"] = MIN_ELEMENTOS

    # Reportes en texto: no son graficos, responden preguntas de lectura.
    audit_km = escribir_reporte_kilometraje(todos_veh, OUT / "REPORTE_KM_POR_DOLAR.md")
    top_precios = escribir_reporte_precios(todos_veh, OUT / "REPORTE_PRECIOS_TOP.md")
    resultados["auditoria_datos_electricos"] = audit_km
    resultados["top_precios"] = top_precios

    escribir_apendice_porcentajes(resultados, marcas_veh)

    (OUT / "resultados.json").write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"  [ok] {(OUT / 'resultados.json').relative_to(ROOT)}")
    print(f"\nTotal figuras generadas: {len(list(FIG.glob('*.png')))}")


if __name__ == "__main__":
    main()