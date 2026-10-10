# Journey del proyecto

Estudio de mercado de motos, bicicletas, patinetes y repuestos en Cuba, a partir
de publicaciones de clasificados.

Este documento registra **qué se hizo y por qué**, en orden cronológico. No es un
log de commits: es la bitácora de decisiones, hallazgos y correcciones, porque
varias de las decisiones más importantes del estudio salieron de descubrir
problemas en los datos, no de escribir código.

---

## 2026-09-19 a 2026-09-24 — Recolección de datos

Se escribieron y ejecutaron los scrapers contra cuatro plataformas cubanas.

| Fuente | Qué se recogió |
| --- | --- |
| Revolico | Vehículos y repuestos |
| iTENCEL | Motos y repuestos |
| ElYerroMenu | Motos y bicicletas (dos catálogos) |
| Facebook | 10 grupos de compraventa |

Los datos crudos quedaron en `data/raw/` y las fechas de recolección están en el
campo `scraped_at` de cada registro (rango 2026-09-19 a 2026-09-24).

## 2026-10-02 — Primera publicación del repositorio

Commit `602bad1` con la estructura del proyecto, la documentación en español
(`README.md`, `docs/ARQUITECTURA.md`, `docs/GUIA_SCRAPING.md`), los scripts de
scraping y los datasets ya curados.

## 2026-10-04 — Inicio del análisis gráfico

Se creó `scripts/analyzers/generate_report.py` como generador único de figuras,
después de que los intentos anteriores en scripts sueltos fallaran por funciones
duplicadas y errores de ámbito. Todo el análisis se ejecuta con:

```
python3 scripts/analyzers/generate_report.py
```

> **Nota sobre el intérprete.** `/usr/bin/python3` no tiene matplotlib en esta
> máquina. El script se ha ejecutado con el entorno que sí lo trae:
> `/home/reynaldomesab/PDF/backend/.venv/bin/python3`. Si al reproducirlo falla
> con `ModuleNotFoundError: matplotlib`, es el intérprete, no el código.

### Hallazgo: el dataset estaba duplicado

El conteo inicial daba 5,787 vehículos, pero al deduplicar por `source_url` el
total real resultó ser **4,979**. Dos fuentes de duplicación:

- `vehicles_curated.json` **ya contenía** los 396 posts de Facebook, y el
  análisis los sumaba otra vez al concatenar `facebook_curated`.
- iTENCEL se había scrapeado cuatro veces con solapamiento (523 anuncios de
  repuestos eran 260 únicos).

La función `dedup()` quedó integrada y hoy se aplica a todo. Cualquier cifra de
este estudio que no pase por ella está inflada.

## 2026-10-05 — Taxonomía del estudio

Se definieron las categorías oficiales y se fusionaron las etiquetas crudas que
usan las plataformas:

- **Motores**: `Moto` + `Moto Combustión`
- **Motorinas**: `Moto Eléctrica` + `Mototrina`
- **Bicicletas eléctricas** y **Bicicletas** separadas
- **Patinetes eléctricos**
- **Otros**

Las plataformas no coinciden entre sí: iTENCEL y Facebook reportan casi todo como
"moto", mientras Revolico sí distingue. Eso hace que la composición por fuente
alone determine la taxonomía del estudio.

### Hallazgo: marcas mal clasificadas

Varias marcas que solo venden vehículos eléctricos estaban dentro de "Motores"
porque la fuente las archivó como moto de combustión. Se creó
`MARCA_SOLO_MOTORINAS` para reclasificarlas por marca en vez de confiar en la
etiqueta heredada.

## 2026-10-06 — Auditoría de marcas y modelos

El trabajo más largo del proyecto, y el que más corrigió resultados. Se hizo un
barrido sistemático en lugar de aceptar la lista de marcas inicial.

**Método.** Tres señales, en orden de fiabilidad:
1. El patrón `MARCA X` que escriben los vendedores.
2. La co-ocurrencia: si un token *siempre* aparece detrás de otro, es modelo.
3. Para lo dudoso, confirmación en internet.

**Hallazgos principales:**

- **MOTICO no es una marca**, es la palabra que nombra el tipo de vehículo. La
  marca va justo detrás: `MOTICO CHALLENGER CORLEONE`. Esto destapó ocho marcas
  que se estaban perdiendo.
- **CORLEONE, PRONTEZZA y ELEGANT son modelos de CHALLENGER**, no marcas. Se
  atribuyeron a su marca madre, junto con las erratas CHALENGER, CALLENGER y
  CHANLLENGER.
- **EAGLE era una marca falsa**: siempre aparece detrás de MIKAZUKI, MAF o
  MIDHA, y ENGLE es su errata. Estaba creando marcas que no existen.
- **DAKAR es modelo de HALCON**, confirmado en una ficha técnica publicada
  ("Marca: HALCON / Modelo: DAKAR PRO 150CC").
- Se recuperaron **16 marcas completas** que no estaban en la lista: JMD, AVA,
  BUCATTI, UNISON, TRECK, KVITOVA, JOMAR, KATZU, PANDA, RALI, VIKING y otras.
- **BEVOMECON y YESELF se dejaron fuera** a propósito: no se pudieron confirmar
  en internet y se prefirió no inventarlas.

**Atribución calculada, no codificada.** `calcular_padre_de_modelos()` deduce la
marca madre de cada modelo contando los títulos donde aparece junto a una marca
identificada. Solo agrupa si una marca alcanza el 90% y al menos 10 títulos. La
evidencia queda guardada en `resultados.json` para poder auditarla.

**Resultado:** la cobertura de marcas pasó de 22.6% a **50.9%**.

## 2026-10-06 — MOTICO y BICIMOTO como señales de tipo

Al revisar por qué marcas eléctricas seguían apareciendo en Motores, se descubrió
que **BICIMOTO** tampoco es una marca: aparece en 1,094 títulos y solo 2 mencionan
gasolina. Es la misma categoría de palabra que MOTICO.

Con esa señal, las categorías eléctricas pasaron a agrupar motorinas y
bicicletas eléctricas, porque **los datos no permiten separarlas**: el mismo
vendedor rotula indistintamente "bicimoto" y "motico" para el mismo producto.

## 2026-10-07 — Gráficos, corrección de cifras y reportes

### Gráfico 05: la mitad de los "repuestos" no son repuestos

Al preparar la comparativa vehículos/repuestos se descubrió que de los 260
anuncios del archivo de repuestos, **130 venden vehículos completos**, mal
archivados. Lo más grave: la categoría "Repuesto Patinete" tiene 13 de 15
anuncios que son scooters enteros.

Esto significa que el estudio, sin corregir, reportaría el doble de repuestos
reales. Por eso el gráfico circular tiene una nota al pie que lo declara.

### Reportes en texto

- `REPORTE_KM_POR_DOLAR.md`: **no publica la cifra.** Solo el 1.4% de los
  anuncios eléctricos tiene a la vez potencia, autonomía y precio, muy por debajo
  del 10% acordado. El reporte documenta la medición y explica por qué no se
  publica, en vez de dar un número frágil.
- `REPORTE_PRECIOS_TOP.md`: los 10 anuncios más caros, con los motivos legibles en
  su propio título. Salen refacciones entre los más caros, lo que confirma que
  el precio no siempre corresponde al vehículo.

### TOPMAQ: marca mixta

Se revisó si TOPMAQ tenía indicios de combustión, y sí: 16 de sus 351 anuncios son
de gasolina ("TOPMAQ TANK 200cc", "TOPMAQ GN 150", "TOPMAQ RAPTOR DE COMBUSTIÓN",
"TOPMAQ AVISPÓN 200cc"). Se la sacó de la lista de marcas solo-eléctricas y se
decide anuncio por anuncio con señales del título.

## 2026-10-07 — Paletas de color

Se sustituyó la paleta por defecto de seaborn por ocho paletas propias
(`oceano`, `desierto`, `selva`, `cyberpunk`, `vinos`, `pastel`, `vibrante`,
`minimal`), con la regla de que en los circulares la porción mayor recibe el
color saturado y la menor un tono apagado del mismo matiz.

## 2026-10-09 — Journey, registro de prompts y plugin

- Se creó este documento.
- Se creó `docs/PROMPTS_DEL_USUARIO.md`, con transcripción manual de los prompts
  de esta sesión y captura automática de los siguientes.
- Se instaló el plugin `~/.config/opencode/plugins/captura-prompts.ts`, que
  escucha el evento `message.updated` de OpenCode y añade cada prompt al archivo
  con su fecha.

---

## Estado actual

**Datos:** 4,979 vehículos únicos, 260 anuncios de repuestos (130 de ellos
vehículos mal archivados).

**Cobertura de información:** 93.9% de los anuncios tienen precio, pero solo
**50.9% tienen marca**. Esa asimetría es uno de los hallazgos centrales del
estudio: el precio está disponible, la identidad del producto casi no.

**Figuras:** 10 gráficos más 4 fichas de fuente en `analysis/figures/`.

**Preguntas descartadas por falta de datos:** medidas de neumáticos, condición
nuevo/usado, ventas confirmadas, coordenadas geográficas, densidad per cápita,
género del vendedor, potencia y autonomía, tendencia temporal.

---

## Lección principal del proyecto

Casi todos los errores graves del estudio no fueron errores de código, sino
**suposiciones sobre lo que significaba un campo**. "MOTICO" parecía una marca y
era el tipo de vehículo; "CORLEONE" parecía una marca y era un modelo; el archivo
de repuestos contenía vehículos. Cada vez que se aceptó un campo tal cual, el
resultado quedó sesgado.

La regla que mejor funcionó: **antes de graficar, contar**. La cobertura de
marcas pasó de 22.6% a 50.9% no porque el extractor mejorara, sino porque se
dejó de asumir y se empezó a medir.
