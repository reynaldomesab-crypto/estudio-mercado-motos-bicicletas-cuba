# Sprint de 10 días: audiencia significativa

**Objetivo:** pasar de 0 a una audiencia real y medible en 10 días (7 → 17 de noviembre de 2026), con coste 0 y la menor dependencia posible de ti.
**Estado:** sitio construido y listo para publicar. Falta activar Pages y distribuir.
**Tiempo requerido:** ~2 h el día 0 y 25–35 min/día después.
**Marco estratégico:** [`PROYECTO_COMUNICACION.md`](PROYECTO_COMUNICACION.md) · **Público:** [`PUBLICO_MAPA.md`](PUBLICO_MAPA.md) · **Conexión y programación:** [`CONEXION_PASO_A_PASO.md`](CONEXION_PASO_A_PASO.md).
**Documento hermano:** [`PLAN_DIVULGACION.md`](PLAN_DIVULGACION.md) (versión de 90 días, para después del sprint).

---

## 1. Qué significa "audiencia significativa" en 10 días

Con 0 presupuesto, una persona y distribución orgánica, la audiencia no se compra: se **concentra**. La meta no es 100.000 impresiones; es que **1.000 personas lean algo completo y 150 hagan algo útil**. Eso ya es significativo para un estudio local y, sobre todo, es la base que sigue creciendo después del día 10.

| Métrica | Mínimo | **Meta** | Ambicioso |
| --- | ---: | ---: | ---: |
| Personas alcanzadas (impresiones estimadas) | 8.000 | **15.000** | 30.000 |
| Visitas únicas al sitio | 500 | **900** | 1.800 |
| Lectura ≥60 s | 45% | **60%** | 68% |
| Descargas del checklist | 100 | **200** | 400 |
| Usos de la calculadora | 60 | **150** | 300 |
| Suscriptores de Telegram | 30 | **70** | 150 |
| Compartidos explícitos | 15 | **35** | 70 |
| Menciones o comunidades externas | 1 | **2** | 4 |

**Regla de honestidad:** no se promete viralidad. Se promete **10–30 veces más alcance que la situación actual** (0 estrellas, 0 sitio, 0 medición) con un sistema que no se apaga al día 10.

---

## 2. La lógica del sprint

En 10 días no hay tiempo para construir una serie de contenido. Hay tiempo para tres cosas:

1. **Un aterrizaje que no rebote** (ya está construido).
2. **Un activo que la gente reenvíe** (checklist PDF + tarjetas + calculadora).
3. **Distribución concentrada** en los 5–8 lugares donde ya está el mercado.

Todo lo demás (SEO, newsletter, comunidad, DOI) es para después. Si intentas hacer todo, no haces nada.

---

## 3. Lo que ya está construido

Sitio estático en `docs/`, sin servidor, sin cookies, sin dependencias externas:

| Página | Función | Peso |
| --- | --- | ---: |
| `index.html` | Portada anti-rebote: promesa, 3 datos, dos caminos (vendo/compro) | ~10 KB |
| `resumen.html` | El estudio en 3 minutos, con gráficos SVG | ~15 KB |
| `guia.html` | 10 cambios + tablas de precios por marca y zona | ~13 KB |
| `precios.html` | Calculadora: mediana, rango p10–p90 y percentil de tu precio | ~13 KB |
| `datos.html` | Dataset, campos, condiciones y cómo citar | ~7 KB |
| `metodo.html` | Cómo se hizo, 5 errores corregidos, límites y privacidad | ~8 KB |
| `assets/checklist.pdf` | Checklist de 2 páginas para reenviar | 19 KB |
| `assets/tarjeta-*.png` | 3 tarjetas 1080×1350 para WhatsApp/Instagram | ~50 KB c/u |
| `og.png` | Tarjeta social 1200×630 para que el enlace no se vea vacío | 40 KB |

**Total de texto del sitio: 104 KB.** Carga en segundos con datos móviles. La calculadora compara contra 2.892 anuncios eléctricos, 1.124 de combustión, 487 bicicletas, 12 municipios y 20+ marcas, siempre con muestra mínima.

Todo se regenera con `python3 comunicacion/build_site.py`.

---

## 4. Arquitectura de independencia

"Independiente" aquí significa: **no depende de que tú publiques todos los días ni de una plataforma**.

| Capa | Qué la hace independiente |
| --- | --- |
| **Sitio estático** | GitHub Pages sirve archivos; no hay servidor, base de datos ni mantenimiento. Si no lo tocas, sigue funcionando. |
| **Activos que viajan solos** | El PDF, las tarjetas y la calculadora se reenvían sin ti. Cada reenvío trae gente al sitio. |
| **Cola de contenido** | Telegram permite **programar mensajes** nativos (gratis). Escribes 15 y el canal publica solo durante 10 días. |
| **Contenido perenne** | Las páginas responden búsquedas reales ("cuánto cuesta una moto eléctrica en La Habana"): siguen trayendo visitas meses después. |
| **Repositorio + DOI** | GitHub y Zenodo dan permanencia y cita académica sin costo. |

**Rutina mínima después del día 10:** 10 minutos al día para responder comentarios y 1 hora al mes para actualizar el dato. Nada más.

---

## 5. Los tres pasos que solo puedes hacer tú

Yo no tengo acceso a tus cuentas. Estos tres pasos desbloquean todo y tardan menos de una hora:

### Paso 1 — Activar GitHub Pages (2 minutos)

1. Repositorio → **Settings** → **Pages**.
2. Source: **Deploy from a branch** → Branch: **main** → Folder: **/docs** → **Save**.
3. En 1–2 minutos el sitio queda en:
   `https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/`

Comprueba que abre la portada. Si no, revisa que `docs/index.html` exista en `main`.

### Paso 2 — Crear el canal de Telegram y programar (30 minutos)

1. Crea un canal público: **"Mercado de dos ruedas · La Habana"**.
2. Copia los 15 mensajes de `COPY_10_DIAS.md` y **programa** cada uno (clip → "Programar mensaje"). Telegram publica solo.
3. Fija el mensaje de bienvenida con el enlace al sitio y al checklist.

### Paso 3 — Abrir tres puertas (15 minutos)

1. Escribe a **3 administradores** de grupos de compraventa pidiendo permiso (plantilla en `PIEZAS_LISTAS.md`, pieza 9).
2. Elige **5 personas aliadas** (vendedores, taller, estudiante) y envíales el PDF + la tarjeta para que lo reenvíen.
3. Publica el **post de lanzamiento** (pieza 1) en tu muro y en tu estado de WhatsApp.

---

## 6. Calendario día por día

Horarios de La Habana. La franja 19:30–21:30 es la de mayor actividad en grupos.

| Día | Fecha | Qué se publica | Dónde | Tiempo |
| --- | --- | --- | --- | ---: |
| **D0** | Sáb 7 nov | Activar Pages; crear canal; programar 15 mensajes; pedir 3 permisos; enviar kit a 5 aliados | — | 120 min |
| **D1** | Dom 8 nov | **Lanzamiento** (post 1) + estado de WhatsApp con tarjeta-marca | Muro + 2 grupos + WhatsApp | 35 min |
| **D2** | Lun 9 nov | Calculadora + reel "¿está caro?" | 2 grupos + Instagram/TikTok | 30 min |
| **D3** | Mar 10 nov | Checklist PDF + difusión a aliados | WhatsApp + 2 grupos + Telegram | 30 min |
| **D4** | Mié 11 nov | Zonas (2,7×) + pitch a 5 periodistas/blogueros | 2 grupos + correo | 35 min |
| **D5** | Jue 12 nov | **Revisión**: mejor y peor mensaje; doblar el mejor | — | 20 min |
| **D6** | Vie 13 nov | Antes/después (reel) + mensaje a 10 profesores | 2 grupos + universidad | 30 min |
| **D7** | Sáb 14 nov | "Detrás del dato" (5 errores) + Q&A en Telegram | LinkedIn + Telegram | 30 min |
| **D8** | Dom 15 nov | Bicicletas (87,1%) + patinetes (64) | 2 grupos + Instagram | 30 min |
| **D9** | Lun 16 nov | FAQ + empujón final: "comparte si te sirvió" | Todos los canales | 25 min |
| **D10** | Mar 17 nov | Resultados + qué sigue + gracias | Muro + Telegram + GitHub | 30 min |

**Regla de cadencia:** máximo 1 publicación por grupo cada 5 días. Se rota entre grupos para no saturar. Nunca el mismo texto en todos.

**Regla de valor:** el dato completo va en el post; el enlace va en el primer comentario o al final, nunca como único contenido.

---

## 7. Qué publicar cada día (resumen)

| Día | Gancho | Dato | Acción |
| --- | --- | --- | --- |
| D1 | "El problema no es el precio" | 45,5% sin marca | Leer resumen |
| D2 | "¿Está caro o está bien?" | Medianas 2.000 / 1.600 / 160 | Usar calculadora |
| D3 | "10 cambios que no cuestan nada" | Checklist | Descargar PDF |
| D4 | "La misma ciudad, 2,7× de diferencia" | Cerro 700 / Habana del Este 1.920 | Ver zona |
| D5 | — | Revisión de métricas | Ajustar |
| D6 | "El mismo vehículo, dos anuncios" | Antes/después | Descargar plantilla |
| D7 | "El error estaba en mi pipeline" | 5.787 → 4.979; 606 títulos | Leer método |
| D8 | "87 de cada 100 bicicletas no dicen su marca" | 87,1% | Ver huecos |
| D9 | "Las 5 preguntas más frecuentes" | FAQ | Compartir |
| D10 | "90 días de datos en 10" | Resultados | Seguir el canal |

Los textos completos, listos para copiar, están en `COPY_10_DIAS.md`.

---

## 8. Medición diaria (5 minutos)

Instrumentación: **GoatCounter** (gratis, sin cookies, 3 KB). Crear cuenta, pegar el script en las 6 páginas antes del día 1.

| Día | Visitas | Lectura | Checklist | Calculadora | Compartidos | Decisión |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| D1 | | | | | | |
| D2 | | | | | | |
| D3 | | | | | | |
| D4 | | | | | | |
| D5 | | | | | | |
| D6 | | | | | | |
| D7 | | | | | | |
| D8 | | | | | | |
| D9 | | | | | | |
| D10 | | | | | | |

**Reglas de decisión (día 5):**

- CTR < 2% → cambia el gancho, no el canal.
- Lectura < 45% → el problema es la portada o el peso (revisar).
- Descargas < 5% de visitas → mueve el CTA del checklist arriba.
- Un grupo rinde 3× más que otro → duplica ahí, abandona el resto.
- Comentarios sin responder > 5 → pausa publicación hasta responder.

---

## 9. Riesgos y respuestas

| Riesgo | Señal | Respuesta |
| --- | --- | --- |
| Rechazo en grupos | "No es lugar para esto" | Agradecer, no insistir, pedir permiso al admin antes del siguiente |
| Penalización por enlace | Alcance bajo en un grupo | Texto completo en el post y enlace en comentario |
| Acusación de spam | Varios reportes | Bajar a 1 post/semana por grupo y aportar solo valor |
| Crítica metodológica | "Los precios no son ventas" | Responder con los límites y el método; nunca discutir |
| Privacidad | "Publicaste mi anuncio" | Explicar anonimización y ofrecer retirada en 48 h |
| Desgaste | Menos de 6 h/semana | Pausar 2 días; el contenido programado sigue |

**Línea roja que no se cruza:** no escribir por WhatsApp ni llamar a los teléfonos del dataset. Se usan solo agregados.

---

## 10. Qué queda funcionando después del día 10

1. **Sitio** con 6 páginas indexables y calculadora permanente.
2. **Checklist PDF** circulando por WhatsApp.
3. **Canal de Telegram** con cola de mensajes.
4. **Dataset y método** citables para estudiantes y prensa.
5. **Medición** para saber qué repetir.

El día 10 no se termina el proyecto: se termina la campaña de lanzamiento. A partir de ahí, el plan de 90 días (`PLAN_DIVULGACION.md`) toma el relevo con una rutina de 6–8 h/semana.
