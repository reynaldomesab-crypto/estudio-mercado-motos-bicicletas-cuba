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
> `<intérprete del venv>`. Si al reproducirlo falla
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

## 2026-10-09 — Corrección de la clasificación por tipo de vehículo

La revisión de los anuncios de TOPMAQ en Motores destapó **tres errores de
clasificación que afectaban a todo el estudio**, no solo a esa marca.

### El error de fondo: los patrones se aplicaban sobre el título crudo

Las expresiones regulares se ejecutaban contra el texto tal cual venía. Eso
rompía dos cosas a la vez:

- **Los acentos.** El patrón buscaba `ELECTRICA` y el título traía `ELÉCTRICA`.
- **Las letras matemáticas Unicode.** Muchos vendedores escriben con negrita
  tipográfica: `𝐁𝐈𝐂𝐈𝐌𝐎𝐓𝐎`. NFKD es lo único que pliega ese bloque a ASCII.

Además, la señal eléctrica **no incluía la palabra "ELÉCTRICA"**, que es la
forma más común de escribirla. Solo buscaba MOTICO y BICIMOTO.

Efecto TOPMAQ en Motores: **146 → 23**.

### Otros dos errores

- **606 anuncios sin título** (12% del dataset, todos de Facebook) quedaban
  clasificados como vehículos porque la plataforma los tenía en "Moto". Sin
  texto no hay evidencia, así que pasan a "Otros".
- **Seis anuncios de baterías de TOPMAQ** contaban como motos. Un anuncio que
  solo describe una pieza no es un vehículo, así que también pasan a "Otros".

### Lo que quedó

De los 23 anuncios de TOPMAQ en Motores, **18 tienen combustión explícita en el
título** (TANK 200cc, GN 150, AVISPÓN 200cc, RAPTOR) y 5 son indecibles: dos
dicen solo "Topmaq" y tres dicen "MOTO TOPMAQ TANK", un modelo que TOPMAQ
vende en las dos gamas.

Efecto global: Motores pasó de 2,264 a 1,036 anuncios y Eléctricos de 2,514 a
2,852.

### Lo que la corrección enseña

Un solo anuncio mal clasificado no es el problema: es que **la señal que decidía
la categoría era incompleta**, y eso afectaba a las 4,979 filas a la vez. La
categoría "Motores" estaba mezclando motos de gasolina con bicimotos eléctricas
porque la mitad de los títulos eléctricos no se reconocían.

Por eso se añadió `data/processed/vehiculos_clasificados.csv`, que exporta la
clasificación registro a registro. Permite auditar sin releer el código, que es
justo lo que faltaba para detectar estos errores.

### Dos regresiones que hubo que corregir

Al arreglar lo anterior aparecieron dos errores nuevos, ambos detectados
revisando los resultados:

- "Patinete eléctrico" pasó a Eléctricos y esa categoría bajó de 47 a 13
  anuncios. Los patinetes son categoría propia, así que se protegieron: solo se
  reclasifican si el título dice MOTICO o BICIMOTO.
- La regla de "solo pieza" arrastraba fuera bicicletas eléctricas que describen
  su batería ("Bicicleta eléctrica marca ONEBOT, batería 48V"). Se acotó a que
  el anuncio **no nombre ningún vehículo**.

## 2026-10-09 — Auditoría de toda la clasificación

TOPMAQ resultó ser el síntoma de un fallo general, así que se construyó
`scripts/analyzers/auditar_clasificaciones.py` para revisar **todas** las
clasificaciones, no una marca. Se ejecuta así:

```
python3 scripts/analyzers/auditar_clasificaciones.py --json
```

Nueve comprobaciones: fugas en ambas direcciones, marcas mal declaradas,
marcas mixtas, anuncios sin señal, anuncios sin título, patinetes absorbidos y
piezas contadas como vehículo.

### Lo que encontró

**Cuatro marcas declaradas solo-eléctricas tienen también gama de combustión:**

| Marca | Anuncios de combustión |
| --- | ---: |
| YOAZAKY | 19 |
| JMD | 3 |
| TRANK | 1 |
| BUCATTI | 1 |

Los 24 están **correctamente en Motores**: la regla por marca excluye los
anuncios que declaran combustión. Se decide dejarlos en la lista de
solo-eléctricas a propósito, porque sus anuncios eléctricos se declaran poco y
sacarlos de la lista los perdería.

**Diez marcas son genuinamente mixtas**, con las dos gamas en volumen:

| Marca | Eléctricos | Combustión |
| --- | ---: | ---: |
| TOPMAQ | 304 | 16 |
| YOAZAKY | 116 | 19 |
| JMD | 110 | 3 |
| HALCON | 70 | 34 |
| MIKAZUKI | 65 | 7 |
| AVA | 44 | 36 |
| IZUKI | 47 | 12 |
| ITALY | 28 | 14 |
| TRECK | 3 | 29 |
| XMOX | 10 | 7 |

### Dos fugas que la auditoría destapó

- **Patinetes absorbidos en Eléctricos.** 29 anuncios de patinetes de CHALLENGER,
  MAF y JMD estaban en Eléctricos. La causa era el **orden de las reglas**: la
  asignación por marca se aplicaba después y pisaba la de patinetes. Se movió al
  final. Patinetes pasó de 40 a 64 anuncios.
- **Piezas contadas como vehículos.** Tres anuncios de "Baterías Topmaq
  72Vol 35Ah" acababan en Eléctricos porque el "35Ah" dispara la señal eléctrica.
  Ahora un anuncio que solo describe una pieza se excluye de la señal y va a
  Otros.

También se corrigió un bug de la propia auditoría: la sección 1 comparaba
`len(casos) == 0` sobre una lista que siempre estaba vacía, así que reportaba
"Ninguna" siempre. Por eso el primer análisis dio 24 problemas y el correcto da
0: los 24 son excepciones bien gestionadas, no errores.

### Resultado

Cero problemas graves. Un anuncio sin señal de tipo o sin título **no se puede
clasificar**, y eso está registrado: 606 anuncios sin título (12.2%) y 738 sin
ninguna señal (14.8%), concentrados en la categoría Otros.

---

---

## Estado actual

**Datos:** 4,979 vehículos únicos, 260 anuncios de repuestos (130 de ellos
vehículos mal archivados).

**Categorías:** Motores 1,036 · Eléctricos 2,825 · Bicicletas 378 ·
Patinetes eléctricos 64 · Otros 656. Los 656 "Otros" son sobre todo los 606
anuncios sin título y los que solo describen una pieza.

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
