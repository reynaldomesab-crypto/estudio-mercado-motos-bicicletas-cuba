# Guía de buenas prácticas para vendedores

Guía para quienes venden motos, eléctricas, bicicletas y patinetes en La Habana,
escrita a partir del análisis de **4.860 anuncios reales** de
Revolico, iTENCEL, ElYerroMenu y Facebook.

No es publicidad ni un curso. Es una lectura del mercado basada en datos, para
que sepas en qué estás parado y qué te está costando ventas.

**Si solo vas a hacer una cosa:** escribe la marca en el título.

---

## Cómo usar esta guía

| Si te interesa… | Ve a… |
|---|---|
| Que te encuentren | [1. Que tu anuncio exista](#1-que-tu-anuncio-exista) |
| Escribir mejor el título | [2. El título](#2-el-título) |
| Fijar el precio | [3. El precio](#3-el-precio) |
| Que te escriban | [4. El contacto](#4-el-contacto) |
| Saber quién te compite | [5. La competencia](#5-la-competencia) |
| Elegir qué vender | [6. Los huecos](#6-los-huecos) |
| Resumen accionable | [7. Checklist](#7-checklist-de-diez-puntos) |
| Saber qué no sabemos | [8. Los límites](#8-lo-que-este-estudio-no-puede-decir) |

Todas las cifras salen de `analysis/evidencia_vendedores.json`, que genera
`scripts/analyzers/generar_evidencia_vendedor.py`.

---

## 1. Que tu anuncio exista

Un anuncio no se vende por ser bueno. Se vende por ser encontrado. Y aquí el
problema es del vendedor, no del comprador.

### La marca

El **45.5%** de los vehículos reales —2.210 de
4.860— no dice su marca en el título.

Quien busca "Topmaq" no ve esos anuncios. No es que estén mal posicionados ni
que la plataforma los esconda: sencillamente no existen para una búsqueda por
marca.

| Categoría | Anuncios | Sin marca |
| --- | ---: | ---: |
| Motores | 1.272 | 47.9% |
| Eléctricos | 3.006 | 37.4% |
| **Bicicletas** | 518 | **87.1%** |
| Patinetes eléctricos | 64 | 39.1% |

En bicicletas el problema es casi total: 87.1% sin marca
(451 de 518). La categoría está documentada peor que
ninguna otra.

### La ubicación

Solo el **91.2%** de los anuncios declara su municipio: el
**8.8%** no dice dónde está el vehículo.

Un comprador que busca en su barrio no puede ver tu anuncio aunque lo tenga a
dos cuadras. Y la comparación de precios por zona, que es la más útil para
decidir, directamente no te incluye.

### Qué hacer

Escribir **marca + categoría + zona** en el título. Son tres palabras y
convierten un anuncio invisible en uno localizable.

---

## 2. El título

El título es lo único que el comprador ve antes de decidir si te escribe. Y es
donde el mercado más falla.

- **43.3%** de los títulos no tienen **ningún número**
  (2.155 anuncios).
- **11** anuncios están directamente **sin título**
  (0.2%).

Un título sin números no se puede filtrar ni comparar. Si no dice qué autonomía
tiene, el comprador tiene que preguntarlo, y cada pregunta es una venta que se pierde.

### Antes y después

```
MOTO SE VENDE
```

```
Moto eléctrica AVA 100 km de autonomía, seminueva, Centro Habana
```

El mismo vehículo. La diferencia entre los dos anuncios no es el producto: es
la información.

### Qué va en un título

En este orden, que es el que hace encontrable un anuncio:

1. **Marca** — sin ella no hay búsqueda por marca
2. **Categoría** — eléctrica, de motor, bicicleta, patinete
3. **Cifra clave** — lo que el comprador filtra: autonomía, cc, voltaje,
   kilómetros, vatios
4. **Estado** — nueva, seminueva, usada
5. **Zona** — el municipio

Un ejemplo por categoría:

| Categoría | Ejemplo de título |
| --- | --- |
| Motores | `Moto JOMAR 150cc nueva, Guanabacoa` |
| Eléctricos | `Eléctrica YOAZAKY 500W, 60 km de autonomía, seminueva, Víbora` |
| Bicicletas | `Bicicleta TRECK 26 pulgadas, alum alloy, Víbora` |
| Patinetes | `Patinete JMD 250W, 30 km, Centro Habana` |

---

## 3. El precio

Negociar sin conocer la mediana de tu categoría es negociar a ciegas. Y esa
asimetría siempre la pierde quien no la tiene.

La buena noticia: el **93.9%** de los anuncios sí publica precio.
El mercado no tiene un problema de transparencia de precios; tiene un problema
de comparabilidad. Faltan la marca, la zona y las cifras con las que comparar.

### Por marca

Mediana de precio publicado, de las ocho marcas con más anuncios:

| Marca | Anuncios | Mediana | Rango p10–p90 |
| --- | ---: | ---: | ---: |
<tr><td>TOPMAQ</td><td class='num'>387</td><td class='num'>2.150 USD</td><td class='num'>1.780–2.900</td></tr><tr><td>VEDCA</td><td class='num'>214</td><td class='num'>1.600 USD</td><td class='num'>1.250–2.500</td></tr><tr><td>YOAZAKY</td><td class='num'>203</td><td class='num'>2.250 USD</td><td class='num'>1.604–2.900</td></tr><tr><td>HALCON</td><td class='num'>148</td><td class='num'>1.800 USD</td><td class='num'>771–2.650</td></tr><tr><td>CHALLENGER</td><td class='num'>130</td><td class='num'>850 USD</td><td class='num'>750–1.403</td></tr><tr><td>JMD</td><td class='num'>115</td><td class='num'>1.600 USD</td><td class='num'>750–1.750</td></tr><tr><td>AVA</td><td class='num'>90</td><td class='num'>1.650 USD</td><td class='num'>948–2.550</td></tr><tr><td>BUCATTI</td><td class='num'>86</td><td class='num'>2.600 USD</td><td class='num'>900–3.175</td></tr>

La diferencia entre la mediana más alta y la más baja de esta lista es de **más
de tres veces**. Marcas como SUZUKI, con mediana de 3.200 USD, quedan fuera de
la tabla por tener menos anuncios publicados.

El rango p10–p90 importa más que la mediana: te dice **dónde puede caer tu
precio** sin salirte del mercado. Un TOPMAQ por 1.200 USD está por debajo del 10%
de su categoría, y eso se nota.

### Por zona

La zona pesa **más que la marca**. En los municipios con al menos 50 anuncios
publicados:

| Municipio | Anuncios | Mediana |
| --- | ---: | ---: |
<tr><td>Cerro</td><td class='num'>107</td><td class='num'>700 USD</td></tr><tr><td>Arroyo Naranjo</td><td class='num'>128</td><td class='num'>820 USD</td></tr><tr><td>Diez de Octubre</td><td class='num'>314</td><td class='num'>900 USD</td></tr><tr><td>Marianao</td><td class='num'>123</td><td class='num'>1.100 USD</td></tr><tr><td>Playa</td><td class='num'>422</td><td class='num'>1.450 USD</td></tr><tr><td>Guanabacoa</td><td class='num'>61</td><td class='num'>1.560 USD</td></tr><tr><td>Habana Vieja</td><td class='num'>107</td><td class='num'>1.620 USD</td></tr><tr><td>Habana del Este</td><td class='num'>69</td><td class='num'>1.920 USD</td></tr>

Cerro y Habana del Este están a **2.7 veces** de distancia en la misma ciudad.
Y si no publicas tu municipio, no apareces en ninguno de estos comparativos.

> **Estos precios son los que declaró cada vendedor, no un avalúo.** Úsalos
> como referencia de posición relativa, no como precio de venta.

---

## 4. El contacto

Un dato que define el estándar del sector:

- **59.9%** publican teléfono de WhatsApp (2.982 anuncios).
- **1 anuncio** en todo el mercado usa correo electrónico.

Es decir: **el correo electrónico prácticamente no existe en este mercado**. Si
hoy vendes por correo, estás dejando fuera a casi todos los compradores.

### Qué implica

- **WhatsApp es obligatorio.** No es un complemento, es el canal.
- Publicar **correo además de WhatsApp** es el estándar mínimo aceptable.
- Publica un número que **atienda en horario**, no solo uno que exista.

---

## 5. La competencia

Centro Habana concentra el **24.0%** de los anuncios que tienen
municipio y precio declarados (2.596 en total).

Eso se lee de dos maneras, y las dos importan:

**Para quien vende en el centro:** la competencia es alta y visible. Vas a
competir por título, por fotos y por precio.

**Para quien vende fuera:** hay muchos menos anuncios publicados. Menos competencia y
casi sin oferta. La lectura accionable de toda esta guía.

---

## 6. Los huecos

Si el problema del mercado es la falta de información, la oportunidad está
donde hay poca publicación.

| Segmento | Volumen | Lectura |
| --- | ---: | --- |
| **Patinetes eléctricos** | 64 anuncios | Prácticamente sin competencia en todo el mercado |
| **Bicicletas** | 518 anuncios | Categoría pequeña y la peor documentada (87.1% sin marca) |
| **Repuestos** | 523 registros en el archivo | Buena parte no son piezas, sino vehículos mal clasificados |
| **Zonas fuera de Centro Habana** | — | Menos competencia y casi sin oferta publicada |

El dato de repuestos merece una aclaración, porque es contraintuitivo: el
archivo de piezas tiene 523 registros, pero una parte grande son en
realidad vehículos mal clasificados como repuestos. **El mercado real de
repuestos es más pequeño de lo que parece y está desatendido.**

---

## 7. Checklist de diez puntos

En orden de impacto sobre las ventas:

1. **Escribe la marca en el título.** Costo cero, el mayor efecto.
2. **Añade una cifra clave**: autonomía, cc, voltaje o kilómetros.
3. **Declara el municipio** donde está el vehículo.
4. **Publica WhatsApp**, no solo teléfono fijo.
5. **Responde en horario**, no solo cuando puedas.
6. **Declara el estado**: nueva, seminueva, usada.
7. **Pide fotos reales** del vehículo, no de catálogo.
8. **Revisa la mediana de tu marca** antes de fijar el precio.
9. **Publica en varias fuentes**, no en una sola.
10. **Borra duplicados y vacíos**: ocupan lugar sin informar a nadie.

---

## 8. Lo que este estudio no puede decir

Esta sección es la más importante de la guía, porque un mercado sin datos
también produce conclusiones falsas con mucha seguridad.

- **No observa ventas.** Solo anuncios. **Más publicadas no significa más
  vendidas.**
- **Los precios son los que declaró el vendedor**, no un avalúo.
- **No hay campo de condición**, así que no se puede distinguir nuevo de usado.
- **No hay fecha por anuncio**, así que no se puede afirmar tendencia ni
  estacionalidad.
- **La deduplicación es por URL**: un vehículo publicado en dos sitios cuenta
  como dos.

Y el problema de origen, que explica por qué un estudio así cuesta trabajo:

- **11** anuncios sin título (0.2%)
- **99** anuncios sin ninguna señal de tipo (2.0%)

Clasificar este mercado exigió escribir reglas de clasificación y auditarlas
para que no hubiera errores. **Ningún vendedor puede esperar que el mercado se
ordene solo.**

---

## Conclusión

El problema de este mercado no es la falta de compradores. Es la falta de
información de los dos lados.

Professionalizar un anuncio no es un favor al comprador — es la forma más
directa de vender más.

---

## Si quieres ir al fondo

| Qué | Dónde |
| --- | --- |
| Presentación | `presentation/index.html` |
| Guion y preguntas frecuentes | `analysis/INFORME_PRESENTACION.md` |
| Cifras de esta guía | `analysis/evidencia_vendedores.json` |
| Análisis completo | `analysis/INFORME_ANALISIS.md` |
| Clasificación de cada anuncio | `data/processed/vehiculos_clasificados.csv` |
| Auditoría automática | `scripts/analyzers/auditar_clasificaciones.py` |