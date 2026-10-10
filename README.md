# Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba

> Análisis de mercado de vehículos de dos ruedas y repuestos en Cuba mediante scraping de múltiples fuentes

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📋 Descripción

Este proyecto realiza un **estudio de mercado integral** del sector de vehículos de dos ruedas (motos, bicicletas, patinetes, triciclos) y sus repuestos en Cuba, mediante **web scraping** de múltiples fuentes de clasificados online cubanas.

### 📖 Documentos del proyecto

| Documento | Para qué sirve |
| --- | --- |
| [`JOURNEY.md`](JOURNEY.md) | Bitácora del proyecto por fechas: qué se hizo, qué se descubrió y qué se corrigió |
| [`docs/PROMPTS_DEL_USUARIO.md`](docs/PROMPTS_DEL_USUARIO.md) | Registro de los prompts del usuario, con captura automática |
| [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) | Arquitectura de datos y flujo de procesamiento |
| [`docs/GUIA_SCRAPING.md`](docs/GUIA_SCRAPING.md) | Guía para ejecutar y ampliar los scrapers |
| `analysis/` | Gráficos y reportes generados por el análisis |

### 🎯 Objetivos

- Recopilar datos de vehículos de dos ruedas (motos, bicicletas, patinetes, triciclos) y sus repuestos
- Analizar precios, distribución geográfica, marcas y tendencias
- Identificar oportunidades de mercado y segmentos desatendidos
- Crear un dataset estructurado y listo para análisis

---

## 📊 Resumen de Datos

| Métrica | Valor |
|---------|-------|
| **Total vehículos** | 5,391 |
| **Total repuestos** | 523 |
| **Páginas scrapeadas** | 715 |
| **Fuentes de datos** | 4 |
| **Cobertura de precios** | 93.2% |
| **Cobertura de imágenes** | 92.9% |
| **Precio promedio vehículos** | $1,536 USD |
| **Precio promedio repuestos** | $1,147 USD |

### 📈 Distribución por Tipo de Vehículo

| Tipo | Cantidad | Precio Promedio |
|------|----------|-----------------|
| Moto Combustión | 1,589 | $1,701 |
| Moto Eléctrica | 635 | $2,012 |
| Bicicleta | 589 | $229 |
| Bicicleta Eléctrica | 525 | $770 |
| Patinete Eléctrico | 92 | $625 |
| Mototrina | 5 | $1,101 |
| Otros | 194 | $1,472 |

### 🛠️ Repuestos por Categoría

| Categoría | Cantidad | Precio Promedio |
|-----------|----------|-----------------|
| Repuesto Moto | 273 | $1,147 |
| Repuesto Patinete | 25 | $625 |
| Repuesto Moto Eléctrica | 4 | $1,321 |
| Repuesto Bicicleta | 10 | $229 |
| Repuesto Bicicleta Eléctrica | 4 | $770 |
| Repuesto Generico | 211 | $1,472 |

---

## 🔍 Fuentes de Datos

| Fuente | Tipo | Vehículos | Repuestos | Páginas |
|--------|------|-----------|-----------|---------|
| **Revolico.com** | Clasificados | 4,347 | - | 109 |
| **itencel.com** | Marketplace | 3,792 | 1,885 | 224 |
| **ElYerroMenu.com** | Marketplace | 244 | - | 114 |
| **Facebook Groups** | Grupos sociales | 396 | - | 10 grupos |

---

## 🏗️ Arquitectura del Proyecto

```
motos_bicis_project/
├── data/
│   ├── raw/                    # Datos raw inmutables (715 páginas)
│   │   ├── revolico/
│   │   ├── elyerro_motos/
│   │   ├── elyerro_bicicletas/
│   │   ├── facebook/
│   │   └── itencel/
│   ├── curated/                # Datos limpios y clasificados
│   │   ├── vehicles_curated.json    (5,391 vehículos)
│   │   ├── parts_curated.json       (523 repuestos)
│   │   ├── facebook_curated.json    (396 vehículos FB)
│   │   ├── itencel_motos_curated.json
│   │   └── spare_parts_curated.json (523 repuestos)
│   └── processed/              # Datasets listos para análisis/ML
├── scripts/
│   ├── scrapers/               # 11 scrapers
│   │   ├── scrape_revolico_vehiculos.py
│   │   ├── scrape_revolico_repuestos.py
│   │   ├── scrape_itencel_motos.py
│   │   ├── scrape_itencel_repuestos.py
│   │   ├── scrape_elyerro_motos.py
│   │   ├── scrape_elyerro_bicicletas.py
│   │   ├── scrape_elyerro_repuestos.py
│   │   ├── scrape_facebook.py
│   │   ├── scrape_facebook_repuestos.py
│   │   └── scrape_itencel_repuestos.py
│   ├── processors/
│   │   ├── process_facebook.py
│   │   └── process_repuestos.py
│   └── utils/
│       ├── base_scraper.py      # Clase base para scrapers
│       ├── vehicle_classifier.py # Clasificación de vehículos
│       └── currency_utils.py    # Normalización de monedas
├── docs/                        # Documentación
└── tests/                       # Pruebas unitarias
```

---

## 🚀 Instalación y Uso

### Requisitos

- Python 3.10+
- Dependencias: `urllib`, `json`, `re`, `pathlib` (solo librería estándar)

### Instalación

```bash
git clone https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba.git
cd estudio-mercado-motos-bicicletas-cuba
```

### Ejecutar Scrapers

```bash
# Scrapers de vehículos
python scripts/scrapers/scrape_revolico_vehiculos.py
python scripts/scrapers/scrape_itencel_motos.py
python scripts/scrapers/scrape_elyerro_motos.py
python scripts/scrapers/scrape_elyerro_bicicletas.py

# Scrapers de repuestos
python scripts/scrapers/scrape_itencel_repuestos.py
python scripts/scrapers/scrape_elyerro_repuestos.py
python scripts/scrapers/scrape_facebook_repuestos.py

# Scraper de Facebook (requiere datos pre-scrapeados)
python scripts/scrapers/scrape_facebook.py
```

### Procesar Datos

```bash
# Procesar Facebook
python scripts/processors/process_facebook.py

# Procesar repuestos (todos las fuentes)
python scripts/processors/process_repuestos.py
```

### Acceder a Datos Curados

```python
import json

# Vehículos (5,391 items)
with open('data/curated/vehicles_curated.json') as f:
    vehicles = json.load(f)['items']

# Repuestos (523 items)
with open('data/curated/parts_curated.json') as f:
    parts = json.load(f)['items']

# Ejemplo: Filtrar motos eléctricas bajo $2000
motos_electricas_baratas = [
    v for v in vehicles 
    if v['vehicle_type'] == 'Moto Eléctrica' and v.get('price_usd', 0) < 2000
]
```

---

## 🔧 Características Técnicas

### ✅ Scraping Robusto
- **HTML parsing** con regex optimizado (sin Selenium)
- **GraphQL/Apollo parsing** para sitios modernos (Revolico, ElYerro)
- **Nuxt.js SSR parsing** para itencel
- **Facebook Graph API-like** parsing para grupos

### ✅ Procesamiento Inteligente
- **Clasificación automática** de 8 tipos de vehículos + 6 tipos de repuestos
- **Filtrado inteligente**: excluye alquileres, piezas sueltas, vehículos completos
- **Normalización de moneda**: USD, CUP, ZELLE, EUR, MLC → USD
- **Detección de ubicación**: 16 provincias + 168 municipios de Cuba
- **Extracción de WhatsUp/Contacto** desde posts de Facebook

### ✅ Calidad de Datos
- **Raw inmutable**: HTML y JSON originales preservados con manifests
- **Lineage tracking**: Cada registro tracable a su fuente original
- **Deduplicación**: Por ID de listing + fuente
- **Validación de precios**: Rangos por categoría, detección de outliers
- **Cobertura de precios**: 93.2%

### ✅ Arquitectura Escalable
- **BaseScraper abstracto**: Extensible para nuevas fuentes
- **Mixin VehicleScraperMixin**: Lógica de clasificación reutilizable
- **Procesadores modulares**: Separación scraping vs procesamiento
- **Manifests JSON**: Lineage completo por source_id

---

## 📊 Ejemplos de Análisis

### Precios por Marca (Top 10)

```python
import pandas as pd

df = pd.DataFrame(vehicles)
top_brands = df.groupby('brand')['price_usd'].agg(['mean', 'count', 'min', 'max']).sort_values('count', ascending=False).head(10)
```

### Distribución Geográfica

```python
# Top provincias
province_dist = df['province_name'].value_counts().head(10)
```

### Tendencias de Precio

```python
# Precio vs Año (si disponible)
# Precio vs Kilometraje (motos)
# Precio vs Estado (nuevo/usado)
```

---

## 🛡️ Consideraciones Éticas y Legales

- ✅ **Solo datos públicos**: Solo información visible públicamente
- ✅ **Rate limiting**: 1.5s entre requests, respeta robots.txt
- ✅ **User-Agent realista**: Identificación transparente
- ✅ **Sin datos personales**: No se almacenan datos privados de usuarios
- ✅ **Uso educativo/investigación**: Análisis de mercado académico
- ⚠️ **Responsabilidad**: Verificar TOS de cada sitio antes de uso comercial

---

## 📁 Datasets Disponibles

| Archivo | Registros | Descripción |
|---------|-----------|-------------|
| `vehicles_curated.json` | 5,391 | Vehículos unificados |
| `parts_curated.json` | 523 | Repuestos clasificados |
| `spare_parts_curated.json` | 523 | Solo repuestos |
| `vehicles_curated.json` | 5,391 | Vehículos unificados |

### Estructura de Registro (Vehículo)
```json
{
  "source": "revolico",
  "source_url": "https://www.revolico.com/item/...",
  "listing_id": "57552196",
  "title": "Moto Eléctrica BEVOMECON🇮🇱",
  "price_usd": 630,
  "currency": "USD",
  "location": "Plaza, La Habana",
  "province": "La Habana",
  "municipality": "Plaza",
  "vehicle_type": "Bicicleta Eléctrica",
  "brand": "BEVOMECON",
  "price_usd": 630,
  "images_count": 1,
  "location": "Plaza, La Habana",
  "updated_at": "2026-09-19T23:58:59.489Z",
  "scraped_at": "2026-09-19T20:04:21.057940"
}
```

### Registro de Repuesto
```json
{
  "source": "itencel",
  "title": "Kit Cilindro Pistón 70cc CG200",
  "price_usd": 45.0,
  "part_category": "Repuesto Moto",
  "vehicle_category": "Moto Combustión",
  "compatible_models": ["CG200", "CG150"],
  "brand": "TOPMAQ",
  "condition": "nuevo",
  "description": "Kit cilindro pistón 70cc para CG200..."
}
```

---

## 🛠️ Desarrollo

### Agregar Nuevo Scraper

```python
from scripts.utils.base_scraper import BaseScraper, VehicleScraperMixin

class MiNuevoScraper(BaseScraper, VehicleScraperMixin):
    BASE_URL = "https://ejemplo.com/buscar"
    CATEGORY_HINT = "motos"
    
    def _get_page_params(self, page: int) -> Dict:
        return {"page": page, "categoria": "motos"}
    
    def extract_listings_from_page(self, html: str) -> List[Dict]:
        # Implementar parsing específico
        pass
    
    def filter_listing(self, listing: Dict) -> bool:
        return self.filter_listing(listing)
```

### Ejecutar Tests

```bash
python -m pytest tests/ -v
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea rama feature (`git checkout -b feature/nueva-fuente`)
3. Commit cambios (`git commit -am 'Agregar scraper XYZ'`)
4. Push a la rama (`git push origin feature/nueva-fuente`)
5. Abre Pull Request

### Guías de Estilo
- Código en inglés, documentación en español
- Type hints obligatorios
- Docstrings en español
- Rate limiting: mínimo 1.5s entre requests

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- **Revolico.com** - Principal clasificados de Cuba
- **itencel.com** - Marketplace cubano
- **ElYerroMenu.com** - Marketplace cubano
- **Grupos de Facebook** - Comunidad de vendedores/compradores
- Comunidad Python - Herramientas de scraping

---

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba/discussions)

---

<div align="center">

**⭐ Si este proyecto te es útil, dale una estrella!**

Hecho con ❤️ para la comunidad de desarrolladores e investigadores de mercado en Cuba

</div>
EOF