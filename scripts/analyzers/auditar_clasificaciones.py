"""Auditoria de la clasificacion de vehiculos.

Revisa de forma sistematica que ninguna categoria contenga vehiculos del tipo
equivocado. El detonante fue TOPMAQ: se dio por marca solo-electrica y 78 de sus
anuncios tenian "electrica" o vatios en el titulo, asi que quedaron 146
anuncios en Motores que no eran motores de combustion.

Uso:
    python3 scripts/analyzers/auditar_clasificaciones.py
    python3 scripts/analyzers/auditar_clasificaciones.py --detalle 50

Lee data/processed/vehiculos_clasificados.csv, que genera generate_report.py.
Salida: informe en pantalla y, con --json, en analysis/auditoria_clasificaciones.json.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLASIFICADOS = ROOT / "data" / "processed" / "vehiculos_clasificados.csv"
SALIDA_JSON = ROOT / "analysis" / "auditoria_clasificaciones.json"

# Senales electricas: deben coincidir con SENALES_ELECTRICAS de
# generate_report.py. Se repiten aqui a proposito, para que la auditoria sea
# independiente del modulo que audita.
SENAL_ELECTRICA = re.compile(
    r"\bMOTICO\b|\bBICIMOTOS?\b|\bBISIMOTO\b|\bMOTORINA\b|\bELECTRICA\b"
    r"|\bELECTRICAS?\b|\bELECTRICOS?\b|\bELECTRICAMENTE\b"
    r"|\d+\s*V\b|\d+\s*W(?:ATTS?)?\b|\d+\s*AH\b"
    r"|\bLITIO\b|\bLITHI\b|\bLIFEPO\w*\b|\bBLUETOOTH\b"
)
SENAL_COMBUSTION = re.compile(
    r"\d{2,3}\s*CC\b|\bCOMBUSTI\w*\b|\bGASOLINA\b|\b4\s*TIEMPOS?\b|\b4T\b|\bKM\s*/\s*L\b"
)
SENAL_PATINETE = re.compile(r"\bPATINET[OA]S?\b")
SENAL_MOTORINA = re.compile(r"\bMOTICO\b|\bBICIMOTOS?\b|\bBISIMOTO\b|\bMOTORINA\b")
SENAL_PIEZA = re.compile(r"\bBATERI\w*\b|\bCARGADOR\w*\b")
# Pieza como sujeto principal del anuncio: la palabra abre el titulo.
SENAL_PIEZA_ENCABEZA = re.compile(
    r"^[^A-Za-z0-9]{0,6}(BATERI\w*|CARGADOR\w*)", re.IGNORECASE
)
SENAL_VEHICULO = re.compile(
    r"\bMOTOS?\b|\bBICIMOTOS?\b|\bMOTICOS?\b|\bMOTORINAS?\b"
    r"|\bBICICLETAS?\b|\bPATINET[OA]S?\b"
)

# Marcas que el analisis da por solo-electricas. Si alguna tiene anuncios de
# combustion, es una marca mixta y deberia salirse de la lista.
MARCAS_DECLARADAS_ELECTRICAS = {
    "VEDCA", "CHALLENGER", "MAF", "YOAZAKY", "JMD", "BUCATTI", "KVITOVA",
    "PANDA", "INFINITY", "TRANK", "VORTAX", "JINGHAN", "TST", "DEEPOWER",
    "G29",
}


def normalizar(texto) -> str:
    """Pasa a ASCII sin tildes ni letras matematicas, en mayusculas."""
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return ""
    descompuesto = unicodedata.normalize("NFKD", str(texto))
    limpio = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return limpio.upper()


def cargar() -> pd.DataFrame:
    if not CLASIFICADOS.exists():
        raise SystemExit(
            f"No existe {CLASIFICADOS}. Ejecuta antes generate_report.py."
        )
    df = pd.read_csv(CLASIFICADOS)
    df["_norm"] = df["title"].map(normalizar)
    df["_electrica"] = df["_norm"].map(lambda t: bool(SENAL_ELECTRICA.search(t)))
    df["_combustion"] = df["_norm"].map(lambda t: bool(SENAL_COMBUSTION.search(t)))
    df["_patinete"] = df["_norm"].map(lambda t: bool(SENAL_PATINETE.search(t)))
    df["_motorina"] = df["_norm"].map(lambda t: bool(SENAL_MOTORINA.search(t)))
    df["_pieza"] = df["_norm"].map(lambda t: bool(SENAL_PIEZA_ENCABEZA.search(t)))
    df["_vehiculo"] = df["_norm"].map(lambda t: bool(SENAL_VEHICULO.search(t)))
    return df


def seccion(titulo: str, df: pd.DataFrame) -> dict:
    print()
    print("=" * 78)
    print(titulo)
    print("=" * 78)
    return {"titulo": titulo, "total": int(len(df)), "casos": []}


def auditar(df: pd.DataFrame, detalle: int) -> dict:
    informe: dict = {}

    # --- 1. Marcas declaradas solo-electricas que tienen anuncios de combustion
    sub1 = df[df.marca_detectada.isin(MARCAS_DECLARADAS_ELECTRICAS) & df._combustion]
    marca = seccion("1. Marcas declaradas solo-electricas CON anuncios de combustion", sub1)
    marca["casos"] = int(len(sub1))
    if sub1.empty:
        marca["titulo"] += "  -> ninguna, la lista es correcta"
        print("  Ninguna. Las marcas de la lista son solo-electricas.")
    else:
        print("  Estas marcas se declararon solo-electricas pero tienen anuncios")
        print("  de combustion. La regla por marca los deja en Motores, pero la")
        print("  lista ya no describe bien la realidad:")
        for m, n in sub1.marca_detectada.value_counts().items():
            print(f"      {str(m):14s} {n} anuncios de combustion")
            marca["casos_por_marca"] = marca.get("casos_por_marca", [])
            marca["casos_por_marca"].append({"marca": str(m), "n": int(n)})
            fila = sub1[sub1.marca_detectada == m]
            for _, r in fila.head(detalle).iterrows():
                print(f"          {str(r.title)[:70]!r}")
    informe["marcas_mixtas_declaradas"] = marca

    # --- 2. Fugas: electricos dentro de Motores
    sub = df[df._electrica & (df.categoria == "Motores")]
    fuga = seccion("2. Anuncios ELECTRICOS que quedaron en Motores", sub)
    fuga["casos"] = int(len(sub))
    if sub.empty:
        fuga["titulo"] += "  -> ninguno"
        print("  Ninguno. No hay vehiculo electrico clasificado como motor.")
    else:
        for _, r in sub.head(detalle).iterrows():
            print(f"  {str(r.title)[:74]!r}")
    informe["fugas_electricas_en_motores"] = fuga

    # --- 3. Fugas: combustion dentro de Electricos
    sub2 = df[df._combustion & ~df._electrica & (df.categoria == "Eléctricos")]
    fuga2 = seccion("3. Anuncios de COMBUSTION que quedaron en Electricos", sub2)
    fuga2["casos"] = int(len(sub2))
    if sub2.empty:
        fuga2["titulo"] += "  -> ninguno"
        print("  Ninguno.")
    else:
        for _, r in sub2.head(detalle).iterrows():
            print(f"  {str(r.title)[:74]!r}")
    informe["fugas_combustion_en_electricos"] = fuga2

    # --- 4. Marcas mixtas reales por conteo de senales
    sub4 = df[df._electrica & df._combustion]
    mezcla = seccion("4. Marcas con las dos senales en el mismo anuncio", sub4)
    if sub4.empty:
        mezcla["titulo"] += "  -> ninguno"
        print("  Ninguno.")
    else:
        print("  Anuncios que declaran ambas (quedan como electricos por prioridad):")
        por_marca = sub4.marca_detectada.value_counts()
        for m, n in por_marca.head(15).items():
            print(f"      {str(m):14s} {n}")
            mezcla["casos"].append({"marca": str(m), "n": int(n)})
    informe["anuncios_ambos_senales"] = mezcla

    # --- 5. Marcas reales mixtas: mismo modelo electrico y de combustion
    sub5 = df[df.marca_detectada.notna() & df._combustion & ~df._electrica]
    reales = seccion(
        "5. Marcas que tienen a la vez una gama electrica y otra de combustion", sub5
    )
    if sub5.empty:
        reales["titulo"] += "  -> ninguna"
        print("  Ninguna marca tiene anuncios inequivocamente de combustion.")
    else:
        # Veredicto por marca: electrica, combustion o mixta. Se cuenta cada
        # marca por separado en los tres buckets y solo es "mixta" si aparece en
        # los dos lados. Esto es exactamente el fallo que se busco con TOPMAQ.
        con_marca = df[df.marca_detectada.notna()]
        solo_comb = (
            con_marca[con_marca._combustion & ~con_marca._electrica]
            .marca_detectada.value_counts()
        )
        solo_elec = (
            con_marca[con_marca._electrica & ~con_marca._combustion]
            .marca_detectada.value_counts()
        )
        electrica_por_defecto = (
            con_marca[con_marca._electrica & con_marca._combustion]
            .marca_detectada.value_counts()
        )
        mixta: list[tuple[str, int, int]] = []
        for marca, n_comb in solo_comb.items():
            n_elec = int(solo_elec.get(marca, 0))
            if n_elec and n_comb >= 3 and n_elec >= 3:
                mixta.append((marca, int(n_comb), n_elec))
        print("  Marcas con las DOS gamas (electrica y de combustion):")
        if not mixta:
            print("      ninguna")
        for marca, n_comb, n_elec in sorted(mixta, key=lambda x: -(x[1] + x[2])):
            print(
                f"      {marca:14s} {n_elec:4d} electricos  "
                f"{n_comb:4d} combustion   (mixta)"
            )
            reales["casos"].append(
                {"marca": marca, "combustion": n_comb, "electricos": n_elec}
            )
        print()
        print("  Solo combustion (correcto si siguen en Motores):")
        for marca, n in solo_comb.head(12).items():
            print(f"      {marca:14s} {n}")
        print()
        print(
            f"  Anuncios electricos con senal mixta de combustion: "
            f"{int(electrica_por_defecto.sum())} "
            f"(se clasifican como electricos por prioridad)"
        )
    informe["marcas_con_gama_combustion"] = reales

    # --- 6. Anuncios sin senal de ningun tipo, por categoria
    sub6 = df[~df._electrica & ~df._combustion & ~df._vehiculo]
    sin = seccion("6. Anuncios SIN ninguna senal de tipo (se techo por la fuente)", sub6)
    sin["casos"] = int(len(sub6))
    print(f"  Total: {len(sub6)} de {len(df)} ({len(sub6) / len(df) * 100:.1f}%)")
    if len(sub6):
        print("  Distribucion por categoria:")
        for cat, n in sub6.categoria.value_counts().items():
            print(f"      {str(cat):22s} {n}")
        sin["por_categoria"] = {
            str(k): int(v) for k, v in sub6.categoria.value_counts().items()
        }
    informe["sin_senal_de_tipo"] = sin

    # --- 7. Anuncios sin titulo
    sub7 = df[df.title.isna()]
    vacios = seccion("7. Anuncios sin titulo", sub7)
    vacios["casos"] = int(len(sub7))
    print(f"  Total: {len(sub7)} ({len(sub7) / len(df) * 100:.1f}%)")
    print("  Distribucion por categoria:")
    for cat, n in sub7.categoria.value_counts().items():
        print(f"      {str(cat):22s} {n}")
    vacios["por_categoria"] = {
        str(k): int(v) for k, v in sub7.categoria.value_counts().items()
    }
    informe["sin_titulo"] = vacios

    # --- 8. Patinetes mal absorbidos
    sub8 = df[df._patinete & (df.categoria == "Eléctricos")]
    pat = seccion("8. Patinetes que se absorbieron en Electricos", sub8)
    pat["casos"] = int(len(sub8))
    if sub8.empty:
        pat["titulo"] += "  -> ninguno"
        print("  Ninguno.")
    else:
        sin_motorina = sub8[~sub8._motorina]
        print(f"  Total: {len(sub8)}; sin senal de motorina: {len(sin_motorina)}")
        for _, r in sin_motorina.head(detalle).iterrows():
            print(f"      {str(r.title)[:74]!r}")
    informe["patinetes_absorbidos"] = pat

    # --- 9. Piezas contadas como vehiculo
    sub9 = df[
        df._pieza
        & ~df._vehiculo
        & df.categoria.isin(["Motores", "Eléctricos", "Bicicletas"])
    ]
    pieza = seccion("9. Anuncios de PIEZA (bateria/cargador) que quedaron como vehiculo", sub9)
    pieza["casos"] = int(len(sub9))
    if sub9.empty:
        pieza["titulo"] += "  -> ninguno"
        print("  Ninguno.")
    else:
        for _, r in sub9.head(detalle).iterrows():
            print(f"      {str(r.title)[:74]!r}")
    informe["piezas_como_vehiculo"] = pieza

    return informe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detalle", type=int, default=20, help="casos a listar")
    parser.add_argument("--json", action="store_true", help="volcar a JSON")
    args = parser.parse_args()

    df = cargar()
    print(f"Dataset: {CLASIFICADOS.relative_to(ROOT)}  ({len(df)} anuncios)")
    print("Categorias:", dict(df.categoria.value_counts()))

    informe = auditar(df, args.detalle)

    print()
    print("=" * 78)
    print("RESUMEN")
    print("=" * 78)
    # En la seccion 1 no todos los casos son errores: si el anuncio de
    # combustion acabo bien en Motores, la regla por marca lo capturaste y no
    # hay problema. Solo cuentan los que se quedaron en Eléctricos.
    sub1 = df[df.marca_detectada.isin(MARCAS_DECLARADAS_ELECTRICAS) & df._combustion]
    mal_ubicados = int((sub1.categoria != "Motores").sum())
    bien_ubicados = int(len(sub1)) - mal_ubicados

    graves = [
        ("Marcas solo-electricas mal clasificadas", mal_ubicados),
        ("Electricos que quedaron en Motores", informe["fugas_electricas_en_motores"]["casos"]),
        ("Combustion que quedaron en Electricos", informe["fugas_combustion_en_electricos"]["casos"]),
        ("Piezas contadas como vehiculo", informe["piezas_como_vehiculo"]["casos"]),
    ]
    total_graves = 0
    for nombre, n in graves:
        total_graves += int(n)
        marca_estado = "OK" if int(n) == 0 else "FALLA"
        print(f"  [{marca_estado}] {nombre:44s} {n}")
    print()
    print("  Excepciones mixtas capturadas correctamente por la regla:")
    print(f"    {len(sub1)} anuncios de combustion de marcas mixtas, de los que")
    print(f"    {bien_ubicados} quedaron en Motores y {mal_ubicados} mal.")
    print(f"\n  Total de problemas graves: {total_graves}")

    if args.json:
        SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
        serializable = json.loads(json.dumps(informe, default=str))
        serializable["generado"] = pd.Timestamp.now().isoformat()
        serializable["anuncios"] = int(len(df))
        SALIDA_JSON.write_text(
            json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n  [ok] {SALIDA_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()