# Informe Técnico — Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba

**Proyecto:** Estudio de Mercado de Motos, Bicicletas, Patinetes y Repuestos en Cuba  
**Autor:** Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba  
**Fecha:** 28 de octubre de 2026  
**Estado:** Completo, versión 1.0  
**Repositorio:** `https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba`

---

## Resumen ejecutivo

Este documento es el **informe técnico completo** del proyecto de análisis de mercado de vehículos de dos ruedas y repuestos en La Habana, Cuba. Describe todo el trabajo realizado, desde la recolección de datos hasta la publicación de los productos finales, y explica **el porqué de cada decisión**: qué se hizo, por qué se hizo así, qué errores se descubrieron y cómo se corrigieron.

El proyecto parte de **4.979 anuncios únicos** recopilados de cuatro fuentes públicas cubanas (Revolico, iTENCEL, ElYerroMenu y Facebook) y produce tres entregas principales:

1. **`analysis/INFORME_FINAL.html`** — informe académico autocontenido (estilo paper F1) con 12 figuras, tablas y referencias.
2. **`analysis/GUIA_VENDEDOR.md`** — guía de buenas prácticas para vendedores del sector.
3. **`presentation/index.html`** — presentación de 14 diapositivas, funciona sin internet.

Además, se incluyen un pipeline de scraping reproducible, un script de anonimización de datos personales y una auditoría automática de clasificaciones.

---

## 1. Contexto y motivación del estudio

### 1.1 Por qué este estudio

En La Habana no existe un registro unificado ni un estándar mínimo de publicación para los anuncios de vehículos de dos ruedas. Un comprador no puede filtrar por autonomía, un vendedor no sabe si su precio es competitivo y un anuncio sin marca, zona o cifra difícilmente puede compararse con otros. El objetivo del estudio es **diagnosticar la calidad de la información publicada** en los anuncios y proponer un estándar mínimo de publicación que cualquier vendedor pueda aplicar.

**Decisión clave:** el estudio es **educativo y no lucrativo**. No incluye secciones comerciales, no tiene precios de servicio, y mantiene un tono impersonal.

### 1.2 Alcance y límites declarados desde el inicio

El estudio no mide ventas reales, ni distingue nuevo/usado, ni captura tendencias temporales (no hay fecha por anuncio). Su alcance se limita a la **calidad de la información publicada**. Estas limitaciones se documentan explícitamente en el informe final y en la guía del vendedor para evitar que se interpreten las cifras como algo que no son.

---

## 2. Fase 1 — Recolección de datos (2026-09-19 a 2026-09-24)

### 2.1 Qué se hizo

Se escribieron y ejecutaron scrapers contra cuatro plataformas cubanas de clasificados:

| Fuente | Contenido recogido |
|--------|-------------------|
| **Revolico** | Vehículos y repuestos |
| **iTENCEL** | Motos y repuestos |
| **ElYerroMenu** | Motos y bicicletas (dos catálogos) |
| **Facebook** | 10 grupos de compraventa |

Los datos crudos quedaron en `data/raw/` con el campo `scraped_at` (rango 19–24 de septiembre de 2026).

### 2.2 Por qué se hizo así

- **Múltiples fuentes:** ninguna plataforma sola cubre el mercado. Revolico tiene volumen y teléfono obligatorio; iTENCEL tiene precio y marca; Facebook aporta volumen pero títulos vacíos; ElYerro tiene catálogo con nombre y precio.
- **Datos públicos únicamente:** se respeta la Ley 149/2022 de Protección de Datos Personales (Art. 17.e permite tratar datos de fuentes de acceso público sin consentimiento, siempre que no se vulneren los principios del Art. 10).
- **Rate limiting de 1,5 s entre requests, respeto a robots.txt y User-Agent realista:** se documenta en `docs/GUIA_SCRAPING.md`.

### 2.3 Resultado bruto

5.391 registros iniciales (vehículos), antes de la deduplicación.

---

## 3. Fase 2 — Limpieza, normalización y deduplicación (2026-10-02)

### 3.1 Qué se hizo

Se creó `scripts/analyzers/generate_report.py` como generador único de figuras, y se integró la **deduplicación por `source_url`**. Posteriormente se conectó `scripts/analyzers/normalizar_registros.py` para recuperar texto de campos alternativos.

### 3.2 Hallazgo crítico: el dataset estaba duplicado

El conteo inicial daba 5.787 vehículos, pero tras deduplicar por `source_url` el total real resultó ser **4.979**. Causas de duplicación:

- `vehicles_curated.json` ya contenía los 396 posts de Facebook, y el análisis los sumaba de nuevo al concatenar `facebook_curated`.
- iTENCEL se scrapeó cuatro veces con solapamiento (523 anuncios de repuestos eran 260 únicos).

**Por qué esto importa:** cualquier cifra que no pase por la deduplicación está inflada. La función `dedup()` se integró y se aplica a todo el pipeline.

### 3.3 Hallazgo metodológico mayor: Facebook guarda el cuerpo en `text`, no en `title`

Facebook no usa el campo `title` para el texto del anuncio; lo publica en `text` (cuerpo del post, mediana 304 caracteres). ElYerro guarda el nombre en `name`. Sin normalización, 606 anuncios quedaban sin texto y se reportaban erróneamente como "vendedores que no informan". **No era omisión del vendedor, sino un bug del pipeline.**

**Decisión:** se creó una capa de normalización que recupera `title` ← `text` / `name`, extrae teléfono (regex `5\d{7}\|7\d{7}\|wa\.me/(\d+)`), provincia y municipio del cuerpo del texto.

**Efecto de la normalización (verificado):**
- Títulos vacíos: 606 → 11 (0.2 %)
- Con provincia: 53.5 % → 91.2 %
- Con WhatsApp: 53.5 % → 59.9 %
- "Otros": 656 → 99
- Eléctricos: 2.825 → 3.006
- Motores: 1.036 → 1.272
- Bicicletas: 378 → 518
- Con marca: 2.596 → 2.720 (54.6 %)

### 3.4 Intérprete de Python obligatorio

`/usr/bin/python3` no tiene matplotlib en la máquina de trabajo. Se usa el entorno virtual que sí lo trae: `<intérprete del venv>/bin/python3`. Esto queda documentado en el JOURNEY para evitar `ModuleNotFoundError` al reproducir.

---

## 4. Fase 3 — Taxonomía y clasificación (2026-10-05)

### 4.1 Qué se hizo

Se definieron cinco categorías de vehículo:

- **Motores** (combustión)
- **Eléctricos**
- **Bicicletas**
- **Patinetes eléctricos**
- **Otros**

La asignación usa reglas jerárquicas sobre el título normalizado (sin acentos, Unicode a ASCII): primero señales de tipo (cilindrada, motor, gasolina, eléctrico, voltaje, vatios, patinete, bicimoto), luego marca, luego señales residuales.

### 4.2 Por qué se hizo así

Las plataformas no coinciden entre sí: iTENCEL y Facebook reportan casi todo como "moto", mientras Revolico sí distingue. Eso hace que la composición por fuente determine la taxonomía del estudio. Se necesitó unificarlas para poder comparar.

### 4.3 Hallazgo: marcas mal clasificadas

Varias marcas que solo venden vehículos eléctricos estaban dentro de "Motores" porque la fuente las archivó como moto de combustión. Se creó `MARCA_SOLO_MOTORINAS` para reclasificarlas por marca en vez de confiar en la etiqueta heredada.

---

## 5. Fase 4 — Atribución de marcas y auditoría (2026-10-06)

### 5.1 Qué se hizo

Se hizo un barrido sistemático de marcas en lugar de aceptar la lista inicial. Tres señales, en orden de fiabilidad:

1. El patrón `MARCA X` que escriben los vendedores.
2. La co-ocurrencia: si un token siempre aparece detrás de otro, es modelo.
3. Para lo dudoso, confirmación en internet.

Se creó `calcular_padre_de_modelos()` que deduce la marca madre de cada modelo contando los títulos donde aparece junto a una marca identificada. Solo agrupa si una marca alcanza el 90 % y al menos 10 títulos.

### 5.2 Principales hallazgos de la auditoría de marcas

| Hallazgo | Qué se descubrió | Por qué importa |
|----------|-----------------|-----------------|
| **MOTICO** | No es marca, es el tipo de vehículo | Destapó 8 marcas que se estaban perdiendo |
| **CORLEONE, PRONTEZZA, ELEGANT** | Modelos de CHALLENGER, no marcas | Se atribuyeron a su marca madre |
| **EAGLE** | Marca falsa, siempre detrás de MIKAZUKI/MAF/MIDHA | Se evitaron marcas inexistentes |
| **DAKAR** | Modelo de HALCON (confirmado en ficha técnica) | Reclasificado correctamente |
| **BEVOMECON, YESELF** | Dejados a propósito | No se pudieron confirmar en internet |

**Resultado:** la cobertura de marcas pasó del 22,6 % al **50,9 %**.

### 5.3 Por qué no se usaron otras fuentes

Se prefirió no inventar marcas que no se pudieran confirmar en internet. La atribución es calculada, no codificada a mano, y la evidencia queda en `resultados.json` para poder auditarla.

---

## 6. Fase 5 — Corrección de la clasificación por tipo (2026-10-09)

### 6.1 El error de fondo

Los patrones de clasificación se aplicaban sobre el **título crudo**. Eso rompía dos cosas:

1. **Los acentos:** el patrón buscaba `ELECTRICA` y el título traía `ELÉCTRICA`.
2. **Letras matemáticas Unicode:** muchos vendedores escriben con negrita tipográfica (`𝐁𝐈𝐂𝐈𝐌𝐎𝐓𝐎`). NFKD es lo único que pliega ese bloque a ASCII.

Además, la señal eléctrica **no incluía la palabra "ELÉCTRICA"**, que es la forma más común de escribirla.

### 6.2 Efecto TOPMAQ

De 146 anuncios de TOPMAQ en Motores, pasaron a 23. De esos 23, 18 tienen combustión explícita en el título y 5 son indecibles.

**Efecto global:** Motores pasó de 2.264 a 1.036 anuncios y Eléctricos de 2.514 a 2.852.

### 6.3 Otros dos errores

- **606 anuncios sin título** (12 % del dataset, todos de Facebook) quedaban clasificados como vehículos porque la plataforma los tenía en "Moto". Sin texto no hay evidencia, así que pasan a "Otros".
- **Seis anuncios de baterías de TOPMAQ** contaban como motos. Un anuncio que solo describe una pieza no es un vehículo.

### 6.4 Lo que enseñó esta corrección

Un solo anuncio mal clasificado no es el problema: es que **la señal que decidía la categoría era incompleta**, y eso afectaba a las 4.979 filas a la vez. La categoría "Motores" estaba mezclando motos de gasolina con bicimotos eléctricas porque la mitad de los títulos eléctricos no se reconocían.

**Decisión clave:** antes de graficar, contar. La cobertura de marcas pasó del 22,6 % al 50,9 % no porque el extractor mejorara, sino porque se dejó de asumir y se empezó a medir.

---

## 7. Fase 6 — Auditoría automática de clasificaciones (2026-10-09)

### 7.1 Qué se hizo

Se construyó `scripts/analyzers/auditar_clasificaciones.py` para revisar **todas** las clasificaciones, no una marca. Ejecuta **9 comprobaciones**:

1. Marcas declaradas solo-eléctricas que tienen anuncios de combustión.
2. Eléctricos clasificados en Motores.
3. Combustión clasificados en Eléctricos.
4. Marcas con ambas señales en el mismo anuncio.
5. Piezas contadas como vehículo.
6. Patinetes absorbidos en Eléctricos por el orden de las reglas.
7. Anuncios sin título.
8. Anuncios sin señal de tipo (categoría "Otros").
9. Baterías o cargadores clasificados como vehículo.

### 7.2 Lo que encontró

**Cuatro marcas declaradas solo-eléctricas tienen también gama de combustión:** YOAZAKY (19), JMD (3), TRANK (1), BUCATTI (1). Los 24 están correctamente en Motores porque la regla por marca excluye los anuncios que declaran combustión. Se dejan en la lista de solo-eléctricas a propósito, porque sus anuncios eléctricos se declaran poco y sacarlos de la lista los perdería.

**Diez marcas son genuinamente mixtas** (TOPMAQ, YOAZAKY, JMD, HALCON, MIKAZUKI, AVA, IZUKI, ITALY, TRECK, XMOX).

**Dos fugas destapadas:**
- Patinetes absorbidos en Eléctricos (29 anuncios). Causa: el orden de las reglas. Se movió la asignación de patinetes al final. Pasaron de 40 a 64.
- Piezas contadas como vehículos (3 anuncios de baterías "35Ah"). Ahora un anuncio que solo describe una pieza se excluye de la señal eléctrica.

**Resultado:** cero problemas graves. Un anuncio sin señal de tipo o sin título no se puede clasificar, y eso está registrado: 606 anuncios sin título (12,2 %) y 738 sin ninguna señal (14,8 %), concentrados en "Otros".

**Bug de la propia auditoría:** la sección 1 comparaba `len(casos) == 0` sobre una lista siempre vacía, así que reportaba "Ninguna" siempre. El primer análisis dio 24 problemas y el correcto da 0: los 24 son excepciones bien gestionadas, no errores.

---

## 8. Fase 7 — Gráficos y reportes (2026-10-07)

### 8.1 Qué se hizo

Se generaron 10 figuras más 4 fichas de fuente en `analysis/figures/`. Posteriormente se crearon 12 figuras para el informe académico en `analysis/figures_informe/`.

### 8.2 Hallazgos de los gráficos

**Gráfico 05: la mitad de los "repuestos" no son repuestos.** De los 260 anuncios del archivo de repuestos, 130 venden vehículos completos, mal archivados. La categoría "Repuesto Patinete" tiene 13 de 15 anuncios que son scooters enteros. El gráfico circular incluye una nota al pie declarándolo.

**Reporte KM por dólar:** no se publica la cifra. Solo el 1,4 % de los anuncios eléctricos tiene a la vez potencia, autonomía y precio, muy por debajo del 10 % acordado. El reporte documenta la medición y explica por qué no se publica, en vez de dar un número frágil.

**TOPMAQ: marca mixta.** Tiene indicios de combustión (16 de 351 anuncios son de gasolina). Se sacó de la lista de marcas solo-eléctricas y se decide anuncio por anuncio con señales del título.

### 8.3 Paletas de color

Se sustituyó la paleta por defecto de seaborn por ocho paletas propias (`oceano`, `desierto`, `selva`, `cyberpunk`, `vinos`, `pastel`, `vibrante`, `minimal`), con la regla de que en los circulares la porción mayor recibe el color saturado y la menor un tono apagado del mismo matiz.

---

## 9. Fase 8 — Anonimización y cumplimiento normativo (2026-10-16 a 2026-10-21)

### 9.1 Qué se hizo

Se creó `scripts/privacy/sanitizar_datos.py` que aplica una **lista blanca** de campos: se conservan únicamente categoría, marca, precio, provincia, municipio, título y texto, procedencia y marca de tiempo. Se descartan o seudonimizan nombres de perfil, identificadores de Facebook, identificadores de anuncio, teléfonos, enlaces e imágenes.

Los teléfonos y enlaces en el texto se sustituyen por `[contacto]` mediante regex. Los IDs se seudonimizan con hash SHA-256 y sal.

### 9.2 Por qué se hizo así (Ley 149/2022)

Los anuncios identifican a personas concretas (nombres de perfil, teléfonos, URLs de anuncio). Publicar el conjunto en un repositorio abierto convierte una observación sobre el mercado en un dato personal localizable.

**Marco legal aplicado:**
- **Art. 17.e:** los datos se obtienen de fuentes de acceso público, por lo que su obtención está permitida sin consentimiento expreso, siempre que no se vulnere ningún principio del Art. 10.
- **Art. 17.f:** antes de publicar, se disocian los datos (hash SHA-256) para que no puedan asociarse a una persona determinada.
- **Art. 10.a** Limitación de recogida: solo se conservan los campos necesarios para el análisis.
- **Art. 10.c** Especificación de fines: diagnóstico académico, sin uso comercial.
- **Art. 10.d** Limitación de uso: los datos se usan exclusivamente para el fin informado.
- **Art. 10.f** Seguridad: los archivos con datos identificativos no se versionan (están en `.gitignore`).
- **Arts. 20-23** Derechos del titular: acceso, rectificación, cancelación y oposición. Contacto: `estudio-mercado@proyecto.local`, plazo 10 días hábiles (Art. 29).
- **No se recopilan datos sensibles** (Art. 15): sexo, género, origen étnico, estado de salud, etc.

### 9.3 Resultado

Los datos con identificadores personales quedan en `data/` (fuera del repositorio por `.gitignore`). La versión pública en `data/publico/` es anónima y segura para versionar.

---

## 9. Fase 9 — Informe académico, guía y presentación (2026-10-17 en adelante)

### 9.1 Qué se hizo

Se crearon tres entregas finales:

| Entrega | Archivo | Contenido |
|---------|---------|-----------|
| Informe académico | `analysis/INFORME_FINAL.html` | Estilo paper F1 (Weissbock 2025): portada, abstract, TOC, 1 Introducción, 2 Materiales y Métodos, 3 Resultados, 4 Discusión y Conclusiones, Referencias. 12 figuras embebidas en base64, tablas con caption, estilo imprimible. |
| Guía para vendedores | `analysis/GUIA_VENDEDOR.md` | 8 secciones con buenas prácticas: marca, cifra, zona, WhatsApp, etc. Cifras regeneradas tras normalización. |
| Presentación | `presentation/index.html` | 14 diapositivas, autocontenida, funciona sin internet, notas del orador, teclas f/o/?. |

### 9.2 Estructura del informe (paper F1)

- **Portada** → **Abstract + Keywords** → **1. Introducción** (Contexto, Planteamiento, Alcance, Trabajo previo, Objetivo) → **2. Materiales y Métodos** (Enfoque analítico, Recolección y normalización, Clasificación y taxonomía, Auditoría automática, Sesgos del origen de los datos, Protección de datos personales) → **3. Resultados** (11 subsecciones con figuras y tablas numeradas) → **4. Discusión y Conclusiones** (Síntesis, Interpretación, Limitaciones, Trabajo futuro, Conclusión) → **Referencias**.

### 9.3 Por qué esta estructura

El paper F1 de Weissbock (2025) es un referente académico que combina rigor metodológico con visualizaciones claras. Se replica su estructura para dar al trabajo escolar la calidad y el atractivo visual que se busca, comunicando buenas prácticas a vendedores del mercado de motos/bicis en La Habana.

---

## 10. Hallazgos centrales del estudio

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Anuncios únicos analizados | 4.979 | Universo del estudio tras deduplicación |
| Vehículos reales clasificados | 4.860 | 97,6 % del total |
| Con precio declarado | 93,9 % | El precio está ampliamente disponible |
| Sin marca | 45,5 % | Casi la mitad no dice su marca |
| Sin cifra en el título | 43,3 % | No hay base para comparar |
| Con ubicación (tras normalización) | 91,2 % | Sin ella caía al 53,5 % |
| Con WhatsApp | 59,9 % | Canal dominante de contacto |
| Sin señal de tipo ("Otros") | 2,0 % | 99 anuncios no clasificables |
| Con cobertura de precios | 93,9 % | Los precios son declarados, no avalúos |

**Conclusión principal:** el principal punto de mejora del mercado no está en la cantidad de oferta, sino en la información que los propios anuncios publican. Un estándar mínimo (marca, cifra clave, municipio, WhatsApp) es el cambio de costo cero con mayor retorno para cualquier vendedor.

---

## 11. Limitaciones declaradas

1. **No se observan ventas, solo anuncios.** Publicar más no equivale a vender más.
2. **No hay campo de condición** (nuevo/usado): no es posible distinguirlo.
3. **No hay fecha por anuncio:** no se puede afirmar tendencia ni estacionalidad.
4. **La deduplicación es por URL:** un mismo vehículo publicado en dos sitios cuenta como dos registros.
5. **Los precios son declarados por el vendedor,** no constituyen un avalúo.
6. **Los datos de ubicación/contacto solo existen en Revolico** (100 %); en otras fuentes el campo no existe. Esta es una limitación de la fuente, no del vendedor.
7. **No hay campo de género del vendedor** ni se infiere.
8. **El estudio es una fotografía de cuatro jornadas** (19–24 de septiembre de 2026), no un promedio del periodo.

---

## 12. Trabajo futuro

1. Integrar fecha de publicación por anuncio para analizar rotación y estacionalidad.
2. Distinguir condición (nuevo/usado) mediante reglas sobre el título.
3. Construir un índice de rotación por marca y zona.
4. Automatizar la recolección periódica para dar seguimiento al estándar.
5. Medir el efecto real del estándar mínimo de publicación sobre las ventas.

---

## 13. Reproducibilidad

Todo el proceso es determinista y se regenera desde el código:

```
# 1. Anonimizar datos antes de publicar
python3 scripts/privacy/sanitizar_datos.py

# 2. Generar figuras del informe
/home/reynaldomesab/PDF/backend/.venv/bin/python3 scripts/analyzers/generar_figuras_informe.py

# 3. Generar informe final
/home/reynaldomesab/PDF/backend/.venv/bin/python3 scripts/build_informe.py

# 4. Generar presentación y guía
/home/reynaldomesab/PDF/backend/.venv/bin/python3 scripts/build_presentation.py
```

El informe final es autocontenido (figuras embebidas en base64), funciona sin internet y no tiene recursos externos.

---

## 14. Conclusión

Este proyecto entrega un diagnóstico cuantitativo de la información que falta en los anuncios de vehículos de dos ruedas en La Habana, una referencia de precios por marca, y un pipeline reproducible y auditable. El principal punto de mejora no está en la cantidad de oferta, sino en la información que los propios anuncios publican. Todas las decisiones metodológicas, los errores encontrados y sus correcciones quedan documentadas en este informe y en el JOURNEY del proyecto, para que el trabajo sea verificable y reproducible.
