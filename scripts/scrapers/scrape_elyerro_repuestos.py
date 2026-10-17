#!/usr/bin/env python3
"""
ElYerroMenu Repuestos Scraper
Extracts spare parts from elyerromenu.com
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter

RAIZ = Path(__file__).resolve().parents[2]

ssl._create_default_https_context = ssl._create_unverified_context


class ElYerroRepuestosScraper:
    BASE_URL = "https://elyerromenu.com/l/search/repuestos"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Category keywords for spare parts
    PART_CATEGORIES = {
        'Repuesto Moto': ['moto ', 'motorina', 'motoneta', 'scooter', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno moto', 'cadena moto'],
        'Repuesto Bicicleta': ['bicicleta ', 'bici ', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici', 'cambio bici', 'desviador', 'freno bici', 'manillar'],
        'Repuesto Moto Eléctrica': ['batería moto', 'bateria moto', 'cargador moto', 'controlador moto', 'motor eléctrico moto', 'batería litio moto'],
        'Repuesto Bicicleta Eléctrica': ['batería bici', 'bateria bici', 'cargador bici', 'controlador bici', 'motor eléctrico bici', 'batería litio bici'],
        'Repuesto Patinete': ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard'],
    }

    # Exclude complete vehicles
    EXCLUDE_KEYWORDS = [
        'triciclo', 'triciclos', 'mototrina', 'mototrin',
        'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
        'bicicleta ', 'bicicletas ', 'bici ', ' ebike', 'e-bike', 'e bike',
        'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
        'patinete', 'patinetes', 'scooter eléctrico', 'hoverboard', 'monociclo',
        'carro', 'auto', 'automovil', 'automóvil',
        'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
        'motoneta', 'motonetas', 'scooter', 'scooters',
        'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
    ]

    # Price filters (USD)
    PRICE_FILTERS = {
        'Repuesto Moto': {'min': 1, 'max': 3000},
        'Repuesto Bicicleta': {'min': 1, 'max': 2000},
        'Repuesto Moto Eléctrica': {'min': 1, 'max': 2000},
        'Repuesto Bicicleta Eléctrica': {'min': 1, 'max': 2000},
        'Repuesto Patinete': {'min': 1, 'max': 1000},
        'Repuesto Generico': {'min': 1, 'max': 1000},
    }

    def __init__(self, output_base: str = str(RAIZ), max_pages: int = 50):
        self.output_base = Path(str(RAIZ))
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"elyerro_repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "elyerromenu.com",
            "source_url": self.BASE_URL,
            "category_hint": "repuestos",
            "scraped_at": self.session_start,
            "scraper_version": "1.0",
            "pages": [],
            "totals": {"pages_processed": 0, "listings_extracted": 0, "listings_by_category": defaultdict(int)}
        }
        self.seen_listing_ids: Set[str] = set()
        self.all_listings: List[Dict] = []

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = {"page": page}
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    print(f"Page {page}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Page {page}: Error - {e}")
            return None

    def parse_nuxt_data(self, html: str) -> Optional[Dict]:
        json_islands = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not json_islands:
            return None
        try:
            return json.loads(json_islands[0])
        except json.JSONDecodeError:
            return None

    def resolve_references(self, data: List) -> Dict[int, Any]:
        """Resolve all numeric references in the serialized data."""
        resolved = {}
        
        def resolve(idx: int, visited: Set[int] = None) -> Any:
            if visited is None:
                visited = set()
            if idx in visited:
                return f"<circular:{idx}>"
            if idx >= len(data):
                return f"<oob:{idx}>"
            visited.add(idx)
            val = data[idx]
            if isinstance(val, (str, int, float, bool)) or val is None:
                return val
            elif isinstance(val, list):
                result = []
                for i in val:
                    if isinstance(i, int):
                        result.append(resolve(i, visited.copy()))
                    else:
                        result.append(i)
                return result
            elif isinstance(val, dict):
                result = {}
                for k, v in val.items():
                    if isinstance(v, int):
                        result[k] = resolve(v, visited.copy())
                    else:
                        result[k] = v
                return result
            return val
        
        for i in range(len(data)):
            resolved[i] = resolve(i)
        
        return resolved

    def extract_products(self, data: List, resolved: Dict[int, Any]) -> List[Dict]:
        products = []
        
        for i, item in enumerate(data):
            if isinstance(item, dict) and 'ref' in item and 'name' in item and 'price' in item:
                product = {}
                for key, ref_idx in item.items():
                    if isinstance(ref_idx, int):
                        product[key] = resolved.get(ref_idx, f"<unresolved:{ref_idx}>")
                    elif isinstance(ref_idx, list):
                        product[key] = [resolved.get(idx, f"<unresolved:{idx}>") for idx in ref_idx]
                    else:
                        product[key] = ref_idx
                products.append(product)
        
        return products

    def _is_repuesto(self, title: str) -> bool:
        """Check if listing is a spare part (not a complete vehicle)."""
        title_lower = title.lower()
        
        # Exclude complete vehicles
        exclude = ['triciclo', 'bicicleta ', 'moto ', 'motorina', 'motoneta', 'scooter', 'patinete', 'triciclo']
        for kw in ['triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad']:
            if kw in title_lower:
                return False
        
        # Check for part keywords
        part_keywords = [
            'repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
            'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
            'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
            'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
            'batería', 'bateria', 'controlador', 'motor eléctrico',
            'extensor de rango', 'extensor de rango',
            'aro ', 'llanta', 'cadena bici', 'piñon', 'cambio', 'desviador',
            'freno', 'pastilla', 'disco', 'manillar', 'sillin', 'pedal',
            'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
            'cargador ', 'cargador de', 'cargador para',
            'batería ', 'bateria ', 'batería de', 'bateria de',
            'extensor de rango', 'extensor de rango',
        ]
        
        title_lower = title.lower()
        # Must contain at least one part keyword
        has_part_keyword = any(kw in title_lower for kw in [
            'repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
            'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
            'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
            'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
            'batería', 'bateria', 'controlador', 'motor eléctrico',
            'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
            'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
        ])
        
        return has_part_keyword

    def filter_listing(self, listing: Dict) -> bool:
        title = listing.get('name', '')
        
        # Must be a spare part
        if not self._is_repuesto(listing.get('name', '')):
            return False
        
        # Price validation
        price = listing.get('price')
        currency = listing.get('currency', 'USD')
        price_usd = price if currency == 'USD' else (price * 0.024 if price else None)
        
        if price_usd is None:
            return False
        
        if price_usd < 1 or price_usd > 5000:
            return False
        
        return True

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = {"page": page}
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    print(f"Page {page}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Page {page}: Error - {e}")
            return None

    def parse_nuxt_data(self, html: str) -> Optional[List]:
        json_islands = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not json_islands:
            return None
        try:
            return json.loads(json_islands[0])
        except json.JSONDecodeError:
            return None

    def process_page_data(self, html: str) -> List[Dict]:
        data = self.parse_nuxt_data(html)
        if not data:
            return []
        
        resolved = self.resolve_references(data)
        products = self.extract_products(data, resolved)
        
        filtered = []
        for product in products:
            title = product.get('name', '')
            price = product.get('price')
            currency = product.get('currency', 'USD')
            location = product.get('locName', '')
            store = product.get('store', '')
            url_slug = product.get('slug', '')
            image = product.get('imageUri', '')
            
            if not title or not self._is_repuesto(title):
                continue
            
            price_usd = price if currency == 'USD' else (price * 0.024 if price else None)
            if price_usd is None or price_usd < 1 or price_usd > 5000:
                continue
            
            listing = {
                'source': 'elyerromenu',
                'source_id': self.source_id,
                'source_url': f"https://elyerromenu.com/l/{url_slug}",
                'listing_id': product.get('ref', ''),
                'title': title,
                'price': price,
                'currency': currency,
                'price_usd': price_usd if price_usd else price,
                'image': image,
                'location': location,
                'store': store,
                'slug': url_slug,
                'category': self._classify_part(title),
                'scraped_at': datetime.now().isoformat(),
                'vehicle_category': self._get_vehicle_category(self._classify_part(title)),
                'part_category': self._classify_part(title),
            }
            yield listing

    def _is_repuesto(self, title: str) -> bool:
        title_lower = title.lower()
        
        # Exclude complete vehicles
        exclude_vehicles = ['triciclo', 'bicicleta ', ' moto ', 'motorina', 'motoneta', 'scooter ', 'patinete', 'triciclo', 'mototrina', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad']
        for kw in ['triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad', 'bicicleta ', 'bicicleta eléctrica']:
            if kw in title_lower:
                return False
        
        # Must contain part keywords
        part_indicators = [
            'repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
            'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
            'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
            'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
            'batería', 'bateria', 'controlador', 'motor eléctrico',
            'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
            'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
            'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
            'cargador ', 'cargador de', 'cargador para',
            'batería ', 'bateria ', 'batería de', 'bateria de',
            'extensor de rango', 'extensor de rango',
        ]
        
        title_lower = title.lower()
        return any(kw in title_lower for kw in part_indicators)

    def _classify_part(self, title: str) -> str:
        title_lower = title.lower()
        
        # Check for specific vehicle type in title
        if any(kw in title_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'e bike']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in title_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard', 'monociclo']):
            return 'Repuesto Patinete'
        elif any(kw in title_lower for kw in ['bicicleta ', 'bici ', 'aro 26', 'aro 29', 'aro 27', 'aro 24', 'aro 20', 'mtb', 'mountain bike', 'huffy', 'vivamax', 'spiderman']):
            return 'Repuesto Bicicleta'
        elif any(kw in title_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas', 'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor', 'bicimoto', 'bicimotos', 'bici moto', 'bici-moto']):
            return 'Repuesto Moto'
        
        # Check for specific part keywords
        part_keywords = {
            'Repuesto Moto': ['motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia', 'freno moto', 'freno moto ', 'llanta moto', 'neumático moto', 'cadena moto', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto', 'bujia moto', 'bobina moto', 'carburador moto'],
            'Repuesto Bicicleta': ['aro ', 'llanta bici', 'neumático bici', 'cadena bici', 'piñon bici', 'cambio bici', 'desviador bici', 'freno bici', 'pastilla bici', 'manillar bici', 'sillin bici', 'sillín bici', 'pedal bici', 'biela bici', 'cuadro bici', 'horquilla bici', 'amortiguador bici'],
            'Repuesto Moto Eléctrica': ['batería moto', 'bateria moto', 'cargador moto', 'controlador moto', 'controlador ', 'ecu moto', 'cdi moto', 'bobina moto', 'estator moto', 'rotor moto', 'motor eléctrico moto', 'motor electrico moto', 'batería litio moto', 'bateria litio moto', 'lifepo4 moto', 'cargador moto', 'cargador de moto', 'controlador moto electrica'],
            'Repuesto Bicicleta Eléctrica': ['batería bici', 'bateria bici', 'cargador bici', 'controlador bici', 'motor eléctrico bici', 'motor electrico bici', 'batería litio bici', 'bateria litio bici', 'lifepo4 bici', 'cargador bici', 'cargador de bici', 'controlador bici electrica', 'motor central bici', 'motor buje bici'],
            'Repuesto Patinete': ['patinete', 'patineta', 'scooter eléctrico', 'scooter electrico', 'hoverboard', 'monociclo', 'unicycle'],
        }
        
        title_lower = title.lower()
        for category, keywords in part_keywords.items():
            for kw in keywords:
                if kw in title_lower:
                    return category
        
        return 'Repuesto Generico'

    def _get_vehicle_category(self, part_category: str) -> str:
        mapping = {
            'Repuesto Moto': 'Moto Combustión',
            'Repuesto Bicicleta': 'Bicicleta',
            'Repuesto Moto Eléctrica': 'Moto Eléctrica',
            'Repuesto Bicicleta Eléctrica': 'Bicicleta Eléctrica',
            'Repuesto Patinete': 'Patinete Eléctrico',
            'Repuesto Generico': 'Otro',
        }
        return mapping.get(part_category, 'Otro')

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = {"page": page}
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    print(f"Page {page}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Page {page}: Error - {e}")
            return None

    def parse_nuxt_data(self, html: str) -> Optional[List]:
        json_islands = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not json_islands:
            return None
        try:
            return json.loads(json_islands[0])
        except json.JSONDecodeError:
            return None

    def resolve_references(self, data: List) -> Dict[int, Any]:
        resolved = {}
        def resolve(idx: int, visited: Set[int] = None) -> Any:
            if visited is None:
                visited = set()
            if idx in visited:
                return f"<circular:{idx}>"
            if idx >= len(data):
                return f"<oob:{idx}>"
            visited.add(idx)
            val = data[idx]
            if isinstance(val, (str, int, float, bool)) or val is None:
                return val
            elif isinstance(val, list):
                result = []
                for i in val:
                    if isinstance(i, int):
                        result.append(resolve(i, visited.copy()))
                    else:
                        result.append(i)
                return result
            elif isinstance(val, dict):
                result = {}
                for k, v in val.items():
                    if isinstance(v, int):
                        result[k] = resolve(v, visited.copy())
                    else:
                        result[k] = v
                return result
            return val
        
        for i in range(len(data)):
            resolved[i] = resolve(i)
        return resolved

    def extract_products(self, data: List, resolved: Dict[int, Any]) -> List[Dict]:
        products = []
        for i, item in enumerate(data):
            if isinstance(item, dict) and 'ref' in item and 'name' in item and 'price' in item:
                product = {}
                for key, ref_idx in item.items():
                    if isinstance(ref_idx, int):
                        product[key] = resolved.get(ref_idx, f"<unresolved:{ref_idx}>")
                    elif isinstance(ref_idx, list):
                        product[key] = [resolved.get(idx, f"<unresolved:{idx}>") for idx in ref_idx]
                    else:
                        product[key] = ref_idx
                products.append(product)
        return products

    def fetch_page(self, page: int) -> Optional[str]:
        params = {"page": page}
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    print(f"Page {page}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Page {page}: Error - {e}")
            return None

    def process_page(self, page: int) -> List[Dict]:
        html = self.fetch_page(page)
        if not html:
            return []
        
        listings = list(self.process_page_data(html))
        
        # Filter
        filtered = [l for l in listings if l is not None]
        
        return filtered

    def save_page_data(self, page: int, html: str, listings: List[Dict]):
        source_dir = self._ensure_source_dir()
        
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps({
            'listings': [l for l in listings if l is not None],
            'page': page,
            'total_on_page': len(listings)
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        
        page_manifest = {
            "page": page,
            "url": f"{self.BASE_URL}?page={page}",
            "status": 200,
            "html_file": f"page_{page:04d}.html",
            "json_file": f"extracted_{page:04d}.json",
            "listings_found": len(listings),
            "scraped_at": datetime.now().isoformat()
        }
        self.manifest['pages'].append(page_manifest)
        self.manifest['totals']['pages_processed'] += 1
        self.manifest['totals']['listings_extracted'] += len(listings)
        for listing in listings:
            if listing:
                cat = listing.get('part_category', 'Repuesto Generico')
                self.manifest['totals']['listings_by_category'][cat] += 1

    def save_manifest(self):
        source_dir = self._ensure_source_dir()
        manifest_file = source_dir / "manifest.json"
        
        manifest_copy = self.manifest.copy()
        manifest_copy['totals']['listings_by_category'] = dict(manifest_copy['totals']['listings_by_category'])
        manifest_copy['completed_at'] = datetime.now().isoformat()
        manifest_copy['unique_listings'] = len(self.seen_listing_ids)
        
        manifest_file.write_text(json.dumps(manifest_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Manifest saved: {manifest_file}")

    def save_final_listings(self):
        cat_dir = self.output_base / "Repuestos" / "data" / "raw" / "scraped" / self.source_id
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        out_file = cat_dir / "listings_repuestos.json"
        out_file.write_text(json.dumps(self.all_listings, ensure_ascii=False, indent=2), encoding='utf-8')
        
        cat_manifest = {
            "source_id": self.source_id,
            "category": "Repuestos",
            "source_file": "listings_repuestos.json",
            "total_listings": len(self.all_listings),
            "extracted_at": datetime.now().isoformat(),
            "parent_manifest": str(self._ensure_source_dir() / "manifest.json")
        }
        (cat_dir / "manifest.json").write_text(json.dumps(cat_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"  Repuestos: {len(self.all_listings)} listings saved to {out_file}")

    def run(self):
        print(f"Starting scrape: {self.source_id}")
        print(f"Target: up to {self.max_pages} pages from {self.BASE_URL}")
        print(f"Filtering for repuestos only...")
        
        for page in range(1, self.max_pages + 1):
            print(f"\n--- Page {page}/{self.max_pages} ---")
            
            listings = self.process_page(page)
            
            if not listings:
                print(f"  No listings found on page {page}")
                break
            
            print(f"  Found {len(listings)} listings")
            
            # Track seen IDs
            for l in listings:
                if l.get('listing_id'):
                    self.seen_listing_ids.add(l['listing_id'])
            
            self.all_listings.extend(listings)
            self.save_page_data(page, "", listings)
            
            # Check if last page
            if len(listings) < 20:
                print("  Few listings found, might be last page")
                break
            
            time.sleep(1.5)
        
        self.save_manifest()
        print("\nSaving final filtered listings...")
        self.save_final_listings()
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique repuesto listings: {len(self.all_listings)}")


if __name__ == "__main__":
    scraper = ElYerroRepuestosScraper(max_pages=50)
    scraper.run()