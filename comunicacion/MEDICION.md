# Panel de medición y registro de decisiones

Documento de trabajo para ejecutar el plan. Se completa una fila por semana. Sin esto, "evitar rebotes" y "llegar a más gente" son impresiones, no resultados.

---

## 1. Qué se mide

### Métrica norte

**Personas que completan una acción útil:** descargar el checklist, usar la calculadora, compartir una tarjeta o asistir a una charla.

### Seis métricas de embudo

| # | Métrica | Definición | Instrumento |
| --- | --- | --- | --- |
| 1 | Visitas únicas | Sesiones distintas por día/dispositivo | GoatCounter |
| 2 | Lectura comprometida | ≥60 s en página y ≥50% de scroll | Evento `scroll50` + duración |
| 3 | Conversión a guía | Descarga o apertura del PDF / visitas a `/guia` | Evento `pdf_download` |
| 4 | Uso de calculadora | Cálculo completado / visitas a `/precios` | Evento `calc_use` |
| 5 | Compartidos | Clic en compartir + reenvíos con UTM | Evento `share_click` |
| 6 | Retorno | 2+ sesiones en 30 días | GoatCounter (visitantes recurrentes) |

### Métricas de apoyo

- CTR por pieza y por canal.
- Comentarios y preguntas respondidas (indicador de comunidad, no de vanidad).
- Suscriptores de Telegram.
- Stars, forks y citas (señal académica, no objetivo principal).
- Menciones externas.

### Lo que no se mide

- "Me gusta": no indica lectura ni acción.
- Impresiones sin clic: útiles solo para calcular CTR.
- Estrellas como objetivo: son consecuencia, no meta.

---

## 2. Instrumentación (30 minutos, coste 0)

1. Crear cuenta en **GoatCounter** (`https://[usuario].goatcounter.com`).
2. Insertar el script en la portada y en las páginas del sitio (3 KB, sin cookies).
3. Definir eventos personalizados:
   - `scroll50` — al llegar al 50% de la página.
   - `cta_primary` — clic en el CTA principal.
   - `pdf_download` — descarga del checklist.
   - `calc_use` — cálculo completado.
   - `share_click` — clic en compartir.
4. Registrar el sitio en **Google Search Console** (verificación por archivo HTML, sin costo).
5. Crear un **Google Form** de una sola pregunta para la encuesta de salida: "¿Encontraste lo que buscabas? Sí / No / ¿Qué faltó?".
6. Etiquetar todos los enlaces con UTM (ver §3).

**Alternativa si GoatCounter no está disponible:** Cloudflare Web Analytics (también gratuito y sin cookies). No usar dos analíticas a la vez: duplica y confunde.

---

## 3. Convención UTM

```
utm_source   = whatsapp | facebook | telegram | instagram | tiktok | youtube | linkedin | github | universidad | prensa
utm_medium   = social | community | referral | email | talk | search
utm_campaign = lanzamiento | serie-precio | serie-visibilidad | serie-huecos | serie-metodo | guia | calculadora | informe | comunidad
utm_content  = p01 … p36 (id de pieza)
```

**Ejemplos:**

```
[SITIO]/?utm_source=facebook&utm_medium=community&utm_campaign=serie-visibilidad&utm_content=p02
[SITIO]/guia?utm_source=whatsapp&utm_medium=social&utm_campaign=guia&utm_content=p10
[SITIO]/precios?utm_source=instagram&utm_medium=social&utm_campaign=calculadora&utm_content=p13
```

**Regla:** un enlace sin UTM es un enlace que no enseña nada. Si no hay tiempo de etiquetarlo, no se publica.

---

## 4. Línea base (antes de empezar)

| Indicador | Valor al 7 nov 2026 | Fuente |
| --- | --- | --- |
| Visitas al sitio | No existe sitio (Pages desactivado) | API GitHub |
| Lectura / rebote | Sin medición | — |
| Stars / forks / watchers | 0 / 0 / 0 | API GitHub |
| Topics | Ninguno | API GitHub |
| DOI | No | — |
| Menciones externas | 0 conocidas | — |

**Conclusión:** no hay línea base porque no hay instrumentación. La primera semana de datos será la referencia, no una comparación.

---

## 5. Panel semanal

Rellenar cada domingo. Una fila por semana.

| Semana | Fechas | Visitas | Lectura ≥60 s | Guía | Calculadora | Compartidos | Telegram | Mejor pieza | Peor pieza | Decisión |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| W01 | 16–22 nov | | | | | | | | | |
| W02 | 23–29 nov | | | | | | | | | |
| W03 | 30 nov–6 dic | | | | | | | | | |
| W04 | 7–13 dic | | | | | | | | | |
| W05 | 14–20 dic | | | | | | | | | |
| W06 | 21–27 dic | | | | | | | | | |
| W07 | 28 dic–3 ene | | | | | | | | | |
| W08 | 4–10 ene | | | | | | | | | |
| W09 | 11–17 ene | | | | | | | | | |
| W10 | 18–24 ene | | | | | | | | | |
| W11 | 25–31 ene | | | | | | | | | |
| W12 | 1–7 feb | | | | | | | | | |

**Umbrales de alerta:**

| Señal | Umbral | Acción |
| --- | --- | --- |
| Lectura comprometida | < 45% | Congelar distribución y arreglar portada |
| Conversión a guía | < 8% | Revisar CTA y peso del PDF |
| CTR de post | < 2% | Cambiar titular, no canal |
| Comentarios sin responder | > 5 | Pausar publicación hasta responder |
| Caída semanal de visitas | > 40% | Revisar dependencia de un solo canal |

---

## 6. Registro de decisiones

Una línea por semana. La decisión debe apoyarse en un número, no en una impresión.

| Fecha | Decisión | Evidencia | Resultado (30 días) |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

---

## 7. Registro de experimentos

| # | Hipótesis | Fechas | n por variante | Métrica | Resultado | Decisión |
| --- | --- | --- | ---: | --- | --- | --- |
| 1 | Pérdida > curiosidad | | | CTR | | |
| 2 | Antes/después > cifra sola | | | Clics | | |
| 3 | Video 30 s > carrusel | | | Lectura | | |
| 4 | Un CTA > dos CTA | | | Conversión | | |
| 5 | Enlace en comentario > enlace en post | | | CTR | | |
| 6 | Calculadora retiene más que guía | | | Retorno 7 d | | |

**Reglas:** mínimo 100 impresiones por variante y 48 h. Se documentan también los empates y los resultados nulos.

---

## 8. Cómo interpretar sin engañarse

1. **Confundidor de canal:** un post en un grupo grande tendrá más clics que uno en Telegram, aunque sea peor. Comparar dentro del mismo canal.
2. **Confundidor de tema:** las piezas de precio funcionan mejor que las de método. Eso no significa que el método no sirva: significa que atrae a menos gente y más cualificada.
3. **Muestras pequeñas:** con menos de 100 visitas por semana, las tasas se mueven por azar. Mirar tendencia de 3 semanas.
4. **Estacionalidad:** diciembre y enero cambian el consumo. No atribuir a la campaña lo que hace el calendario.
5. **Supervivencia:** no contar solo las piezas que funcionaron; llevar registro de todas las publicadas.

---

## 9. Informe de cierre (7 feb 2027)

Debe responder cinco preguntas, con datos:

1. ¿Cuántas personas llegaron y cuántas completaron una acción útil?
2. ¿Qué canal trajo lectores que **actúan**, no solo clics?
3. ¿Qué mensaje funcionó mejor: pérdida, utilidad o curiosidad?
4. ¿Qué se abandona y qué se escala?
5. ¿Qué cambió en el estudio a partir de lo aprendido?

El informe se publica, aunque los resultados sean mediocres. Es parte del compromiso de rigor.
