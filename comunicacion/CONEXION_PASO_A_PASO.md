# Conexión y programación: de 0 a campaña funcionando

Guía operativa para conectar el sitio, medir y programar la campaña de 10 días. Está pensada para ejecutarse en **2 horas el día 0** y luego 25–30 minutos al día.

**Regla:** no pasar de fase sin completar la verificación. Cada fase tiene una “definición de terminado”.

---

## Mapa de cuentas

| Cuenta | Para qué | Coste | Tiempo |
| --- | --- | --- | ---: |
| GitHub (ya la tienes) | Publicar el sitio | 0 | 10 min |
| GoatCounter | Medir visitas y acciones | 0 | 15 min |
| Google Search Console | Saber qué se busca | 0 | 10 min |
| Telegram | Canal propio y cola programada | 0 | 30 min |
| Facebook Page + Meta Business Suite | Página y programación | 0 | 20 min |
| Instagram profesional | Descubrimiento visual | 0 | 10 min |
| TikTok | Reels | 0 | 5 min |
| LinkedIn | Credibilidad y prensa | 0 | 5 min |
| WhatsApp Business | Difusión y estados | 0 | 5 min |
| Google Calendar | Importar el plan | 0 | 5 min |
| Google Sheets | Panel de seguimiento | 0 | 5 min |

**Total:** ~2 horas. No necesitas tarjeta, dominio ni servidor.

---

## Fase 0 — Preparación (10 min)

- [ ] Abre el repositorio en el navegador y comprueba que `docs/index.html` existe.
- [ ] Ten a mano el teléfono con la sesión de Facebook, Telegram y WhatsApp.
- [ ] Descarga `docs/assets/checklist.pdf` y las 3 tarjetas a la galería del teléfono.
- [ ] Ten abierto `COPY_10_DIAS.md` para copiar textos.
- [ ] Comprueba la hora del teléfono: zona **America/Havana**.

**Terminado cuando:** tienes el PDF, las tarjetas y los textos a mano.

---

## Fase 1 — Publicar el sitio (10 min)

1. Entra al repositorio: `github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba`.
2. **Settings** (arriba) → menú lateral **Pages**.
3. En **Build and deployment → Source**, elige **Deploy from a branch**.
4. En **Branch**, elige **main** y carpeta **/docs**. Pulsa **Save**.
5. Espera 1–3 minutos. Recarga la página de Pages: aparecerá la URL.
6. Abre: `https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/`
7. Si aparece **Enforce HTTPS**, actívalo.

**Verificación (hazla en el teléfono, no en la computadora):**

- [ ] La portada abre y se ve el titular del 45,5%.
- [ ] El botón “Resumen de 3 minutos” abre.
- [ ] En `/precios.html`, escribe `1600`: aparece mediana, rango y percentil.
- [ ] El checklist PDF se descarga desde “Descargar el checklist”.
- [ ] La página `/prensa.html` abre.
- [ ] Una URL inventada muestra la página 404.

**Si falla:**

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| 404 en todo | Repo privado o carpeta mal elegida | Repo público; branch `main`, carpeta `/docs` |
| 404 solo en el inicio | `index.html` no está en `docs/` | Verifica el archivo en GitHub |
| Sin estilos | Ruta de `assets/` mal | Los enlaces deben ser relativos (`assets/style.css`) |
| Sigue 404 tras 10 min | Build falló | Settings → Pages → “View builds” y revisa el error |
| Imágenes no cargan | Nombre o mayúsculas | Los nombres deben coincidir exactamente |

**Terminado cuando:** la portada, la calculadora y el PDF funcionan en el teléfono.

---

## Fase 2 — Medir (15 min)

### 2.1 Crear GoatCounter

1. Entra a `https://www.goatcounter.com/` → **Sign up**.
2. Elige un código corto: por ejemplo `mercadodosruedas`. Ese código será tu subdominio.
3. Confirma el correo.
4. En **Settings**, copia tu código (sin `.goatcounter.com`).

### 2.2 Conectarlo (una sola línea)

1. En GitHub, abre `docs/assets/config.js`.
2. Pulsa el lápiz (**Edit**).
3. Cambia:
   ```js
   window.SITE_CONFIG = { goatcounter: "" };
   ```
   por:
   ```js
   window.SITE_CONFIG = { goatcounter: "mercadodosruedas" };
   ```
   (usa tu código real).
4. **Commit changes** en `main`.
5. Espera 1–2 minutos a que Pages reconstruya y visita el sitio.

### 2.3 Verificar

- [ ] En el código fuente de la página aparece `gc.zgo.at/count.js`.
- [ ] En el panel de GoatCounter aparece tu visita (“Paths”).
- [ ] Al usar la calculadora, aparece el evento `calc-use`.
- [ ] Al pulsar el checklist, aparece `download-checklist`.
- [ ] Al compartir, aparece `share-click`.
- [ ] Los clics en botones aparecen como `cta:...`.

**Nota:** GoatCounter no usa cookies y es gratuito para uso no comercial. Si tu bloqueador lo bloquea, pruébalo en una ventana limpia.

### 2.4 Google Search Console (opcional hoy, hazlo antes del día 3)

1. `search.google.com/search-console` → **Añadir propiedad** → **Prefijo de URL**.
2. Pega la URL del sitio.
3. Verifica con **archivo HTML**: descarga el archivo, súbelo a `docs/` en GitHub (Add file → Upload files) y confirma.
4. Envía `sitemap.xml` en **Sitemaps**.

**Terminado cuando:** una visita tuya aparece en GoatCounter y los eventos se registran.

---

## Fase 3 — Crear los canales (40 min)

### 3.1 Telegram (15 min)

1. Telegram → menú → **Nuevo canal**.
2. Nombre: **Mercado de dos ruedas · La Habana**.
3. Descripción: “Datos del mercado de motos, bicis y patinetes. Estudio de 4.979 anuncios. Sin publicidad.”
4. Tipo: **Público**; usuario: por ejemplo `mercadodosruedas` (si está libre).
5. Foto: sube `docs/og.png`.
6. Publica y **fija** el mensaje de bienvenida (T1 de `COPY_10_DIAS.md`).

### 3.2 Facebook Page (10 min)

1. `facebook.com/pages/create` → nombre **El mercado invisible · La Habana**.
2. Categoría: **Educación** o **Sitio web de noticias**.
3. Bio: “Estudio de 4.979 anuncios del mercado de dos ruedas en La Habana. Datos abiertos y gratuito.”
4. Foto de perfil: `og.png`. Portada: `tarjeta-marca.png`.
5. Sitio web: la URL de Pages.
6. Publica el post de lanzamiento y fíjalo.

**Importante:** la página es la que se puede programar. Los **grupos no se pueden programar**; se publican a mano con el calendario.

### 3.3 Instagram (5 min)

1. Instala la app; crea cuenta o cambia a **profesional**.
2. Vincula la página de Facebook.
3. Bio: “El mercado de motos de La Habana en datos · 4.979 anuncios · Gratis” + enlace al sitio.
4. Sube las 3 tarjetas como primeras publicaciones.
5. Crea 3 historias destacadas: **Precios**, **Guía**, **Estudio**.

### 3.4 TikTok (5 min)

1. Crea la cuenta con el mismo nombre.
2. Bio con el enlace al sitio.
3. Sube el reel 1 cuando esté grabado.

### 3.5 LinkedIn (5 min)

- No necesitas página: publica desde tu perfil.
- Titular: “Lo que aprendí analizando 4.979 anuncios del mercado de motos de La Habana”.
- Enlace en el primer comentario.

### 3.6 WhatsApp Business (5 min)

1. Instala WhatsApp Business (gratis) y configura nombre y web.
2. Crea la lista de difusión **Dato semanal** solo con quienes den permiso.
3. Comprueba que puedes publicar estados con imagen y texto.

**Terminado cuando:** existen canal de Telegram, página de Facebook, Instagram y lista de difusión, y el enlace del sitio está en todas las bios.

---

## Fase 4 — Programar (60 min)

### 4.1 Telegram: 15 mensajes (25 min)

1. Abre el canal → botón de escribir.
2. Pega el mensaje T1 de `COPY_10_DIAS.md`.
3. En lugar de enviar, pulsa el **icono de reloj** o mantén pulsado el botón de enviar → **Programar mensaje**.
4. Elige fecha y hora. Repite con T2–T15.
5. Horarios sugeridos: **19:30** (lunes a sábado) y **11:00** (domingo).

**Verificación:** en el canal deben aparecer 15 mensajes con la etiqueta “programado”.

### 4.2 Facebook Page: posts programados (15 min)

1. `business.facebook.com` → **Planner** (o **Publicaciones programadas**).
2. **Crear publicación** → elige la página.
3. Pega el texto del día, añade la tarjeta, y en **Programar** elige fecha/hora (19:30).
4. Programa D1–D10 (10 publicaciones).
5. En el texto, evita el enlace; ponlo en el primer comentario al publicar.

**Verificación:** el Planner muestra 10 publicaciones en cola.

### 4.3 Instagram (10 min)

1. En Meta Business Suite → **Planner** → **Crear publicación** → elige Instagram.
2. Sube la tarjeta o el reel y programa.
3. Para historias: se publican a mano (recordatorio en el calendario).

### 4.4 LinkedIn (5 min)

1. Crea la publicación → icono de **reloj** → programa para el día 3 y el día 7.

### 4.5 TikTok (opcional, 5 min)

1. `tiktok.com/tiktokstudio` → **Subir** → programa si tu cuenta lo permite (hasta 10 días).
2. Si no aparece la opción, usa el calendario y publica a mano.

### 4.6 WhatsApp: sin programación nativa

No se puede programar sin API de pago. Solución:

- Crea **recordatorios** en el teléfono para los estados y la lista.
- Deja los textos y las imágenes listos en una nota o en la galería.
- 5 minutos al día: estado + reenvío a aliados.

### 4.7 Importar el plan al calendario (5 min)

1. Descarga `comunicacion/plan_10_dias.ics`.
2. Google Calendar → **Configuración** → **Importar y exportar** → selecciona el archivo → elige calendario → **Importar**.
3. Comprueba que el primer evento (D0, 09:00) cae a la hora correcta.

Cada evento trae recordatorio 10 minutos antes.

### 4.8 Panel de seguimiento (5 min)

1. Crea una hoja en Google Sheets.
2. **Archivo → Importar → Subir** `comunicacion/SEGUIMIENTO.csv`.
3. Rellénala cada noche con 5 números.

**Terminado cuando:** Telegram tiene 15 mensajes programados, Facebook 10, Instagram y LinkedIn tienen cola, y el calendario está importado.

---

## Fase 5 — Verificación final (10 min)

Hazlo en una ventana de incógnito y en el teléfono:

- [ ] La portada abre en menos de 3 segundos con datos móviles.
- [ ] El enlace compartido en WhatsApp muestra imagen y título (si no, espera o usa `?v=2`).
- [ ] El enlace en Telegram muestra la tarjeta social.
- [ ] La calculadora funciona sin JavaScript bloqueado.
- [ ] El PDF abre en el visor del teléfono.
- [ ] Los enlaces del pie llevan al repositorio y al informe.
- [ ] El 404 funciona.
- [ ] La URL empieza con `https://` y no hay aviso de seguridad.
- [ ] GoatCounter registra tu visita.
- [ ] El evento de calculadora y el de descarga aparecen.
- [ ] El calendario tiene los 33 eventos.
- [ ] Tienes 5 aliados confirmados y 3 permisos de administradores.

**Si algo falla, no lances.** Un enlace roto en el día 1 cuesta más que un día de retraso.

---

## Fase 6 — Día 1: lanzamiento hora por hora

| Hora | Acción | Canal |
| --- | --- | --- |
| 08:30 | Verificación final de la fase 5 | — |
| 09:00 | Publica el post de lanzamiento y fíjalo | Página de Facebook |
| 09:15 | Publica en 2 grupos (con permiso), enlace en primer comentario | Grupos |
| 10:00 | Estado de WhatsApp con `tarjeta-marca.png` | WhatsApp |
| 10:15 | Envía PDF + tarjeta a los 5 aliados | WhatsApp |
| 12:00 | Publica T1 y T2 | Telegram (programado) |
| 19:30 | Responde todos los comentarios | Todos |
| 21:00 | Anota 5 métricas en el panel | Sheets |

---

## Fase 7 — Operación diaria y semanal

### Rutina diaria (25 min)

| Bloque | Tiempo | Qué |
| --- | --- | ---: |
| Mañana | 5 min | Revisar métricas y comentarios nuevos |
| Tarde | 10 min | 2 publicaciones en grupos (según calendario) |
| Noche | 10 min | Responder todo y anotar 5 números |

### Rutina semanal (45 min)

1. Leer el panel: visitas, lectura, descargas, calculadora, compartidos.
2. Identificar la mejor y la peor pieza.
3. Decidir una cosa: repetir, cambiar gancho o cambiar canal.
4. Producir el lote de la semana siguiente (3–4 piezas).
5. Actualizar el CRM: quién respondió, quién autorizó, quién compartió.

### Reglas de decisión

| Señal | Acción |
| --- | --- |
| CTR < 2% | Cambiar el gancho, no el canal |
| Lectura < 45% | Revisar portada y peso |
| Descargas < 5% | Subir el CTA del checklist |
| Un grupo rinde 3× | Duplicar ahí y abandonar el resto |
| Comentarios sin responder > 5 | Pausar publicación y responder |
| Cansancio | Pausar 2 días: la cola programada sigue |

---

## Anexo A — Enlaces con UTM listos

Base: `https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba`

| Uso | Enlace |
| --- | --- |
| Post en grupos (D1) | `/?utm_source=facebook&utm_medium=community&utm_campaign=lanzamiento&utm_content=d1-grupos` |
| Muro (D1) | `/?utm_source=facebook&utm_medium=social&utm_campaign=lanzamiento&utm_content=d1-muro` |
| WhatsApp (D1) | `/?utm_source=whatsapp&utm_medium=social&utm_campaign=lanzamiento&utm_content=d1-wa` |
| Telegram (T1) | `/?utm_source=telegram&utm_medium=social&utm_campaign=lanzamiento&utm_content=t1` |
| Reel calculadora (D2) | `/precios.html?utm_source=instagram&utm_medium=social&utm_campaign=calculadora&utm_content=d2-reel` |
| Checklist (D3) | `/assets/checklist.pdf?utm_source=whatsapp&utm_medium=social&utm_campaign=guia&utm_content=d3-pdf` |
| LinkedIn (D3) | `/?utm_source=linkedin&utm_medium=social&utm_campaign=metodo&utm_content=d3-li` |
| Prensa (D4) | `/prensa.html?utm_source=prensa&utm_medium=referral&utm_campaign=prensa&utm_content=d4-pitch` |

**Regla:** un enlace sin UTM no enseña nada. Si no hay tiempo de etiquetarlo, no se publica.

---

## Anexo B — Solución de problemas

| Problema | Causa | Solución |
| --- | --- | --- |
| Pages da 404 | Repo privado, rama o carpeta mal | Público; `main`; `/docs`; esperar 3 min |
| El sitio carga sin CSS | Ruta absoluta o nombre distinto | Usar rutas relativas y respetar mayúsculas |
| GoatCounter no registra | Código mal escrito o bloqueador | Revisar `config.js`; probar en incógnito |
| Los eventos no aparecen | Script cargado después del clic | Recargar y repetir; verificar `count.js` |
| WhatsApp no muestra imagen | Caché del enlace | Añadir `?v=2` al final |
| Facebook no muestra imagen | Caché | Usar **Sharing Debugger** → “Scrape Again” |
| Telegram programa a otra hora | Zona horaria del teléfono | Ajustar a America/Havana |
| El post de grupo se borra | Sin permiso o spam | Pedir permiso al admin; bajar cadencia |
| El PDF no abre en el teléfono | Enlace mal copiado | Usar `assets/checklist.pdf` exacto |
| La calculadora no responde | JavaScript bloqueado | Probar otro navegador; las tablas siguen disponibles |

---

## Anexo C — Automatización (sin pagar)

| Tarea | Automatización gratuita |
| --- | --- |
| Publicar el sitio | GitHub Pages reconstruye al hacer commit |
| Publicar en Telegram | Programación nativa (15 mensajes) |
| Publicar en Facebook/Instagram | Meta Business Suite Planner |
| Publicar en LinkedIn | Programación nativa |
| Recordatorios de grupos/WhatsApp | Google Calendar (`.ics`) |
| Medición | GoatCounter |
| Panel | Google Sheets |

**No uses bots de auto-publicación en grupos.** Violan las reglas, queman la cuenta y destruyen la credibilidad. La parte que no se puede automatizar son 20 minutos de conversación al día; el resto ya está programado.

---

## Anexo D — Definición de terminado

| Fase | Terminado cuando |
| --- | --- |
| 1. Sitio | Portada, calculadora y PDF funcionan en el teléfono |
| 2. Medición | Una visita y un evento aparecen en GoatCounter |
| 3. Canales | Telegram, Facebook, Instagram y WhatsApp existen con enlace |
| 4. Programación | 15 mensajes en Telegram, 10 posts en Facebook, calendario importado |
| 5. Verificación | Los 12 puntos de la fase 5 están marcados |
| 6. Lanzamiento | Post publicado en página + 2 grupos + estado + 5 aliados |
| 7. Operación | Panel con 5 números al final del día 1 |
