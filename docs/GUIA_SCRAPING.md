# Guía de Scraping

## Reglas Básicas

### ✅ Hacer
- Usar `User-Agent` realista y identificativo
- Respetar `robots.txt` y `crawl-delay`
- Rate limiting mínimo 1.5s entre requests
- Manejar errores HTTP (429, 503) con backoff exponencial
- Preservar HTML raw + JSON extraído
- Documentar selectores CSS/XPath usados

### ❌ No Hacer
- Scraping agresivo (requests paralelos masivos)
- Ignorar códigos de estado HTTP
- Hardcodear valores que cambian (IDs, tokens)
- Almacenar datos personales sensibles (teléfonos, nombres, URLs de anuncio) sin seudonimizar
- Scrapear detrás de login sin autorización
- Publicar datos identificativos de personas sin anonimización previa

> **Marco normativo:** el tratamiento de datos personales se ajusta a la **Ley 149/2022 de Protección de Datos Personales** (GOC-2022-832-O90). Los datos se obtienen de fuentes de acceso público (Art. 17.e) y se disocian antes de su publicación (Art. 17.f), aplicando los principios del Art. 10 (limitación de recogida, calidad, especificación de fines, limitación de uso, legitimación, seguridad, transparencia, participación individual, responsabilidad y legalidad). Antes de versionar cualquier conjunto, ejecutar `scripts/privacy/sanitizar_datos.py` para eliminar identificadores directos.

## Patrones Comunes

### 1. Extracción de `__NEXT_DATA__` (Next.js)
```python
def parse_next_data(self, html: str) -> Optional[Dict]:
    match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return None
```

### 2. Extracción de JSON-LD (Schema.org)
```python
ld_json = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
for ld in ld_json:
    data = json.loads(ld)
    # Procesar @graph
```

### 3. Resolución de Referencias Pinia (Nuxt/ElYerro)
```python
def resolve_references(self, data: List) -> Dict[int, Any]:
    resolved = {}
    def resolve(idx, visited=None):
        if visited is None: visited = set()
        if idx in visited: return f"<circular:{idx}>"
        if idx >= len(data): return f"<oob:{idx}>"
        visited.add(idx)
        val = data[idx]
        if isinstance(val, (str, int, float, bool)) or val is None:
            return val
        elif isinstance(val, list):
            return [resolve(i, visited.copy()) for i in val]
        elif isinstance(val, dict):
            return {k: resolve(v, visited.copy()) for k, v in val.items()}
        return val
    
    for i in range(len(data)):
        resolved[i] = resolve(i)
    return resolved
```

### 4. Paginación Genérica
```python
def _get_page_params(self, page: int) -> Dict:
    if page == 1:
        return {}
    return {"page": page}

def _get_page_url(self, page: int) -> str:
    if page == 1:
        return self.BASE_URL
    return f"{self.BASE_URL}page/{page}/"
```

## Anti-Bot Evasion

### Headers Recomendados
```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}
```

### Rate Limiting Inteligente
```python
async def fetch_with_backoff(self, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=self.HEADERS) as resp:
                if resp.status == 429:
                    wait = 2 ** attempt * 5  # 5s, 10s, 20s
                    await asyncio.sleep(wait)
                    continue
                elif resp.status >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return await resp.text()
        except asyncio.TimeoutError:
            await asyncio.sleep(2 ** attempt)
    return None
```

## Manejo de Anti-Bot

### Detección Común
- **403 Forbidden**: Headers insuficientes, IP bloqueada
- **429 Too Many Requests**: Rate limit excedido
- **503 Service Unavailable**: Protección anti-bot activa
- **Challenge/Cloudflare**: JavaScript challenge requerido

### Estrategias de Mitigación
1. **Headers completos** (ver arriba)
2. **Session persistence** (cookies, session)
3. **Rotación de User-Agents** (pool de 10+)
3. **Delays aleatorios** (1-3s + jitter)
4. **Retry con backoff exponencial** (2^attempt * base)
4. **Sesiones persistentes** (cookies, localStorage)
4. **Evitar horas pico** (madrugada mejor)

## Selectores Comunes

### Revolico (Apollo/GraphQL)
```python
# __NEXT_DATA__ -> props.pageProps.__APOLLO_STATE__
# Ads en: apollo['Query'].adsPerPage({...}).edges[].node
```

### itencel (Nuxt.js)
```python
# __NEXT_DATA__ -> props.pageProps.__APOLLO_STATE__
# Cards: div.rtcl-listing-card.it-app.listing-item.rtcl-listing-item
# Título: h3.listing-title > a
# Precio: bdi > span.rtcl-price-currencySymbol
```

### ElYerro (Nuxt + Pinia)
```python
# <script type="application/json"> con Pinia state serializado
# Referencias numéricas resueltas recursivamente
# Cards: div.rtcl-listing-card.it-app.listing-item
```

### Facebook Groups
```python
# Export JSON con estructura:
# {text, sharedPost, attachments[], textReferences[], time, user, groupTitle}
# WhatsApp en textReferences[].external_url (wa.me)
```

## Validación de Datos

### Checklist Pre-Commit
- [ ] HTML raw guardado
- [ ] JSON extraído válido
- [ ] Manifest generado con counts
- [ ] Deduplicación por ID
- [ ] Precio en rango válido
- [ ] Moneda normalizada a USD
- [ ] Ubicación parseada (provincia/municipio)
- [ ] Clasificación de vehículo
- [ ] Exclusión de alquileres/partes

### Métricas de Calidad Mínimas
- Cobertura precio > 80%
- Cobertura imágenes > 70%
- Cobertura ubicación > 60%
- Deduplicación > 95%
- Filtro alquiler > 90%
EOF