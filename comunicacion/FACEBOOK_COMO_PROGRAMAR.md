# Cómo programar publicaciones en Facebook (paso a paso)

Vale para la página **El mercado invisible · La Habana**. La herramienta gratuita es **Meta Business Suite**.

---

## 0. Lo que necesitas

1. Una **página** de Facebook (no un perfil personal).
2. Ser **administrador** de esa página.
3. **Meta Business Suite**: `business.facebook.com` (escritorio) o la app **Meta Business Suite** (teléfono).

**Regla importante:** se programan publicaciones de **páginas** e **Instagram profesional**. **Los grupos no se pueden programar**: se publican a mano.

---

## 1. Crear la página (si aún no existe)

1. `facebook.com/pages/create`.
2. Nombre: **El mercado invisible · La Habana**.
3. Categoría: **Educación**.
4. Descripción: “Estudio de 4.979 anuncios del mercado de dos ruedas en La Habana. Datos abiertos y gratuitos.”
5. Foto de perfil: `docs/og.png`. Portada: `docs/assets/tarjeta-marca.png`.
6. Sitio web: la URL del estudio.
7. **Publicar**.

---

## 2. Entrar a Business Suite y agregar la página

1. Abre `business.facebook.com` e inicia sesión con la cuenta que administra la página.
2. Si es la primera vez: **Crear cuenta** → ponle un nombre (por ejemplo, “Estudio Mercado Dos Ruedas”).
3. En **Configuración del negocio → Cuentas → Páginas → Agregar**, selecciona tu página.
4. Vuelve al inicio: arriba a la izquierda debe aparecer el selector de página con **El mercado invisible · La Habana**.

Si no ves la página, no la agregaste o no eres administrador.

---

## 3. Programar un post (escritorio)

1. En el menú izquierdo, abre **Planner** (icono de calendario).
2. Pulsa **Crear publicación**.
3. Arriba, confirma que está seleccionada tu **página**. Si aparece Instagram y no lo quieres, desmárcalo.
4. Pega el texto del bloque (por ejemplo, D1 de `FACEBOOK_10_POSTS.txt`).
5. Añade la imagen: **Añadir foto** → sube la tarjeta indicada.
6. Pega el enlace al final del texto. Facebook generará una vista previa; puedes dejarla o quitarla con la **×**.
7. No pulses “Publicar”. Pulsa la flecha junto a **Publicar** → **Programar**.
8. Elige **fecha y hora**.
9. Confirma con **Programar**.

El post aparece en el calendario de Planner con la etiqueta **Programado**.

### Ver la hora correcta

Business Suite usa la **zona horaria del negocio**, no siempre la del teléfono.

1. **Configuración del negocio → Información del negocio → Zona horaria**.
2. Pon **America/Havana**.
3. Después de programar, abre el post en Planner y comprueba que la hora sea la que querías.

---

## 4. Programar desde el teléfono

1. Instala la app **Meta Business Suite** (no la app normal de Facebook).
2. Inicia sesión y elige la página.
3. Abajo, toca **Publicaciones** o **Planner**.
4. **Crear publicación** → escribe/pega el texto → añade foto.
5. Toca **Programar** (a veces está en “Más opciones” o con el icono de reloj).
6. Elige fecha y hora → confirmar.

La app de Facebook normal **no** programa posts de página; usa Business Suite.

---

## 5. Ver, editar o eliminar programados

- **Escritorio:** Planner → pestaña **Programadas** (o el calendario). Haz clic en el post.
- **Teléfono:** Planner → lista de programados.
- Opciones: **Editar**, **Reprogramar**, **Eliminar**.

Si te equivocas de hora o de imagen, se corrige ahí sin borrar y volver a empezar.

---

## 6. Qué se puede programar y qué no

| Lugar | ¿Se programa? | Cómo |
| --- | --- | --- |
| Página de Facebook | **Sí** | Business Suite → Planner |
| Instagram profesional | **Sí** | Business Suite (cuenta vinculada) |
| Perfil personal | No | — |
| Grupos de Facebook | **No** | Manual, con permiso y calendario |
| WhatsApp | No (sin API de pago) | Recordatorios y envío manual |
| Telegram | Sí | Programación nativa del canal |

---

## 7. Prueba segura de 10 minutos

Antes de programar los 10 posts:

1. Crea un post de prueba: “Prueba de programación”.
2. Prográmalo **10 minutos adelante**.
3. Espera: debe publicarse solo.
4. Si funcionó, **elimínalo** y programa los 10 reales.

Así detectas errores de hora o de página sin arruinar el lanzamiento.

---

## 8. Errores comunes

| Problema | Causa | Solución |
| --- | --- | --- |
| No aparece “Programar” | Estás en el perfil personal, no en la página | Selecciona la página arriba |
| Se publicó de inmediato | Pulsaste “Publicar” | Borra y repite con la flecha → Programar |
| Hora equivocada | Zona horaria del negocio | Configuración → Zona horaria → America/Havana |
| No aparece la página | No la agregaste o no eres admin | Configuración → Páginas → Agregar |
| El enlace no muestra imagen | Caché de Facebook | Sharing Debugger → “Scrape Again”; o añade `?v=2` |
| El post programado falla | Contenido marcado o permiso retirado | Revisa Planner → estado del post |
| No encuentro Planner | Menú distinto según versión | Ve directo a `business.facebook.com/planner` |

---

## 9. Orden recomendado para tus 10 posts

1. Crea la página.
2. Agrega la página a Business Suite.
3. Haz la prueba de 10 minutos.
4. Programa D1–D10 con la tabla de `FACEBOOK_10_POSTS.txt`.
5. Verifica en Planner que aparezcan los 10 como **Programados**.
6. El día 1, revisa a las 11:00 que D1 se publicó.

**No programes los grupos.** Esos se publican a mano, con permiso del administrador, y el enlace va en el primer comentario.
