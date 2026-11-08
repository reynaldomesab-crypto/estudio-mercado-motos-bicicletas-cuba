# Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba

> Análisis de mercado de vehículos de dos ruedas y repuestos en Cuba mediante scraping de múltiples fuentes

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## ▶ Lee el estudio en línea

**[reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba](https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/)**

Resumen de 3 minutos · [Calculadora de precio](https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/precios.html) · [Guía para vendedores](https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/guia.html) · [Dataset](https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/datos.html)

**4.979 anuncios únicos · 4.860 vehículos clasificados · 4 fuentes · 13 figuras.**

## 📋 Descripción

Este proyecto realiza un **estudio de mercado integral** del sector de vehículos de dos ruedas (motos, bicicletas, patinetes, triciclos) y sus repuestos en Cuba, mediante **web scraping** de múltiples fuentes de clasificados online cubanas.

### 📖 Documentos del proyecto

| Documento | Para qué sirve |
| --- | --- |
| [`docs/index.html`](docs/index.html) | **Sitio publicado en GitHub Pages**: resumen, calculadora, guía y dataset |
| [Campaña de comunicación](https://github.com/reynaldomesab-crypto/campana-mercado-motos-bicicletas-cuba) | Plan, evidencia y calendario de la campaña (repositorio aparte) |
| [`INFORME_TECNICO.md`](INFORME_TECNICO.md) | Informe técnico completo: decisiones, errores y correcciones |
| [`presentation/index.html`](presentation/index.html) | Presentación de 14 diapositivas sobre buenas prácticas para vendedores. Un solo archivo, funciona sin internet |
| [`analysis/INFORME_PRESENTACION.md`](analysis/INFORME_PRESENTACION.md) | Guion de la presentación, preguntas frecuentes y material de respaldo |
| [`analysis/GUIA_VENDEDOR.md`](analysis/GUIA_VENDEDOR.md) | Guía de buenas prácticas para vendedores del sector, con las cifras que la sostienen |
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

**Cifras tras deduplicar por URL** (el conteo bruto de 5.787 estaba inflado; ver `JOURNEY.md`):

| Métrica | Valor |
|---------|-------|
| **Anuncios únicos** | 4.979 |
| **Vehículos clasificados** | 4.860 (97,6%) |
| **Páginas scrapeadas** | 715 |
| **Fuentes de datos** | 4 |
| **Con precio declarado** | 93,9% |
| **Con municipio** | 91,2% |
| **Con marca** | 54,5% |
| **Mediana de precio (vehículos)** | $1.610 USD |
| **Con WhatsApp** | 59,9% |

### 📈 Distribución por Tipo de Vehículo

| Tipo | Cantidad | Mediana de precio |
|------|----------|-------------------|
| Motores (combustión) | 1.272 | $2.000 |
| Eléctricos | 3.006 | $1.600 |
| Bicicletas | 518 | $160 |
| Patinetes eléctricos | 64 | $750 |
| Otros (sin señal de tipo) | 99 | — |
| Partes y accesorios | 20 | — |

### 🛠️ Repuestos

El archivo de repuestos tiene 523 registros, pero tras deduplicar quedan **260 anuncios únicos**, y de esos **130 vendían vehículos completos** mal archivados. El mercado real de repuestos es más pequeño de lo que parece y está desatendido. Detalle en `analysis/INFORME_FINAL.html` §8.2.

---

## 🔍 Fuentes de Datos

| Fuente | Tipo | Vehículos | Páginas |
|--------|------|-----------|---------|
| **Revolico.com** | Clasificados | 2.662 | 109 |
| **itencel.com** | Marketplace | 1.711 | 224 |
| **ElYerroMenu.com** | Marketplace | 210 | 114 |
| **Facebook Groups** | Grupos sociales | 396 | 10 grupos |

*Total: 4.979 anuncios únicos. La tabla anterior de esta sección sumaba 8.779 porque contaba registros repetidos entre archivos; las cifras de esta tabla son las deduplicadas.*

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
│   │   ├── vehicles_curated.json    (5.391 registros; 4.979 tras deduplicar)
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
git clone https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba.git
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

# Vehículos (5.391 registros; 4.979 tras deduplicar)
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

- ✅ **Solo datos públicos**: Solo información visible públicamente en clasificados
- ✅ **Rate limiting**: 1.5s entre requests, respeta robots.txt
- ✅ **User-Agent realista**: Identificación transparente
- ✅ **Anonimización antes de publicar**: teléfonos y URLs seudonimizados (hash SHA-256) en `data/publico/`; el CSV con datos identificativos queda fuera del repositorio (`.gitignore`)
- ✅ **Minimización**: solo se conservan campos necesarios para el análisis (categoría, marca, precio, provincia, municipio)
- ✅ **Uso educativo/investigación**: Análisis de mercado académico, sin fines comerciales
- ⚠️ **Cumplimiento normativo**: tratado conforme a la **Ley 149/2022 de Protección de Datos Personales** (GOC-2022-832-O90), principios del Art. 10, y bases del Art. 17.e (fuentes de acceso público) y 17.f (disociación de datos)
- ⚠️ **Derechos del titular**: acceso, rectificación, cancelación y oposición (Arts. 20-22) y oposición (Art. 23). Solicitudes por escrito al responsable del fichero: estudio-mercado@proyecto.local (plazo 10 días hábiles, Art. 29)
- ⚠️ **Responsabilidad**: Verificar TOS de cada sitio antes de uso comercial

---

## 📁 Datasets Disponibles

| Archivo | Registros | Descripción |
|---------|-----------|-------------|
| `vehicles_curated.json` | 5.391 | Vehículos unificados (4.979 tras deduplicar por URL) |
| `parts_curated.json` | 523 | Repuestos clasificados (260 únicos) |
| `spare_parts_curated.json` | 523 | Solo repuestos |
| `data/publico/vehiculos_clasificados.csv` | 4.979 | Versión pública anonimizada |

### Estructura de Registro (Vehículo)
```json
{
  "title": "Moto Eléctrica AVA 100 km seminueva",
  "source": "revolico",
  "categoria": "Eléctricos",
  "marca_detectada": "AVA",
  "price_usd": 1650,
  "currency": "USD",
  "province_name": "La Habana",
  "municipality_name": "Centro Habana",
  "tiene_whatsapp": true,
  "anuncio_id": "9f2c…",
  "telefono_id": "4a71…"
}
```

*El dataset público no contiene nombres, teléfonos ni URLs de anuncio: los identificadores están seudonimizados con SHA-256 (Ley 149/2022).*

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

- **Issues**: [GitHub Issues](https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/discussions)

---

<div align="center">

**⭐ Si este proyecto te es útil, dale una estrella!**

Hecho con ❤️ para la comunidad de desarrolladores e investigadores de mercado en Cuba

</div>
