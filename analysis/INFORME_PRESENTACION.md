# Informe de presentación

Guion para presentar el estudio. Está pensado para **5 a 7 minutos**.

Hay dos versiones del mismo material:

| Versión | Archivo | Cuándo usarla |
|---|---|---|
| Diapositivas | `presentation/index.html` | Presentación con proyector |
| Guion | este archivo | Ensayar, o si se proyecta sin HTML |

Las cifras del guion salen de `analysis/evidencia_vendedores.json`, que genera
`scripts/analyzers/generar_evidencia_vendedor.py`. Si un día cambian los datos,
se regenera y las diapositivas y este guion se actualizan juntos.

---

## Antes de empezar

El deck es un solo archivo y **funciona sin internet**. Eso importa: si el
proyector falla o no hay WiFi, la presentación abre igual.

```
xdg-open presentation/index.html
```

Controles: `←` `→` para navegar, `f` pantalla completa, `o` índice de
diapositivas, `?` ayuda. Las notas del orador están en el propio HTML: se ven
en el código, en `aside.notario`.

---

## Guion

### 1. Portada

> Este trabajo es un estudio de datos reales del mercado de motos, eléctricas,
> bicicletas y patinetes en La Habana. Analicé {{TOTAL_VEHICULOS}} anuncios de
> cuatro fuentes públicas. La conclusión no es sobre el mercado: es sobre cómo
> se vende en él.

---

### 2. El punto de partida

> Primero, el volumen: {{TOTAL_VEHICULOS}} anuncios únicos,
> {{PCT_CON_PRECIO}}% con precio, {{CON_UBICACION}}% que dicen dónde están y
> {{PCT_WHATSAPP}}% con WhatsApp.

> Dos precisiones antes de seguir, porque son importantes y están en todos los
> números: **más publicadas no significa más vendidas**, y los precios son los
> que declaró cada vendedor, no un avalúo.

**No omitir la segunda frase.** Es lo que sostiene la credibilidad de todo lo
que viene después.

---

### 3. La tesis

> Aquí está el problema. Un comprador busca "moto eléctrica 100 km de
> autonomía". Un vendedor publica "se vende moto". Ninguno de los dos encuentra
> al otro.
>
> Ese costo no lo paga el comprador. Lo paga el vendedor, y no por falta de
> demanda: por falta de información en el anuncio.

---

### 4. Prueba 1 — Invisibilidad

> El {{PCT_SIN_MARCA}}% de los vehículos reales no dice su marca en el título.
> {{SIN_MARCA}} de {{VEHICULOS_REALES}}.
>
> Quien busca "Topmaq" nunca ve esos anuncios. No es que estén mal
> posicionados: es que no existen para quien busca por marca.
>
> En bicicletas el problema es mucho peor: {{PCT_SIN_MARCA_BICI}}% sin marca.

**Pausa y pregunta a la audiencia:** ¿cuántos han buscado un producto por
marca y no encontraron lo que buscaban? Ahí está el {{PCT_SIN_MARCA}}%.

---

### 5. Prueba 2 — El título

> El título es lo único que ve el comprador antes de decidir si te escribe. Y
> {{PCT_SIN_CIFRA}}% de los títulos no contienen un solo número.
>
> Sin cc, sin voltaje, sin kilómetros, sin autonomía. No se puede filtrar, no
> se puede comparar y no se puede decidir.
>
> Y hay {{TITULOS_VACIOS}} anuncios directamente sin título
> ({{PCT_TITULOS_VACIOS}}%). Ese anuncio existe en la plataforma, pero no
> dice absolutamente nada.

---

### 6. Prueba 3 — La geografía

> El {{SIN_UBICACION}}% no dice en qué municipio está. Quien busca en su barrio
> no puede verlos.
>
> Y hay una concentración fuerte: {{MUNI_TOP}} concentra el
> {{MUNI_TOP_PCT}}% de los anuncios con ubicación y precio.
>
> Esto no significa que fuera de ahí no haya mercado. Significa que fuera de
> ahí no hay publicación. Para un vendedor es la lectura más accionable de
> toda la presentación.

---

### 7. Prueba 4 — El precio por marca

> ¿Estás cobrando de más o de menos? Sin referencia, no hay forma de saberlo.
>
> Esta es la mediana de precio publicado por marca, de las ocho con más
> anuncios. BUCATTI está en 2.600 USD, TOPMAQ en 2.150 y CHALLENGER en 850.
>
> Marcas como SUZUKI, con mediana de 3.200 USD, quedan fuera de esta tabla
> porque tienen menos anuncios publicados.
>
> **Un vendedor que no conoce la mediana de su categoría negocia a ciegas.**
> Y esa asimetría beneficia a quien sí la conoce.

---

### 8. El precio por zona

> Y esto es lo que más sorprende: la zona pesa más que la marca.
>
> Cerro con mediana de 700 USD, Habana del Este con 1.920 USD. Dos veces y
> media, en la misma ciudad.
>
> Y si no publicas tu zona, no apareces en ninguno de estos comparativos.

---

### 9. El canal

> {{PCT_WHATSAPP}}% publican WhatsApp. El correo electrónico aparece en
> **{{CORREOS}} anuncio de todo el mercado**.
>
> Si hoy estás vendiendo por correo, estás dejando fuera a casi todos los
> compradores. Publicar ambos es el mínimo aceptable.

---

### 10. La oportunidad

> Ahora la parte positiva. Si el problema es la información, la oportunidad
> está donde hay hueco:
>
> - **Patinetes eléctricos**: {{PATINETES}} anuncios en todo el mercado.
>   Prácticamente sin competencia.
> - **Repuestos**: el archivo de piezas tiene {{PIEZAS}} registros, pero cerca
>   de la mitad ni siquiera son piezas. El mercado real está desatendido.
> - **Bicicletas**: {{BICICLETAS}} anuncios y {{PCT_SIN_MARCA_BICI}}% sin
>   marca. La categoría más pequeña y la peor documentada.

---

### 11. El mismo vehículo, dos anuncios

> Todo lo anterior se resume en un ejemplo. Lee los dos:
>
> **"MOTO SE VENDE"** — sin marca, sin cifra, sin zona. No aparece en ninguna
> búsqueda.
>
> **"Moto eléctrica AVA 100 km de autonomía, seminueva, Centro Habana"** —
> marca, categoría, cifra clave, estado y zona. Aparece en las cinco
> búsquedas que importan.
>
> Es el mismo vehículo. La diferencia entre los dos anuncios no es el
> producto: es la información.

---

### 12. La práctica

> Diez cosas que se pueden cambiar mañana:
>
> Marca, una cifra clave, el municipio, WhatsApp, horario de respuesta, fotos
> reales, estado declarado, revisar la mediana de tu marca antes de fijar
> precio, publicar en varias fuentes, y borrar los duplicados y vacíos.
>
> Si alguien solo puede hacer una cosa hoy: **escribir la marca en el título**.
> Es el cambio de costo cero con más efecto.

---

### 13. Los límites

> Ahora lo que este estudio **no** puede decir, y creo que es lo más importante
> que decir:
>
> - No observa ventas. Solo anuncios. **Más publicadas no es más vendidas.**
> - Los precios son los que declaró el vendedor, no un avalúo.
> - No hay campo de condición, así que no puedo distinguir nuevo de usado.
> - No hay fecha por anuncio, así que no puedo afirmar tendencias.
>
> Y el problema de origen: {{SIN_TITULO}} anuncios sin título
> ({{PCT_SIN_TITULO}}%) y {{SIN_SENAL}} sin ninguna señal de tipo
> ({{PCT_SIN_SENAL}}%). Para analizar este mercado tuve que escribir reglas de
> clasificación y auditarlas. **Ningún vendedor puede esperar que el mercado se
> ordene solo.**

**Decir esto antes de que lo pregunten es lo que hace creíble todo lo anterior.**

---

### 14. El método y el cierre

> Un detalle de cómo se hizo, porque creo que es lo que sostiene el trabajo:
> todo se reprodujo con scripts, con una taxonomía explícita y con nueve
> comprobaciones automáticas. El resultado de la auditoría es **cero problemas
> graves**. Ninguna cifra de esta presentación está escrita a mano.
>
> Para cerrar: el problema de este mercado no es la falta de compradores. Es la
> falta de información de los dos lados. Professionalizar un anuncio no es un
> favor al comprador — es la forma más directa de vender más.

---

## Preguntas que suelen salir

**¿Esto es una predicción de ventas?**
No. No hay datos de ventas en ninguna fuente pública. Todo es análisis de
anuncios publicados.

**¿Entonces los precios no sirven?**
Sirven como referencia de posición relativa, no como avalúo. La utilidad está en
compararte con tu propia categoría, no en el número absoluto.

**¿Por qué 4.979 y no 5.391?**
La diferencia son duplicados: 412 anuncios repetidos en la misma fuente. Se
eliminan por URL.

**¿Por qué hay una categoría "Otros"?**
Porque {{SIN_SENAL}} anuncios no dan ninguna señal de tipo y {{SIN_TITULO}} no
tienen título. Meterlos en una categoría inventada sería mentir. "Otros" dice
la verdad: no sabemos qué son.

**¿Se puede seguir ampliando el estudio?**
Sí. El pipeline ya está: se scrapea, se clasifica y se audita. Sumar una fuente
más es agregar el scraper, no rehacer el análisis.

---

## Material de respaldo

Si alguien pide ver el detalle, existe:

| Qué | Dónde |
|---|---|
| Figuras completas | `analysis/figures/` |
| Clasificación de cada anuncio | `data/processed/vehiculos_clasificados.csv` |
| Cifras de esta presentación | `analysis/evidencia_vendedores.json` |
| Análisis completo | `analysis/INFORME_ANALISIS.md` |
| Auditoría automática | `scripts/analyzers/auditar_clasificaciones.py` |
| Bitácora del proyecto | `JOURNEY.md` |