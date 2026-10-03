# Guía de Contribución

## 🤝 Cómo Contribuir

¡Gracias por tu interés en contribuir! Este proyecto busca mejorar el entendimiento del mercado de vehículos de dos ruedas en Cuba.

## 🚀 Primeros Pasos

1. **Fork** el repositorio
2. **Clona** tu fork: `git clone https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba.git`
3. **Crea rama**: `git checkout -b feature/nueva-funcionalidad`
4. **Desarrolla** tu mejora
4. **Testea**: `python -m pytest tests/ -v`
5. **Commit**: `git commit -am 'feat: descripción clara'`
5. **Push**: `git push origin feature/nueva-funcionalidad`
6. **Pull Request**: Abre PR con descripción clara

## 📋 Tipos de Contribuciones Bienvenidas

### 🔧 Nuevos Scrapers
- Nuevas fuentes de datos (sitios de clasificados, marketplaces)
- Mejoras a scrapers existentes (paginación, anti-bot, nuevos campos)
- Soporte para nuevas categorías de vehículos

### 🧠 Mejoras de Clasificación
- Nuevas palabras clave para vehículos/partes
- Mejor detección de alquileres vs venta
- Clasificación de condiciones (nuevo/usado/reacondicionado)
- Detección de marcas/modelos específicos

### 📊 Procesamiento y Análisis
- Nuevas métricas de calidad de datos
- Análisis de tendencias temporales
- Detección de anomalías/outliers
- Enriquecimiento de datos (geocoding, marcas)

### 📚 Documentación
- README en otros idiomas
- Tutoriales de uso
- Documentación de API
- Guías de deployment

### 🐛 Correcciones
- Bug fixes en scrapers
- Mejoras de robustez (anti-bot, rate limiting)
- Correcciones de parsing
- Mejoras de performance

## 🛠️ Configuración de Desarrollo

```bash
# Clonar y configurar
git clone https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba.git
cd estudio-mercado-motos-bicicletas-cuba

# Entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependencias de desarrollo
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install
```

### Estándares de Código

```bash
# Formateo
black scripts/ --line-length 100

# Linting
flake8 scripts/ --max-line-length=100

# Type checking
mypy scripts/ --strict

# Tests
pytest tests/ -v --cov=scripts --cov-report=html
```

### Estilo de Código

- **Type hints obligatorios** en funciones públicas
- **Docstrings en español** (Google style)
- **Type hints** en todos los parámetros y returns
- **Manejo de errores** explícito (try/except específicos)
- **Logging** en lugar de print (excepto en scripts CLI)

## 📝 Convenciones de Commit

### Formato
```
<tipo>: <descripción corta>

[cuerpo opcional con detalles]

[refs #issue]
```

### Tipos
| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Refactorización sin cambio funcional |
| `docs` | Cambios en documentación |
| `test` | Agregar/modificar tests |
| `chore` | Mantenimiento, dependencias, configs |
| `perf` | Mejora de performance |
| `style` | Formato, linting, sin cambio lógico |

### Ejemplos
```
feat: agregar scraper para nueva fuente "Clasificados Cuba"

fix: corregir parsing de precios en CUP en itencel

refactor: extraer lógica de clasificación a vehicle_classifier.py

docs: actualizar README con nuevos scrapers

test: agregar tests unitarios para currency_utils

chore: actualizar dependencias de desarrollo
```

## 🧪 Testing

### Estructura de Tests
```
tests/
├── unit/
│   ├── test_currency_utils.py
│   ├── test_vehicle_classifier.py
│   └── test_base_scraper.py
├── integration/
│   ├── test_scrapers.py
│   └── test_processors.py
└── fixtures/
    ├── sample_html/
    └── sample_json/
```

### Ejecutar Tests
```bash
# Todos los tests
pytest tests/ -v

# Solo unitarios
pytest tests/unit/ -v

# Con cobertura
pytest tests/ --cov=scripts --cov-report=html

# Solo tests de scrapers (requiere internet)
pytest tests/integration/test_scrapers.py -v -k "not slow"
```

### Escribir Tests
```python
# tests/unit/test_currency_utils.py
import pytest
from scripts.utils.currency_utils import extract_price_and_currency, convert_to_usd

def test_extract_usd():
    result = extract_price_and_currency("Precio: $1,500 USD")
    assert result == {'price': 1500.0, 'currency': 'USD'}

def test_extract_cup():
    result = extract_price_and_currency("Precio: 50000 CUP")
    assert result == {'price': 50000.0, 'currency': 'CUP'}

def test_convert_to_usd():
    assert convert_to_usd(24000, 'CUP') == 10.0
    assert convert_to_usd(100, 'USD') == 100.0
```

## 📦 Estructura de Commits

### Formato
```
<tipo>: <descripción en minúsculas, imperativo>

[cuerpo opcional explicando qué y por qué]

[Refs: #número-issue]
```

### Tipos
| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Bug fix |
| `refactor` | Refactoring sin cambio funcional |
| `docs` | Documentación |
| `test` | Tests |
| `chore` | Mantenimiento, deps, config |
| `perf` | Performance |
| `style` | Formato, linting |
| `ci` | CI/CD |

### Ejemplos
```
feat: agregar scraper para nueva fuente "Clasificados Cuba"

fix: corregir parsing de precios CUP en itencel

refactor: extraer lógica de clasificación a vehicle_classifier.py

docs: actualizar README con nuevos scrapers

test: agregar tests unitarios para currency_utils

chore: actualizar dependencias de desarrollo
```

## 🔍 Code Review Checklist

### Autor
- [ ] Tests pasan (`pytest tests/ -v`)
- [ ] Linting pasa (`flake8 scripts/`)
- [ ] Types OK (`mypy scripts/`)
- [ ] Formato correcto (`black scripts/`)
- [ ] Docs actualizadas si aplica
- [ ] Tests para nueva funcionalidad

### Revisor
- [ ] Lógica correcta
- [ ] Manejo de errores apropiado
- [ ] No rompe funcionalidad existente
- [ ] Código legible y mantenible
- [ ] Tests cubren casos edge
- [ ] Documentación actualizada

## 📦 Release Process

### Versionado (SemVer)
```
MAJOR.MINOR.PATCH
- MAJOR: Cambios incompatibles API
- MINOR: Nueva funcionalidad compatible
- PATCH: Bug fixes compatibles
```

### Proceso Release
1. Actualizar `VERSION` en `pyproject.toml`/`setup.py`
2. `git tag -a v1.2.3 -m "Release v1.2.3"`
3. `git push origin v1.2.3`
4. GitHub Actions crea release automático
4. Actualizar CHANGELOG.md

## 🏷️ Labels de Issues/PRs

| Label | Descripción |
|-------|-------------|
| `good first issue` | Ideal para principiantes |
| `help wanted` | Se necesita ayuda |
| `bug` | Bug confirmado |
| `enhancement` | Mejora/feature request |
| `documentation` | Documentación |
| `scraper` | Relacionado con scrapers |
| `processor` | Relacionado con procesadores |
| `breaking change` | Cambio incompatible |

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/estudio-mercado-motos-bicicletas-cuba/discussions)
- **Email**: proyecto@ejemplo.com

---

**¡Gracias por contribuir! 🎉**
EOF