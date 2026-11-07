# Plan de comunicación, crecimiento y anti-rebote

**Proyecto:** Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba
**Repositorio:** https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba
**Versión del plan:** 1.0 · 7 de noviembre de 2026
**Horizonte:** 90 días (9 de noviembre de 2026 → 7 de febrero de 2027)
**Presupuesto:** 0 USD (solo herramientas gratuitas y trabajo propio)
**Capacidad asumida:** 1 persona, 6–8 h/semana
**Estado:** planificación. **No se ha modificado ningún archivo del estudio.**

---

## 0. Cómo leer este plan

| Si tienes… | Lee… |
| --- | --- |
| 3 minutos | §1 Resumen ejecutivo + §13 Recomendaciones |
| 20 minutos | §2 Diagnóstico + §7 Arquitectura anti-rebote + §8 Canales |
| Una hora | Todo el documento, con `CALENDARIO_90_DIAS.csv` al lado |
| Que ejecutar ya | §9 Primeros 14 días + `PIEZAS_LISTAS.md` |

**Supuestos declarados** (corrígelos y el plan se recalibra):

1. El público prioritario habla español y está en La Habana o tiene vínculo con el mercado cubano de dos ruedas.
2. Tienes acceso normal a Facebook, WhatsApp, Telegram y GitHub. No hay presupuesto para anuncios.
3. Puedes activar GitHub Pages y crear cuentas gratuitas (GoatCounter, Zenodo, Google Search Console).
4. El objetivo no es "hacerse viral", sino **ser útil a mucha gente y que lo compartan por utilidad**. La viralidad es una consecuencia, no una estrategia.
5. El estudio se comunica como **diagnóstico de información**, no como predicción de ventas ni como avalúo.

---

## 1. Resumen ejecutivo

El estudio es sólido; **la puerta de entrada está rota**. Hoy un visitante llega a un README técnico de 13 KB, con seis tablas y ninguna imagen de contenido (solo tres insignias), y para leer el informe hace clic en un HTML de 1,7 MB que GitHub muestra como código fuente. GitHub Pages está desactivado. No hay instrumentación. El resultado esperado es abandono casi total en el segundo clic, antes de que el trabajo tenga oportunidad de demostrar su valor.

La estrategia tiene cuatro movimientos, en este orden:

1. **Arreglar el aterrizaje antes de atraer tráfico.** Un sitio estático gratuito (GitHub Pages) con una portada de 60 segundos, un resumen de 3 minutos, la guía y el informe completo. Sin registro, sin descargas obligatorias, en menos de 300 KB. Atraer tráfico hacia la página actual es pagar con audiencia un problema de diseño.
2. **Convertir el estudio en un sistema de contenido, no en un PDF.** 13 figuras, 8 secciones de guía, 5 decisiones metodológicas y 10 preguntas frecuentes son, como mínimo, **40 piezas nativas multicanal** (y más de 70 al aplicar la matriz de reutilización). Una pieza por publicación no escala; un sistema sí.
3. **Distribuir por reciprocidad comunitaria, no por intrusión.** Los vendedores están en grupos de Facebook, WhatsApp y Telegram. Se entra con permiso del administrador, valor completo dentro del post y enlace solo como segundo paso. Cero mensajes a los teléfonos del dataset: eso sería una violación de finalidad de la Ley 149/2022 y destruiría la credibilidad del proyecto.
4. **Medir para decidir, no para adornar.** Una métrica norte —personas que completan una acción útil—, seis métricas de embudo, experimentos preinscritos y un ritual semanal de 20 minutos. Sin medición, "evitar rebotes" es una opinión.

**Meta a 90 días (escenario base):** 50.000 impresiones, 3.000 visitas únicas al sitio, 65% de lectura comprometida, 18% de conversión a la guía, 800 usos de la calculadora de precio, 250 compartidos, 200 suscriptores de Telegram, 40 estrellas en GitHub y 3 menciones externas.

**Regla de oro del plan:** cada afirmación pública debe poder rastrearse hasta una cifra del estudio y hasta su limitación. La honestidad metodológica no es un adorno: es el principal diferenciador frente a cualquier contenido de mercado que ya circula.

---

## 2. Diagnóstico: qué ve hoy la audiencia

### 2.1 La prueba de los 10 segundos

Un vendedor abre el enlace del repositorio y ve: título largo, tres insignias, una tabla de documentos, un bloque de código de instalación. Lo que **no** ve: una imagen, una cifra que le hable, una promesa, un botón. A los 10 segundos no sabe si esto es para él. Se va.

Un comprador hace lo mismo. Un profesor de la Universidad de La Habana tarda un poco más: reconoce rigor en la estructura, pero no encuentra un resumen ejecutivo de una página ni un DOI que citar.

### 2.2 Evidencia recogida (verificada en el repositorio y en la API de GitHub)

| # | Hallazgo | Evidencia | Efecto sobre la audiencia |
| --- | --- | --- | --- |
| 1 | **GitHub Pages está desactivado** | `has_pages = false`; sin `homepage` | No existe "sitio del estudio": solo un repositorio |
| 2 | **El informe no se puede leer en GitHub** | `analysis/INFORME_FINAL.html` pesa 1,7 MB (1,66 MB son imágenes base64); github.com lo muestra como código | El clic más importante del embudo termina en abandono |
| 3 | **README es una puerta técnica** | 13 KB, 6 tablas, 3 insignias y 0 imágenes de contenido | No responde "¿esto qué me resuelve?" |
| 4 | **Las cifras de portada contradicen al estudio** | README: 5.391 vehículos y 8.779 en la tabla de fuentes; informe: 4.979 únicos y 4.860 vehículos | Rompe la confianza justo en el público que más valor tiene |
| 5 | **Enlaces y datos de contacto de plantilla** | `tu-usuario` en clonar/issues; correo `estudio-mercado@proyecto.local` | Señal de proyecto inacabado; el correo ficticio contradice el compromiso legal |
| 6 | **Referencias internas muertas** | El guion remite a `analysis/INFORME_ANALISIS.md`, que no existe | Fricción para quien quiere profundizar |
| 7 | **Sin señales de descubrimiento** | `topics = []`, sin descripción enriquecida, sin releases, sin `CITATION.cff`, sin DOI; licencia detectada como "Other" | GitHub no lo clasifica, no lo sugiere, no lo cita |
| 8 | **Sin imagen social ni portada** | Ninguna imagen fuera de `analysis/` | Al compartir el enlace no hay tarjeta visual |
| 9 | **Peso prohibitivo para datos móviles** | 1,7 MB el informe; 330 KB la presentación | En conexión móvil cubana, muchos no llegan al contenido |
| 10 | **Cero instrumentación** | Sin analítica; GitHub Insights solo cubre 14 días y solo el repo | Imposible saber rebote, fuente o lectura |
| 11 | **Ruido de publicación** | 4,2 MB de audios cifrados en un commit local sin publicar | Confunde la propuesta del proyecto si se publica tal cual |
| 12 | **Sin versión de bolsillo** | No hay PDF de 2 páginas ni resumen de 1 minuto | No hay nada que reenviar por WhatsApp, el canal real del mercado |
| 13 | **Tablas de la guía rotas en GitHub** | Dos tablas tienen filas HTML (`<tr>`) sin etiqueta `<table>`; la cabecera es Markdown | El activo más compartible se ve desalineado justo donde muestra precios |

### 2.3 Lectura del embudo actual

```
Ven un post/enlace  →  Repositorio  →  Clic en el informe  →  ✗ Abandono
                           │                    │
                           │                    └─ HTML crudo en pantalla de código
                           └─ README sin promesa ni imagen
```

No hay un problema de contenido: hay un **problema de correspondencia y de fricción**. La promesa del post no se repite en la página, y el contenido tarda demasiado en recompensar el clic. Cada paso añade una razón para irse.

### 2.4 Las ocho causas de rebote, ordenadas por impacto

1. **Desajuste de mensaje:** el post promete un dato; la página entrega un repositorio.
2. **Contenido que no se renderiza:** el HTML del informe solo se ve descargándolo.
3. **Peso y tiempo de carga:** 1,7 MB en móvil es una espera que nadie concede.
4. **Ausencia de jerarquía lectora:** 3.676 palabras sin un camino de 60 s → 3 min → completo.
5. **Cero llamada a la acción visible** en la primera pantalla.
6. **Fricción de descarga:** para obtener la guía hay que navegar carpetas.
7. **Falta de señales de confianza:** autor, fecha, método, límites y contacto real no están arriba.
8. **Sin motivo para volver:** no hay serie, canal, ni contenido nuevo prometido.

---

## 3. Objetivo, teoría del cambio y métrica norte

### 3.1 Teoría del cambio

El impacto no depende solo del alcance. Depende de cuatro multiplicadores y de un divisor:

```
Impacto  ≈  (Alcance × Relevancia × Confianza × Facilidad de compartir) / Fricción
```

| Palanca | Qué la mueve en este plan |
| --- | --- |
| **Alcance** | Presencia en los canales donde ya está el mercado (§8) y sistema de contenidos (§6) |
| **Relevancia** | Mensajes construidos sobre dolores concretos: "no me encuentran", "no sé si cobro bien" (§5) |
| **Confianza** | Método auditable, límites declarados, correcciones públicas, autor identificable (§12) |
| **Compartir** | Piezas autocontenidas y reenviables: tarjeta de precios, checklist, calculadora (§7) |
| **Fricción** | Sitio ligero, sin registro, lectura por niveles, un clic por paso (§7) |

Si una acción no mueve al menos una de estas cinco, no entra al calendario.

### 3.2 Métrica norte

> **Personas que completan una acción útil:** descargar el checklist, usar la calculadora, compartir una tarjeta o asistir a una charla.

No es "visitas". Una visita que rebota no es impacto; una persona que usa la calculadora y la comparte, sí. Las visitas son un medio para estimar cuántas de esas personas podemos alcanzar.

### 3.3 Objetivos a 90 días

| Escenario | Visitas únicas | Lectura comprometida | Guía descargada | Calculadora | Compartidos | Telegram | Stars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Conservador | 1.200 | 55% | 150 | 250 | 80 | 60 | 15 |
| **Base** | **3.000** | **65%** | **540** | **800** | **250** | **200** | **40** |
| Ambicioso | 7.000 | 70% | 1.400 | 2.000 | 600 | 500 | 100 |

**Regla de decisión:** si al día 30 la lectura comprometida es menor al 45%, se congela la distribución y se arregla la página. No se escala un embudo que gotea.

---

## 4. Audiencias

### 4.1 Segmentos y promesa

| Segmento | Quién es | Qué necesita | Promesa | Canal principal | Objeción |
| --- | --- | --- | --- | --- | --- |
| **A. Vendedor particular** | Vende 1–3 vehículos al año; publica en Revolico y grupos | Vender rápido y no regalar el vehículo | "Tu anuncio puede estar invisible y no es por el precio" | Facebook, WhatsApp, Telegram | "Otro que quiere venderme algo" |
| **B. Comprador** | Busca eléctrica o bici para moverse; compara precios | No pagar de más; saber qué es razonable | "Cuánto se está pidiendo de verdad, por tipo y por zona" | Facebook, WhatsApp, Instagram | "Los precios publicados son mentira" |
| **C. Taller y repuestero** | Vende piezas, repara, conoce el mercado | Proveedores, precios de referencia, huecos | "Dónde está la demanda que nadie atiende" | Telegram, grupos técnicos | "Esto no aplica a piezas" |
| **D. Emprendedor de movilidad** | Delivery, alquiler, compraventa de 5–20 unidades | Decidir compra/venta con criterio; rotación | "Dónde comprar, a qué precio y en qué zona" | LinkedIn, WhatsApp directo | "Necesito datos de ventas, no de anuncios" |
| **E. Técnico y académico** | Estudiantes y profesores de MatCom/UCI/CUJAE, devs | Método reproducible, datos citables | "Un dataset abierto y auditable de un mercado sin registro" | GitHub, LinkedIn, universidad | "¿Dónde está el DOI / la validación?" |
| **F. Divulgador y prensa** | Periodistas de economía/tecnología, creadores | Dato + historia + fuente confiable | "El primer diagnóstico cuantitativo del mercado de dos ruedas en La Habana" | Correo, LinkedIn, X | "¿Es riguroso o es un scraping?" |

**Prioridad de esfuerzo:** A y B concentran el 70% del trabajo (son el mercado real y los que comparten por utilidad). E y F dan credibilidad y amplificación, con poco volumen pero alto efecto de reputación. C y D son secundarios hasta que exista contenido específico.

### 4.2 Qué NO es la audiencia

No es "todo el mundo". No son compradores fuera de Cuba. No son inversores. No son políticos. Cada intento de hablarle a todos diluye el mensaje y aumenta el rebote.

---

## 5. Posicionamiento y arquitectura de mensaje

### 5.1 Posicionamiento

> **El mapa de precios y de errores del mercado de motos en La Habana, hecho con 4.979 anuncios reales.**
> No es un curso. No es publicidad. Es una lectura del mercado para que decidas con datos.

Tres decisiones de posicionamiento:

- **Categoría:** diagnóstico de información de mercado (no consultoría, no avalúo, no curso).
- **Enemigo:** la información que falta, nunca las personas que venden.
- **Prueba:** cada cifra es reproducible con el pipeline publicado.

### 5.2 Mensajes clave

| # | Mensaje | Prueba | Implicación práctica |
| --- | --- | --- | --- |
| 1 | Casi la mitad de los anuncios no dice la marca | 45,5% de 4.860 vehículos (2.210) sin marca | Escribe la marca en el título: es gratis y es lo que más cambia |
| 2 | El título es el 90% de la venta | 43,3% sin ningún número (2.155) | Marca + cifra clave + zona + estado |
| 3 | Las bicicletas son el segmento peor documentado | 87,1% sin marca (451 de 518) | Oportunidad para quien documente bien |
| 4 | El precio depende del tipo y de la zona | Medianas: motores 2.000 / eléctricas 1.600 / bicis 160 USD; Habana Vieja 1.620 vs Cerro 700 | Compara contra tu categoría y tu municipio, no contra el total |
| 5 | WhatsApp es el canal real | 59,9% de los anuncios lo incluyen | Publícalo y responde en horario |
| 6 | Los patinetes y las zonas periféricas están vacíos | 64 anuncios de patinetes; Centro Habana concentra 24% de la oferta con precio y zona | Menos competencia donde nadie publica |

**Meta-mensaje transversal (siempre presente):** *más publicado no es más vendido; los precios son declarados, no avalúos.*

### 5.3 Reglas de lenguaje

**Sí:** anuncios, precio declarado, mediana, referencia, "según 4.979 anuncios", "en La Habana", "no sabemos".
**No:** avalúo, predicción, garantizado, "el mercado dice", "todos los vendedores", "revolución", "los precios van a subir".
**Tono:** directo, respetuoso, sin culpa, sin jerga innecesaria. Una idea por pieza. Una acción por pieza.
**Formato:** cifra grande + una frase de consecuencia + una acción. Nunca tres cifras en el mismo párrafo.

### 5.4 Promesa por nivel de lectura

| Nivel | Tiempo | Contenido | Llamada a la acción |
| --- | --- | --- | --- |
| 1. Gancho | 5 s | Una cifra + una consecuencia | "Mira si tu anuncio está aquí" |
| 2. Resumen | 60 s | Tres datos + el estándar mínimo | "Descarga el checklist" |
| 3. Informe breve | 3 min | El argumento completo con 3 figuras | "Usa la calculadora" |
| 4. Estudio | 20–40 min | Informe académico completo | "Cita el dataset / comparte" |

---

## 6. Sistema de contenidos

### 6.1 Seis pilares (series reconocibles)

| Pilar | Nombre de serie | Qué entrega | Cadencia |
| --- | --- | --- | --- |
| Precio | **Precio justo** | Referencia por tipo, marca y zona | Semanal |
| Visibilidad | **Anatomía de un anuncio** | Antes/después, errores concretos | Semanal |
| Oportunidad | **Los huecos** | Dónde hay poca oferta y por qué importa | Quincenal |
| Método | **Detrás del dato** | Cómo se hizo, errores corregidos, límites | Quincenal |
| Herramientas | **30 segundos** | Checklist, calculadora, generador de título | Mensual |
| Comunidad | **Preguntas del mercado** | Dudas reales de la audiencia, respondidas con datos | Semanal |

Las series cumplen dos funciones: dan motivo para volver y permiten producir en lote sin decidir cada semana.

### 6.2 Matriz de reutilización (una fuente, muchos formatos)

| Activo original | Piezas derivadas | Canal |
| --- | --- | --- |
| 13 figuras del informe | 13 tarjetas 1080×1350 + 3 carruseles de 6 láminas | Instagram, Facebook, Telegram |
| 8 secciones de la guía | 8 videos de 30–45 s + 8 posts de texto | TikTok, Reels, Facebook |
| 10 puntos del checklist | 1 PDF de 2 páginas + 10 historias + 1 carrusel | WhatsApp, Instagram |
| 5 correcciones metodológicas | 5 posts "Detrás del dato" + 1 hilo técnico | LinkedIn, GitHub |
| 12 preguntas frecuentes | 12 historias con pregunta/respuesta | Instagram, Telegram |
| Tabla de precios por marca | 1 calculadora + 6 tarjetas "marca X, mediana Y" | Sitio, WhatsApp |
| Presentación de 14 diapositivas | 1 video de 6 min + 1 PDF + 14 tarjetas | YouTube, LinkedIn |

**Resultado:** de 6 activos existentes salen más de 70 piezas sin producir material nuevo. El estudio ya está hecho; lo que falta es traducción.

### 6.3 Banco de 20 titulares listos

1. El 45% de las motos en venta en La Habana no dice su marca. Por eso nadie las encuentra.
2. Vendes una moto. ¿Sabes cuánto se está pidiendo por esa marca este mes?
3. "MOTO SE VENDE" vs. "AVA 100 km, seminueva, Centro Habana": el mismo vehículo, dos resultados.
4. Las bicicletas son el negocio peor contado de La Habana: 87% sin marca.
5. Habana Vieja pide 2,3 veces más que El Cerro. No es el vehículo: es la zona.
6. 64 patinetes en todo el mercado. Ese es el tamaño de la competencia.
7. El precio no es tu problema. La información sí.
8. 4.979 anuncios después, esto es lo que aprendí sobre vender motos en Cuba.
9. Lo que WhatsApp dice del mercado: 6 de cada 10 anuncios ya lo usan.
10. Tres palabras que cambian un anuncio invisible: marca, cifra, zona.
11. No publiques más. Publica mejor.
12. El error que cometí analizando 4.979 anuncios (y por qué importa para tu precio).
13. Cómo saber si tu moto está cara: compara con tu zona, no con tu vecino.
14. La mediana manda: 2.000 USD en combustión, 1.600 en eléctricas, 160 en bicis.
15. Por qué "más publicado" no significa "más vendido".
16. El 43% de los anuncios no tiene ni un número en el título. Ni precio, ni cilindraje, ni autonomía.
17. Lo que el mercado de motos de La Habana no dice (y debería).
18. Un anuncio mal escrito cuesta más que un descuento.
19. Si vendes en La Habana, esta tabla te dice dónde hay menos competencia.
20. El estudio que faltaba: 4.979 anuncios, 4 fuentes, 0 excusas.

### 6.4 Regla de producción

> **Nunca publicar una pieza que no pueda entenderse sin hacer clic.**

El enlace es el segundo paso, no el primero. Esto reduce rebotes (el valor ya se entregó) y protege de los algoritmos que penalizan enlaces externos.

---

## 7. Arquitectura anti-rebote

Esta sección es el corazón del plan. El objetivo no es "retener" con trucos, sino **recompensar cada clic más rápido de lo que cuesta darlo**.

### 7.1 Mapa del sitio (GitHub Pages, coste 0)

```
/                     Portada: promesa + 3 datos + 2 CTA (60 s)
/resumen              Resumen ejecutivo de 3 minutos, 3 figuras
/informe              Informe completo, carga diferida por secciones
/guia                 Guía del vendedor + checklist descargable
/precios              Calculadora de precio de referencia (n≥30)
/datos                Dataset, diccionario, licencia, cómo citar
/metodo               Cómo se hizo + límites + auditoría
/prensa               Kit de prensa: 3 datos, 2 historias, contacto
```

**Regla:** todo lo publicado apunta a `/` o a una página del mapa. Nunca a un archivo crudo del repositorio.

### 7.2 Las doce reglas de la portada

1. **Titular con la promesa y la cifra:** "4.979 anuncios reales: así se vende (y se esconde) el mercado de motos en La Habana".
2. **Subtítulo de una frase** que diga para quién es.
3. **Tres cifras grandes** con su implicación, no una pared de texto.
4. **Un CTA primario** ("Ver el resumen de 3 minutos") y uno secundario ("Descargar el checklist").
5. **Sin registro, sin correo obligatorio, sin ventanas modales.**
6. **Prueba de autoridad:** autor, fecha, método, fuentes, límites, enlace a `/metodo`.
7. **Correspondencia exacta** con el texto del post que trajo al visitante (misma frase, mismo dato).
8. **Velocidad:** menos de 300 KB, sin fuentes externas, sin CDN, sin vídeo automático.
9. **Móvil primero:** una columna, tipografía ≥17 px, botones ≥44 px.
10. **Navegación de lectura:** progreso visible y "seguir leyendo" cada 2 pantallas.
11. **Salida útil:** si se va, que se lleve una tarjeta de precios o el enlace al canal.
12. **Cero trampas:** sin cuenta atrás, sin "solo hoy", sin oscurecer el cierre.

### 7.3 Presupuesto de rendimiento (no negociable)

| Métrica | Objetivo | Por qué |
| --- | --- | --- |
| Peso de la portada | < 300 KB | Datos móviles caros y lentos |
| Peso del informe | < 800 KB (carga diferida) | Hoy son 1,7 MB de golpe |
| LCP en 3G | < 2,5 s | Cada segundo extra cuesta lectores |
| Peticiones externas | 0 | Evita bloqueos y latencia |
| Funciona sin JS | Sí, el contenido | Robustez y accesibilidad |
| Funciona sin internet tras la primera visita | Sí (PWA opcional) | Realidad de conectividad |

### 7.4 Correspondencia mensaje → página

| El post dice | La página debe decir (arriba) | CTA |
| --- | --- | --- |
| "45% no dice marca" | El mismo 45,5%, con la fuente y la fecha | "Mira las 10 marcas más buscadas" |
| "Habana Vieja pide 2,3× más" | La tabla de zonas, con n por municipio | "Calcula tu precio por zona" |
| "El mismo vehículo, dos anuncios" | El antes/después completo | "Descarga la plantilla de título" |
| "Así se hizo" | El método y la auditoría | "Lee el informe completo" |

Si la frase no coincide, el visitante siente que lo engañaron y se va. La correspondencia es la palanca más barata contra el rebote.

### 7.5 Flujo de lectura por niveles

```
Portada (60 s)
   ├─ 3 datos + 1 acción  →  Checklist (PDF 2 páginas)
   ├─ "Seguir leyendo"     →  /resumen (3 min, 3 figuras)
   │                             ├─ "Ver los datos"   →  /precios (calculadora)
   │                             └─ "El estudio"      →  /informe (completo)
   └─ "Si te vas, llévate" →  Tarjeta de precios + canal de Telegram
```

Cada nivel termina en una acción concreta. Nunca en un callejón sin salida.

### 7.6 Qué haremos con el informe actual

No se reescribe: se **envuelve**. El HTML de 1,7 MB se conserva como obra completa en `/informe`, con carga diferida y un resumen delante. El PDF de 2 páginas no compite con él: lo alimenta. Así se protege el trabajo académico y se le da una puerta usable.

---

## 8. Plan de canales a coste 0

### 8.1 Mapa de canales

| Canal | Rol | Cadencia | Regla de oro | Riesgo |
| --- | --- | --- | --- | --- |
| **WhatsApp** | Distribución capilar y reenvío | 3 estados/semana; 5 grupos | Solo con permiso; nunca DM a teléfonos del dataset | Ser percibido como spam |
| **Facebook (grupos)** | Donde está el mercado | 3–5 grupos/semana | Contenido completo en el post; enlace en primer comentario | Baneo por enlaces |
| **Telegram** | Canal propio y grupos técnicos | 3/semana + archivos | PDF ligero y texto; respuestas honestas | Bajo |
| **Instagram / TikTok** | Descubrimiento y recordación | 3 reels/semana | Gancho en 1,5 s; subtítulos; 9:16 | Producción consume tiempo |
| **YouTube** | Credibilidad y búsqueda | 1 video/2 semanas + Shorts | Capítulos, subtítulos, descripción con fuentes | Bajo |
| **GitHub** | Casa técnica y sello de rigor | Continuo | Topics, release, DOI, Discussions | Audiencia pequeña si no se traduce |
| **LinkedIn** | Academia, prensa, LatAm data | 2/semana | Carrusel + aprendizaje, no enlace seco | Bajo |
| **Universidad** | Validación y relevo | 1 charla/mes | Oferta concreta: dataset para prácticas | Logística |
| **Prensa / newsletters** | Amplificación | 1 pitch/semana | Dato + historia + fuente en 1 página | Ignorar el correo |
| **SEO** | Tráfico duradero | Continuo | Páginas por pregunta real, no por palabra clave vacía | Tarda 2–3 meses |
| **Reddit / HN** | Pico y crítica técnica | 1 intento | Inglés, humildad, responder todo | Recepción dura |

### 8.2 Playbook de WhatsApp

- **Estados:** 3 por semana, imagen 1080×1920 con una cifra y una frase. Texto corto: "45% de las motos en venta no dice su marca. Si vendes, esto te interesa."
- **Grupos:** máximo 5 grupos, 2 publicaciones por semana, nunca el mismo texto. Pedir permiso al administrador por privado antes de entrar.
- **Lista de difusión:** solo con opt-in explícito ("si quieres recibir el dato semanal, responde SÍ").
- **Prohibido:** usar los teléfonos del dataset. Ese dato se recogió para analizar el mercado, no para hacer marketing. La finalidad es incompatible con la Ley 149/2022 (Art. 10.c y 10.d) y es la línea ética que más daño haría si se cruza.

### 8.3 Playbook de Facebook

- **Los 10 grupos ya identificados** son el punto de partida natural, pero se entra como participante, no como anunciante.
- **Estructura del post:** dato → consecuencia → acción → pregunta. El enlace va en el primer comentario.
- **Cadencia:** 1 post por grupo por semana como máximo. Alternar grupos para no saturar.
- **Horario:** 19:00–21:30 (hora de La Habana), cuando hay actividad.
- **Moderación:** responder todos los comentarios en menos de 12 h. Una crítica bien respondida vale más que diez "me gusta".
- **Nunca:** publicar el mismo texto en 10 grupos el mismo día. Es la firma del spam.

### 8.4 Playbook de video (30–45 s)

Estructura fija, sin excepciones:

1. **0–1,5 s:** la cifra en pantalla + frase de choque.
2. **1,5–10 s:** qué significa para quien vende o compra.
3. **10–30 s:** una prueba visual (la figura o la tabla).
4. **30–40 s:** la acción de costo cero.
5. **40–45 s:** "el estudio completo está en el enlace".

Producir 4 videos en una sola sesión de 90 minutos al mes. Subtítulos siempre: se consume sin sonido.

### 8.5 Playbook de GitHub (para la audiencia técnica)

- **Topics:** `cuba`, `havana`, `market-analysis`, `data-science`, `open-data`, `scraping`, `motorcycles`, `spanish`.
- **Release v1.0** con notas claras y enlace al sitio.
- **`CITATION.cff`** y **DOI de Zenodo**: convierten el repositorio en algo citable. Es el cambio de mayor retorno para la audiencia académica y cuesta cero.
- **Discussions** con tres categorías: "Pregunta al estudio", "Pide tu zona/marca", "Errores y correcciones".
- **Un `good first issue`** real: "Añadir una fuente" o "Traducir el resumen al inglés".
- **Descripción del repo:** una frase con la promesa y el enlace al sitio.

### 8.6 Playbook académico

- **Objetivo:** 10 profesores contactados, 2 charlas, 1 uso del dataset en clase.
- **Oferta:** "20 minutos de charla + dataset anonimizado para prácticas + guía de reproducción". Sin costo, sin pedir nada.
- **Mensaje:** adjuntar el resumen de 2 páginas, no el repositorio. El repositorio va en el segundo correo.
- **Universidades:** Facultad de Matemática y Computación (UH), CUJAE, UCI, grupos de estudiantes de datos.

### 8.7 Playbook de prensa

- **Nota de 1 página:** titular, 3 datos, 2 historias humanas (anonimizadas), 1 cita del autor, enlace y contacto real.
- **Ángulo:** consumo y emprendimiento ("cómo saber si te están cobrando de más"), no política.
- **Lista de 10:** periodistas de economía/tecnología, newsletters de emprendimiento cubano, podcasts locales.
- **Seguimiento:** un correo, un recordatorio a los 5 días, nunca más.

### 8.8 SEO de cola larga

Páginas que responden preguntas reales, cada una con datos del estudio:

- "Cuánto cuesta una moto eléctrica en La Habana"
- "Precio de una bici eléctrica en Cuba"
- "Cómo vender una moto rápido en Revolico"
- "Qué marca de moto eléctrica es más cara"
- "Precio de motos por municipio en La Habana"

Cada página: título con la pregunta, respuesta en la primera pantalla, tabla con n y mediana, fecha, enlace al método. Sin relleno.

---

## 9. Calendario de 90 días

### 9.1 Fases

| Fase | Fechas | Objetivo | Hito de salida |
| --- | --- | --- | --- |
| **0. Cimientos** | 9–15 nov | Que el sitio exista y se pueda medir | Portada publicada + analítica + 6 piezas de reserva |
| **1. Lanzamiento suave** | 16–29 nov | Validar mensajes en 3 grupos piloto | 3 mensajes con CTR conocido; página ajustada |
| **2. Ampliación** | 30 nov–20 dic | Abrir video, LinkedIn, prensa y DOI | 1.000 visitas; 1 mención; DOI activo |
| **3. Sostenimiento** | 21 dic–31 ene | Serie semanal + herramienta + comunidad | 2.500 visitas; 500 usos de calculadora; 150 en Telegram |
| **4. Cierre** | 1–7 feb | Decidir qué escalar y qué cerrar | Informe de impacto y plan v2 |

### 9.2 Semana tipo (6–8 h)

| Día | Bloque | Tiempo |
| --- | --- | --- |
| Lunes | Revisión de métricas + decisión de la semana | 20 min |
| Martes | Publicación A (precio/visibilidad) + respuesta a comentarios | 60 min |
| Miércoles | Acción comunitaria (grupo, pregunta, respuesta) | 45 min |
| Jueves | Publicación B (reel o carrusel) | 60 min |
| Viernes | Publicación C o video + LinkedIn | 60 min |
| Sábado | Publicación D (opcional) + resumen semanal | 45 min |
| Domingo | Producción en lote (3–4 piezas) | 120 min |

**Regla de capacidad:** si una semana se pasa de 8 h, se recorta la producción, no la respuesta a la comunidad. El silencio ante una pregunta cuesta más que una publicación menos.

### 9.3 Primeros 14 días, día a día

| Fecha | Acción | Resultado esperado |
| --- | --- | --- |
| Lun 9 nov | Activar GitHub Pages; publicar portada mínima; instalar GoatCounter | URL del sitio funcionando |
| Mar 10 | Crear PDF de 2 páginas y tarjeta de precios; definir UTMs | Material reenviable |
| Mié 11 | Escribir 6 piezas de reserva; preparar kit de prensa | Colchón de contenido |
| Jue 12 | Lista de 30 contactos (grupos, profesores, periodistas); pedir permiso a 3 admins | Accesos concedidos |
| Vie 13 | Prueba interna de la portada con 5 personas ajenas al proyecto | 3 mejoras identificadas |
| Sáb 14 | Corregir portada; publicar release v1.0 y topics | Repo presentable |
| Dom 15 | Ensayo general: publicar en 1 grupo piloto y medir 24 h | Primera curva real |
| Lun 16 | **Lanzamiento:** post principal + estado de WhatsApp | 300–800 impresiones |
| Mar 17 | Publicar "45% sin marca" en 2 grupos distintos | CTR por grupo |
| Mié 18 | Responder comentarios; ajustar titular si CTR < 2% | Aprendizaje aplicado |
| Jue 19 | Reel "El mismo vehículo, dos anuncios" | Primer video |
| Vie 20 | LinkedIn técnico: "cómo deduplicamos 4.979 anuncios" | 5–20 visitas cualificadas |
| Sáb 21 | Publicar "Habana Vieja vs El Cerro" | Prueba de mensaje 2 |
| Dom 22 | Revisión semanal: 5 números, 1 decisión, 1 experimento | Semana 1 cerrada |

El detalle completo está en `CALENDARIO_90_DIAS.csv`.

---

## 10. Producción y operación

### 10.1 Stack gratuito

| Necesidad | Herramienta | Coste |
| --- | --- | --- |
| Sitio | GitHub Pages | 0 |
| Analítica | GoatCounter (sin cookies, 3 KB) | 0 |
| Formularios | Google Forms | 0 |
| Diseño | Canva gratis | 0 |
| Video | CapCut / OBS | 0 |
| PDF | LibreOffice | 0 |
| DOI | Zenodo | 0 |
| Correo | Gmail | 0 |
| Programación | Buffer gratis / publicación manual | 0 |
| Búsqueda | Google Search Console | 0 |

### 10.2 Flujo semanal

1. **Lunes:** leer 5 números y elegir el foco.
2. **Martes–jueves:** publicar lo que ya está en el banco.
3. **Viernes:** revisar comentarios y preguntas; las mejores se convierten en piezas.
4. **Domingo:** producir 3–4 piezas del banco y dejar la semana armada.

### 10.3 Checklist antes de publicar (10 puntos)

- [ ] ¿La primera línea tiene una cifra o una consecuencia?
- [ ] ¿Se entiende sin hacer clic?
- [ ] ¿La cifra está en el estudio y tiene su limitación al lado?
- [ ] ¿Hay una sola acción pedida?
- [ ] ¿El enlace lleva a la página correcta y no a un archivo crudo?
- [ ] ¿La imagen se lee en un teléfono a 30 cm?
- [ ] ¿Tiene texto alternativo?
- [ ] ¿Está libre de datos personales (teléfonos, nombres, capturas sin difuminar)?
- [ ] ¿Respeta la cadencia del grupo o canal?
- [ ] ¿Puedo responder en 12 h?

---

## 11. Medición y experimentación

### 11.1 Definiciones

| Métrica | Definición operativa |
| --- | --- |
| Visita única | Sesión distinta por dispositivo/día en GoatCounter |
| Lectura comprometida | ≥60 s en página **y** ≥50% de scroll |
| CTR de post | Clics al sitio / impresiones estimadas del canal |
| Conversión a guía | Descargas o aperturas del PDF / visitas a `/guia` |
| Uso de calculadora | Cálculo completado / visitas a `/precios` |
| Compartido | Evento explícito de compartir + enlaces con UTM de reenvío |
| Retorno | 2+ sesiones en 30 días |
| Rebote | Sesión <10 s sin interacción (definición propia y estable) |

### 11.2 Convención UTM

```
utm_source   = whatsapp | facebook | telegram | instagram | tiktok | youtube | linkedin | github | universidad | prensa
utm_medium   = social | community | referral | email | talk | search
utm_campaign = lanzamiento | serie-precio | serie-visibilidad | guia | calculadora | informe
utm_content  = p01 … p40 (id de pieza)
```

Sin esta convención no se puede saber qué pieza trae lectores que **actúan**, solo cuántos clics trae.

### 11.3 Experimentos (preinscritos, 6)

| # | Hipótesis | Diseño | Métrica | Regla de decisión |
| --- | --- | --- | --- | --- |
| 1 | La pérdida ("estás invisible") supera a la curiosidad | 2 titulares, mismo grupo, misma hora, 48 h | CTR | Gana el de ≥30% más CTR; si no, empate |
| 2 | El antes/después convierte más que la cifra sola | 2 posts alternos en semanas distintas | Clics + tiempo | Adoptar el ganador 3 semanas |
| 3 | El video de 30 s retiene más que el carrusel | 1 semana cada formato | Lectura comprometida | Escalar el de mayor retención |
| 4 | Un CTA supera a dos en la portada | A/B con GoatCounter | Conversión | Un solo CTA si gana por ≥20% |
| 5 | El enlace en el primer comentario supera al enlace en el post | 2 grupos comparables | CTR + alcance | Adoptar según el resultado |
| 6 | La calculadora retiene más que la guía | Fuente de tráfico cruzada | Retorno a 7 días | Convertir la calculadora en CTA principal |

**Regla estadística:** no se declara ganador con menos de 100 impresiones por variante ni antes de 48 h. Los resultados nulos se documentan igual.

### 11.4 Ritual

- **Semanal (20 min):** visitas, lectura, conversión, compartidos, mejor y peor pieza → una decisión.
- **Mensual (45 min):** cohortes por canal, tres experimentos, ajuste del calendario.
- **Final (90 días):** informe de impacto con lo que funcionó, lo que no y lo que se abandona.

---

## 12. Ética, privacidad y riesgos

### 12.1 Líneas rojas (no negociables)

1. **No contactar** a personas del dataset por teléfono, WhatsApp o redes. Los datos se recogieron para analizar el mercado, no para hacer prospección.
2. **No publicar** nombres, teléfonos, URLs de anuncio ni capturas sin difuminar.
3. **No desagregar** celdas con menos de 30 casos: riesgo de reidentificación.
4. **No usar** cuentas falsas, bots, ni grupos de apoyo mutuo para inflar métricas.
5. **No hacer spam** en grupos: permiso del administrador y cadencia limitada.
6. **No prometer** ventas, causalidad ni predicciones de precio.
7. **No usar** el estudio para estigmatizar a vendedores informales ni para narrativas políticas.
8. **No ocultar** limitaciones ni corregir en silencio: errata pública.
9. **No usar** imágenes de terceros sin licencia.
10. **No monetizar** datos personales. El proyecto es de coste cero y sin fin comercial.

### 12.2 Ley 149/2022 aplicada a la difusión

El estudio ya cumple en la recolección y la publicación del dataset. La difusión añade tres obligaciones:

- **Finalidad (Art. 10.c):** comunicar un diagnóstico académico. Cualquier uso publicitario queda fuera.
- **Minimización (Art. 10.a):** en las piezas se usan agregados, no registros.
- **Derechos del titular (Arts. 20–23):** correo real y procedimiento de retirada en menos de 10 días hábiles. El correo de plantilla actual (`estudio-mercado@proyecto.local`) debe sustituirse antes de cualquier campaña.

### 12.3 Matriz de riesgos

| Riesgo | Prob. | Impacto | Mitigación |
| --- | --- | --- | --- |
| Acusación de spam en grupos | Media | Alto | Permiso previo, valor completo en el post, 1/semana |
| Crítica metodológica ("precios no son ventas") | Alta | Medio | Límites en la primera pantalla; FAQ; enlace al método |
| Reclamo de privacidad | Baja | Alto | Datos agregados, difuminado, correo real, retirada rápida |
| Mala recepción política | Baja | Alto | Enfoque consumo/emprendimiento; sin actores políticos |
| Baneo de cuenta o enlace | Media | Medio | Variar formatos; no depender de un solo canal |
| Desgaste del autor | Alta | Alto | Capacidad máxima 8 h/semana; banco de piezas; pausas |
| Baja calidad percibida por cifras inconsistentes | Alta | Alto | Una sola fuente de verdad numérica antes del lanzamiento |

### 12.4 Protocolo de crisis (48 h)

1. **Escuchar** sin borrar: capturar la crítica textual.
2. **Verificar** contra el estudio y la auditoría.
3. **Responder** en público, en menos de 48 h, con la cifra y la limitación.
4. **Corregir** si hay error, con nota de errata visible.
5. **No discutir** con cuentas anónimas más de dos respuestas.

---

## 13. Recomendaciones para mejorar la atractividad del proyecto

**No se ejecuta nada en esta fase.** Se ordena por impacto/esfuerzo para que se decida después. ICE = Impacto (1–10) × Confianza (1–10) × Facilidad (1–10) / 10.

### 13.1 Arreglos de una hora (mayor retorno inmediato)

| # | Acción | Por qué | ICE |
| --- | --- | --- | --- |
| 1 | **Activar GitHub Pages** con una portada real | Sin sitio no hay embudo; es el cambio que desbloquea todo | 100 |
| 2 | **Unificar las cifras** en README, informe y guía (4.979 / 4.860) | La inconsistencia destruye credibilidad en la primera lectura | 98 |
| 3 | **Quitar `EOF`**, arreglar `tu-usuario` y el correo ficticio | Señales de abandono que cuestan confianza | 95 |
| 4 | **Añadir topics, descripción y `CITATION.cff`** | Descubrimiento y citabilidad a coste cero | 92 |
| 5 | **PDF de 2 páginas + tarjeta de precios** | Es lo que se reenvía por WhatsApp | 90 |
| 6 | **Release v1.0** con notas | Punto de entrada ordenado y fecha de referencia | 85 |
| 7 | **Imagen social 1200×630** | El enlace deja de verse vacío al compartirse | 82 |
| 8 | **Arreglar la referencia a `INFORME_ANALISIS.md`** | Enlace muerto en el material de respaldo | 80 |
| 9 | **Corregir el JSON de ejemplo** (claves duplicadas) y la tabla de datasets repetida | Detalle que delata falta de revisión | 78 |
| 10 | **Sustituir el correo legal por uno real** | Coherencia con el compromiso de derechos | 76 |

### 13.2 Atractividad de lectura

| # | Acción | Por qué | ICE |
| --- | --- | --- | --- |
| 11 | **Tres niveles de lectura** (60 s / 3 min / completo) con navegación | El 90% no leerá 3.676 palabras de una vez | 96 |
| 12 | **Versión ligera** (<300 KB) y carga diferida de figuras | Conectividad móvil cubana | 94 |
| 13 | **Figuras adaptadas a móvil** (versiones verticales o gráficos en CSS) | Las actuales son de 2.000 px y texto pequeño | 88 |
| 14 | **Índice fijo y progreso de lectura** | Orienta en un documento largo | 75 |
| 15 | **PDF imprimible y modo offline (PWA)** | Uso en aulas y talleres sin datos | 72 |
| 16 | **Reparar las dos tablas de la guía** (filas HTML sin `<table>`) | Es donde se leen los precios; hoy se rompen en GitHub | 77 |
| 17 | **Glosario de 12 términos** (mediana, n, declarado) | Baja la barrera para público no técnico | 68 |

### 13.3 Producto y utilidad

| # | Acción | Por qué | ICE |
| --- | --- | --- | --- |
| 18 | **Calculadora de precio de referencia** (estática, n≥30) | Convierte lectura en herramienta; motivo de retorno | 95 |
| 19 | **Generador de título** que aplica el estándar mínimo | Acción inmediata y resultado visible | 90 |
| 20 | **"Score del anuncio" 0–10** con recomendaciones | Gamifica la mejora sin manipular | 84 |
| 21 | **Tarjeta de precios compartible** por marca/zona | Unidad de reenvío por WhatsApp | 86 |
| 22 | **Plantilla de anuncio** descargable | Uso práctico inmediato | 80 |
| 23 | **Comparador de zonas** | Responde "¿dónde vendo mejor?" | 74 |

### 13.4 Confianza y comunidad

| # | Acción | Por qué | ICE |
| --- | --- | --- | --- |
| 24 | **DOI de Zenodo** + cómo citar | Sello académico gratuito | 88 |
| 25 | **Página de método y límites** enlazada arriba | Anticipa la crítica y la desarma | 86 |
| 26 | **Errata y changelog visibles** | La corrección pública es prueba de rigor | 78 |
| 27 | **GitHub Discussions** con tres categorías | Convierte audiencia en comunidad | 72 |
| 28 | **"Pide tu zona o marca"** (crowdsourcing de análisis) | Genera contenido y pertenencia | 70 |
| 29 | **Créditos a colaboradores** y charla mensual de 30 min | Sostiene la participación sin costo | 65 |

### 13.5 Presentación y marca

| # | Acción | Por qué | ICE |
| --- | --- | --- | --- |
| 30 | **Identidad visual mínima**: un color de acento, cifras grandes, mismas reglas en todas las figuras | Coherencia = profesionalidad percibida | 80 |
| 31 | **Portada del estudio** (1 imagen, 1 frase, 3 datos) | Primera impresión | 84 |
| 32 | **Textos alternativos y contraste AA** | Accesibilidad y SEO | 70 |
| 33 | **Subtítulos en todos los videos** | Consumo sin sonido | 76 |
| 34 | **Resumen en inglés** (1 página) | Alcance internacional y HN/Reddit | 60 |
| 35 | **Auditar el repo de ruido** (audios, datos crudos, temporales) | Claridad de propuesta | 74 |

### 13.6 Qué NO hacer

- Comprar seguidores, usar bots o grupos de apoyo mutuo.
- Anuncios pagados: el presupuesto es cero y el retorno no está probado.
- Titulares que prometan predicciones o "secretos del mercado".
- Publicar el mismo texto en 10 grupos el mismo día.
- Perseguir estrellas de GitHub como métrica principal.
- Añadir funciones nuevas antes de arreglar la portada.
- Reescribir el informe académico: hay que envolverlo, no rehacerlo.

### 13.7 Secuencia recomendada (si se aprueba)

1. **Semana 1:** arreglos de una hora (1–10) + portada.
2. **Semana 2:** tres niveles de lectura + PDF + peso.
3. **Semana 3:** calculadora + tarjeta de precios.
4. **Semana 4:** DOI, método, errata, Discussions.
5. **Después:** identidad visual y traducción.

---

## 14. Gobernanza y sostenibilidad

- **Capacidad:** 6–8 h/semana, con corte duro. El plan está dimensionado para una persona.
- **Prioridad en conflicto:** responder comunidad > publicar > producir > diseñar.
- **Registro de decisiones:** una línea por semana en `MEDICION.md` (qué se probó, qué se decidió).
- **Banco de reserva:** mínimo 6 piezas listas siempre. Si baja de 3, se suspende la publicación y se produce.
- **Pausas:** una semana de silencio cada 6 semanas, anunciada. Es mejor que desaparecer sin avisar.
- **Criterio de cierre:** si a los 90 días la métrica norte no crece y la lectura comprometida es <45%, se replantea el canal, no el estudio.

---

## 15. Entregables de esta fase

| Archivo | Contenido |
| --- | --- |
| `comunicacion/PLAN_DIVULGACION.md` | Este plan |
| `comunicacion/CALENDARIO_90_DIAS.csv` | Calendario ejecutable con canales, UTMs y métricas |
| `comunicacion/PIEZAS_LISTAS.md` | 14 piezas redactadas y listas para publicar |
| `comunicacion/MEDICION.md` | Panel de métricas y registro de decisiones |

**Nada del estudio fue modificado.** No se tocaron `README.md`, `INFORME_TECNICO.md`, `analysis/`, `data/`, `presentation/` ni los scripts. Todo lo nuevo vive en `comunicacion/`, sin commit y sin publicar.
