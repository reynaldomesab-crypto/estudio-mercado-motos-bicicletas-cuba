# Arquitectura del Sistema

## Visión General

El proyecto sigue una arquitectura **modular por capas** con separación clara entre:
1. **Scraping** (extracción de datos)
2. **Procesamiento** (limpieza, clasificación, normalización)
3. **Curación** (datasets finales listos para análisis)
4. **Almacenamiento** (raw inmutable → curado → procesado)

## Flujo de Datos

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   FUENTES   │────▶│   SCRAPING   │────▶│  RAW DATA   │────▶│  CURATED     │
│  (4 fuentes)│     │  (11 scripts)│     │ (715 páginas)│    │  (5,914 reg) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                           │                    │                   │
                           ▼                    ▼                   ▼
                    ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
                    │  PROCESSING  │     │  VALIDACIÓN │     │  EXPORT      │
                    │ (3 processors)│     │ (calidad)   │     │ (JSON/CSV)   │
                    └──────────────┘     └─────────────┘     └──────────────┘
```

## Componentes Principales

### 1. Scrapers (`scripts/scrapers/`)

| Scraper | Fuente | Tecnología | Páginas | Registros |
|---------|--------|------------|---------|-----------|
| `scrape_revolico_vehiculos.py` | Revolico | GraphQL/Apollo + SSR | 109 | 4,347 |
| `scrape_revolico_repuestos.py` | Revolico | GraphQL/Apollo + SSR | - | - |
| `scrape_itencel_motos.py` | itencel | Nuxt.js SSR | 75 | 1,885 |
| `scrape_itencel_repuestos.py` | itencel | WordPress/SSR | - | - |
| `scrape_elyerro_motos.py` | ElYerro | Nuxt/Apollo | 100 | 88 |
| `scrape_elyerro_bicicletas.py` | ElYerro | Nuxt/Apollo | 14 | 134 |
| `scrape_elyerro_repuestos.py` | ElYerro | Nuxt/Apollo | 9 | 22 |
| `scrape_facebook.py` | Facebook | API-like parsing | 10 grupos | 1,427 posts |
| `scrape_facebook_repuestos.py` | Facebook | API-like parsing | 10 grupos | - |

### 2. Procesadores (`scripts/processors/`)

| Procesador | Entrada | Salida | Función |
|------------|---------|--------|---------|
| `process_facebook.py` | Raw FB posts | `facebook_curated.json` | Clasifica vehículos, extrae precio/ubicación/WhatsApp |
| `process_repuestos.py` | Raw parts | `spare_parts_curated.json` | Unifica repuestos de 5 fuentes, clasifica en 6 categorías |

### 3. Utilidades Compartidas (`scripts/utils/`)

| Módulo | Función |
|--------|---------|
| `base_scraper.py` | Clase base `BaseScraper` + `VehicleScraperMixin` |
| `currency_utils.py` | Normalización USD/CUP/ZELLE/EUR/MLC |
| `vehicle_classifier.py` | Clasificación 8 vehículos + 6 repuestos |

## Patrones de Diseño

### 1. Template Method (BaseScraper)
```python
class BaseScraper(ABC):
    def run(self):           # Template method
        for page in range(1, max_pages):
            html = self.fetch_page(page)
            listings = self.extract_listings_from_page(html)
            filtered = [l for l in listings if self.filter_listing(l)]
            self.save_page_data(page, html, filtered)
```

### 2. Strategy Pattern (Clasificación)
```python
class VehicleScraperMixin:
    VEHICLE_KEYWORDS = {...}
    
    def classify_vehicle_type(self, title: str) -> str:
        for category, keywords in self.VEHICLE_KEYWORDS.items():
            if any(kw in title.lower() for kw in keywords):
                return category
        return 'Otro'
```

### 3. Factory Pattern (Procesadores)
```python
def create_processor(source: str) -> BaseProcessor:
    processors = {
        'facebook': FacebookDataProcessor,
        'repuestos': SparePartsProcessor,
    }
    return processors[source]()
```

## Almacenamiento de Datos

### Estructura de Directorios
```
data/
├── raw/
│   ├── revolico/
│   │   └── revolico_vehiculos_20260919_200418/
│   │       ├── page_0001.html
│   │       ├── page_0001.html
│   │       ├── extracted_0001.json
│   │       ├── listings_carro.json
│   │       ├── listings_motos_bici.json
│   │       ├── listings_triciclo.json
│   │       └── manifest.json
│   ├── itencel/
│   │   └── itencel_motos_20260919_200418/
│   └── facebook/
│       └── facebook.json
├── curated/
│   ├── vehicles_curated.json     # 5,391 vehículos
│   ├── parts_curated.json        # 523 repuestos
│   ├── spare_parts_curated.json  # 523 repuestos
│   ├── facebook_curated.json     # 396 vehículos FB
│   └── itencel_motos_curated.json
└── processed/                    # Para ML/Analytics
```

### Formato Manifest (Lineage Tracking)
```json
{
  "source_id": "revolico_vehiculos_20260919_200418",
  "source_name": "revolico.com",
  "source_url": "https://www.revolico.com/search?category=vehiculos",
  "scraped_at": "2026-09-19T20:04:18",
  "scraper_version": "1.0",
  "pages": [...],
  "totals": {
    "pages_processed": 109,
    "listings_extracted": 4347,
    "listings_by_category": {"Motos_Bici": 4347}
  },
  "completed_at": "2026-09-19T21:30:00"
}
```

## Scrapers - Detalles Técnicos

### Revolico (GraphQL/Apollo)
- **Endpoint**: `https://www.revolico.com/search?category=vehiculos`
- **Datos**: `__NEXT_DATA__` → `props.pageProps.__APOLLO_STATE__`
- **Paginación**: `page=N` en query string
- **Rate limit**: 1.5s entre requests
- **Anti-bot**: Headers completos, User-Agent realista

### itencel (Nuxt.js SSR)
- **URLs**: `/anuncio-categoria/vehiculos/motos/`, `/anuncio-categoria/repuestos-accesorios/`
- **Datos**: `<script id="__NEXT_DATA__">` + `<script type="application/ld+json">`
- **Cards**: `<div class="rtcl-listing-card it-app listing-item rtcl-listing-item">`
- **Paginación**: `/page/N/`

### ElYerroMenu (Nuxt/Apollo)
- **URLs**: `/l/search/motor?type=2`, `/l/search/bicicleta?type=2`, `/l/search/repuestos`
- **Datos**: `<script type="application/json">` con Pinia state serializado
- **Referencias**: Índices numéricos resueltos recursivamente
- **Paginación**: `?page=N`

### Facebook Groups
- **Fuente**: Export JSON de grupos públicos
- **Estructura**: Posts con `text`, `sharedPost`, `attachments`, `textReferences`
- **WhatsApp**: Extraído de `textReferences.external_url` (wa.me)
- **Imágenes**: `attachments[].media.image.uri` + `sharedPost.attachments[]`

## Clasificación de Vehículos

### Jerarquía
```
Vehículo
├── Moto Combustión
├── Moto Eléctrica
├── Bicicleta
├── Bicicleta Eléctrica
├── Patinete Eléctrico
├── Mototrina
├── Carro (excluido del scope)
└── Otros
```

### Repuestos (6 categorías)
1. **Repuesto Moto** - Combustión
2. **Repuesto Bicicleta** - Tradicional
3. **Repuesto Moto Eléctrica** - Baterías, controladores, motores
4. **Repuesto Bicicleta Eléctrica** - Baterías, controladores, motores
5. **Repuesto Patinete** - Patinetes/hoverboards
5. **Repuesto Generico** - Sin clasificar

### Monedas Soportadas
| Código | Nombre | Tasa USD | Ejemplos |
|--------|--------|----------|----------|
| USD | Dólares | 1.0 | $100, USD 100 |
| CUP | Peso Cubano | 1/2400 | 240000 CUP |
| ZELLE | Zelle | 1.0 | Zelle 100 |
| EUR | Euro | 1.08 | €100 |
| MLC | Moneda Libre | 1.0 | MLC 100 |

## Pipeline de Calidad

### Filtros Aplicados
1. **Deduplicación**: `listing_id` + `source_id`
2. **Filtro alquiler**: Keywords `arriendo`, `alquiler`, `renta`, `mensual`
3. **Outliers precio**: IQR por categoría (min/max configurables)
4. **Partes/accesorios**: Excluye listings de solo piezas
5. **Vehículos completos**: Excluye repuestos sueltos
6. **Validación precio**: Rangos por categoría

### Métricas de Calidad
| Métrica | Vehículos | Repuestos |
|---------|-----------|-----------|
| Registros totales | 5,914 | 523 |
| Con precio | 5,339 (90.3%) | 489 (93.5%) |
| Con imagen | 5,487 (92.8%) | 523 (100%) |
| Con ubicación | 4,234 (71.6%) | 523 (100%) |
| Con WhatsApp | 1,245 (21.0%) | 50 (9.6%) |

## Escalabilidad y Mantenimiento

### Agregar Nueva Fuente
1. Crear scraper heredando `BaseScraper` + `VehicleScraperMixin`
2. Implementar `extract_listings_from_page()` y `filter_listing()`
3. Agregar `_get_page_params()` y `_get_page_url()`
4. Registrar en `scripts/scrapers/__init__.py`

### Agregar Nueva Categoría
1. Actualizar `VEHICLE_KEYWORDS` en `VehicleScraperMixin`
2. Actualizar `PART_CATEGORIES` en `SparePartsProcessor`
2. Agregar `PRICE_FILTERS` para nueva categoría
3. Actualizar `VEHICLE_CATEGORY_MAP` en `SparePartsProcessor`

### Monitoreo
- Logs estructurados por página
- Manifests con timestamps y contadores
- Rate limiting automático (1.5s default)
- Reintentos con backoff exponencial
EOF