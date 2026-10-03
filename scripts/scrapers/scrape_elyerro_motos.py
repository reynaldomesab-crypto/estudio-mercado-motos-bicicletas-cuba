#!/usr/bin/env python3
"""
ElYerroMenu Motorcycle Scraper
Extracts motorcycle listings from elyerromenu.com/l/search/motor?type=2
Filters for: actual motorcycles, motorinas, scooters, bicimotos (combustion & electric)
Excludes: phones (Motorola), parts, accessories, industrial motors, casco, batteries, etc.
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

ssl._create_default_https_context = ssl._create_unverified_context


class ElYerroMotoScraper:
    BASE_URL = "https://elyerromenu.com/l/search/motor"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Motorcycle-related keywords - ONLY keep actual vehicles
    MOTO_KEYWORDS = [
        # Motorcycles combustion
        'moto ', 'motocicleta', 'motocicletas',
        'moto deportiva', 'moto cross', 'moto enduro', 'moto trail',
        'moto scooter', 'scooter', 'scuter',
        'motoneta', 'motonetas',
        'motorina', 'motorinas',
        'ciclomotor', 'ciclomotores',
        'cubano', 'cubana',  # Cuban motorcycles
        'jin ', 'jincheng', 'loncin', 'lifan', 'znen', 'keeway', 'bj ',
        'yamaha ', 'honda ', 'suzuki ', 'kawasaki ', 'ktm ',
        'cz ', 'java ', 'mz ', 'simson ',
        'cc ', 'cilindrada', '125cc', '150cc', '200cc', '250cc', '300cc',
        
        # Electric motorcycles/scooters
        'moto eléctrica', 'moto electrica',
        'motorina eléctrica', 'motorina electrica',
        'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
        'scooter eléctrico', 'scooter electrico',
        'patinete eléctrico', 'patinete electrico',
        'kvitova', 'halcón', 'halcon', 'pla51',
        'motorina gasolina', 'motorina eléctrica',
        
        # Brands/models common in Cuba
        'adv ', 'restrepa', 'mt ', 'krathos', 'izuki',
        'acorazada', 'blindada',
    ]

    # Exclude keywords - NOT motorcycles
    EXCLUDE_KEYWORDS = [
        # Phones (Motorola)
        'motorola', 'moto g', 'moto g0', 'moto g1', 'moto g2', 'moto g3',
        'moto g4', 'moto g5', 'moto g6', 'moto g7', 'moto g8', 'moto g9',
        'moto e', 'moto e0', 'moto e1', 'moto e2', 'moto e3', 'moto e4',
        'moto e5', 'moto e6', 'moto e7', 'moto edge', 'moto razr',
        'celular', 'smartphone', 'telefono', 'móvil', 'movil',
        'gb ram', 'gb almacenamiento', 'gb almacenamiento',
        
        # Parts & Accessories
        'casco', 'cascos', 'helmet',
        'batería para', 'bateria para', 'batería de moto', 'bateria de moto',
        'batería triciclo', 'bateria triciclo',
        'alarma', 'alarmas', 'mishozuki', 'yoasaky', 'nippon',
        'breque', 'breques', 'freno', 'frenos', 'pastilla', 'pastillas',
        'neumático', 'neumáticos', 'llanta', 'llantas', 'cubierta', 'cubiertas',
        'repuesto', 'repuestos', 'accesorio', 'accesorios', 'pieza', 'piezas',
        'componente', 'componentes', 'kit conversión', 'kit conversion',
        'controlador', 'cargador', 'cargador de',
        'espejo', 'espejos', 'retrovisor', 'retrovisores',
        'manillar', 'puño', 'puños', 'maneta', 'manetas',
        'cadena', 'piñón', 'piñon', 'corona', 'tensor',
        'amortiguador', 'horquilla', 'horquillas',
        'carburador', 'inyector', 'bujía', 'bujia', 'bobina',
        'filtro', 'aceite', 'lubricante', 'refrigerante',
        'base para', 'soporte para', 'parrilla', 'baúl', 'baul', 'maleta',
        'guarda', 'guardabarros', 'guardalodos',
        'farol', 'farola', 'luz trasera', 'luz delantera', 'intermitente',
        'claxon', 'bocina', 'contacto', 'llave', 'llaves',
        'documentos', 'matricula', 'placa', 'transferencia',
        'instalación eléctrica', 'instalacion electrica', 'electricista',
        'gafas', 'lentes', 'goggles', 'guantes', 'guante',
        'chaqueta', 'pantalon', 'pantalón', 'botas', 'bota',
        'rodillera', 'coderas', 'protector', 'protección', 'proteccion',
        
        # Industrial/Other motors
        'motor evaporador', 'fan motor', 'motor ventilador', 'motor de',
        'motor electrico', 'motor eléctrico', 'bomba motor', 'motor bomba',
        'compresor', 'generador', 'alternador', 'arranque',
        'motor industrial', 'motor trifasico', 'motor monofasico',
        'hp ', 'cv ', 'kw motor', 'rpm ',
        
        # Other vehicles
        'triciclo', 'triciclos', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
        'bicicleta', 'bici ', 'ebike', 'e-bike', 'mountain bike', 'mtb',
        'patinete', 'skate', 'hoverboard', 'monociclo',
        'carro', 'auto', 'automovil', 'automóvil', 'camioneta', 'furgoneta',
        'barco', 'lancha', 'motor fuera', 'fuera de borda',
        
        # Services
        'reparación', 'reparacion', 'taller', 'mecanico', 'mecánico',
        'lavado', 'engrase', 'mantenimiento', 'revision', 'revisión',
        'pintura', 'pintado', 'cromado', 'tapiceria', 'tapicería',
        'importacion', 'importación', 'traer', 'gestionar', 'tramite', 'trámite',
    ]

    # Price filters (USD equivalent)
    PRICE_FILTERS = {
        'Motos_Bici': {'min': 50, 'max': 100000},
    }

    def __init__(self, output_base: str = "/home/reynaldomesab/Project", max_pages: int = 100):
        self.output_base = Path(output_base)
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"elyerro_motos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "elyerromenu.com",
            "source_url": f"{self.BASE_URL}?type=2",
            "category_hint": "motor",
            "scraped_at": self.session_start,
            "scraper_version": "1.0",
            "pages": [],
            "totals": {"pages_processed": 0, "listings_extracted": 0, "listings_by_category": defaultdict(int)}
        }
        self.seen_product_ids: Set[str] = set()
        self.all_products: List[Dict] = []

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "Motos_Bici" / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = {"page": page, "type": "2"}
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

    def _is_motorcycle(self, title: str) -> bool:
        """Check if listing is an actual motorcycle/motorina/scooter."""
        title_lower = title.lower()
        
        # Must contain motorcycle-related keyword
        has_moto = any(kw in title_lower for kw in self.MOTO_KEYWORDS)
        
        # Must NOT contain exclude keywords
        has_exclude = any(kw in title_lower for kw in self.EXCLUDE_KEYWORDS)
        
        return has_moto and not has_exclude

    def _convert_price_to_usd(self, price: float, currency: str) -> Optional[float]:
        """Convert price to USD for filtering."""
        if price is None:
            return None
        currency = currency.upper() if currency else 'USD'
        if currency == 'USD':
            return price
        elif currency == 'CUP':
            return price * 0.00042  # Approximate: 2400 CUP = 1 USD
        elif currency == 'MLC':
            return price  # MLC is 1:1 with USD
        elif currency == 'ZELLE':
            return price  # Zelle payments are in USD
        elif currency == 'EUR':
            return price * 1.08  # Approximate EUR to USD
        else:
            return price  # Default assume USD

    def _is_price_outlier(self, category: str, price_usd: Optional[float]) -> bool:
        if price_usd is None:
            return True
        filters = self.PRICE_FILTERS.get(category, {'min': 0, 'max': float('inf')})
        return price_usd < filters['min'] or price_usd > filters['max']

    def filter_products(self, products: List[Dict]) -> tuple[List[Dict], Dict[str, int]]:
        filtered = []
        stats = {'total': len(products), 'non_moto': 0, 'outliers': 0, 'no_price': 0, 'by_category': defaultdict(int), 'duplicates': 0, 'currencies': Counter()}
        
        for p in products:
            pid = p.get('ref') or p.get('id')
            if pid in self.seen_product_ids:
                stats['duplicates'] += 1
                continue
            
            title = p.get('name', '')
            price = p.get('price')
            currency = p.get('currency', 'USD')
            
            stats['currencies'][currency] += 1
            
            # Check if actual motorcycle
            if not self._is_motorcycle(title):
                stats['non_moto'] += 1
                continue
            
            price_usd = self._convert_price_to_usd(price, currency)
            
            if price_usd is None:
                stats['no_price'] += 1
                continue
            
            if self._is_price_outlier('Motos_Bici', price_usd):
                stats['outliers'] += 1
                continue
            
            # Add computed fields
            p['price_usd'] = price_usd
            p['currency_original'] = currency
            p['source_id'] = self.source_id
            p['source_url'] = f"https://elyerromenu.com/l/{p.get('slug', '')}" if p.get('slug') else self.BASE_URL
            p['scraped_at'] = datetime.now().isoformat()
            p['category_detected'] = 'Motos_Bici'
            
            self.seen_product_ids.add(pid)
            filtered.append(p)
            stats['by_category']['Motos_Bici'] += 1
        
        stats['kept'] = len(filtered)
        return filtered, stats

    def save_page_data(self, page: int, html: str, products: List[Dict], stats: Dict):
        source_dir = self._ensure_source_dir()
        
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps({
            'products': products,
            'filter_stats': stats,
            'page': page
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        
        page_manifest = {
            "page": page,
            "url": f"{self.BASE_URL}?page={page}&type=2",
            "status": 200,
            "html_file": f"page_{page:04d}.html",
            "json_file": f"extracted_{page:04d}.json",
            "products_found": stats['total'],
            "products_non_moto": stats['non_moto'],
            "products_outliers": stats['outliers'],
            "products_no_price": stats['no_price'],
            "products_duplicates": stats['duplicates'],
            "products_kept": stats['kept'],
            "products_by_category": dict(stats['by_category']),
            "currencies": dict(stats['currencies']),
            "scraped_at": datetime.now().isoformat()
        }
        self.manifest['pages'].append(page_manifest)
        self.manifest['totals']['pages_processed'] += 1
        self.manifest['totals']['listings_extracted'] += stats['kept']
        for cat, count in stats['by_category'].items():
            self.manifest['totals']['listings_by_category'][cat] += count

    def save_manifest(self):
        source_dir = self._ensure_source_dir()
        manifest_file = source_dir / "manifest.json"
        
        manifest_copy = self.manifest.copy()
        manifest_copy['totals']['listings_by_category'] = dict(manifest_copy['totals']['listings_by_category'])
        manifest_copy['completed_at'] = datetime.now().isoformat()
        manifest_copy['unique_products_total'] = len(self.seen_product_ids)
        
        manifest_file.write_text(json.dumps(manifest_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Manifest saved: {manifest_file}")

    def save_final_listings(self):
        cat_dir = self.output_base / "Motos_Bici" / "data" / "raw" / "scraped" / self.source_id
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        out_file = cat_dir / "listings_motos_bici.json"
        out_file.write_text(json.dumps(self.all_products, ensure_ascii=False, indent=2), encoding='utf-8')
        
        cat_manifest = {
            "source_id": self.source_id,
            "category": "Motos_Bici",
            "source_file": "listings_motos_bici.json",
            "total_listings": len(self.all_products),
            "extracted_at": datetime.now().isoformat(),
            "parent_manifest": str(self._ensure_source_dir() / "manifest.json")
        }
        (cat_dir / "manifest.json").write_text(json.dumps(cat_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"  Motos_Bici: {len(self.all_products)} listings saved to {out_file}")

    def run(self):
        print(f"Starting scrape: {self.source_id}")
        print(f"Target: up to {self.max_pages} pages from {self.BASE_URL}?type=2")
        print(f"Filtering for actual motorcycles/motorinas only...")
        
        consecutive_empty = 0
        
        for page in range(1, self.max_pages + 1):
            print(f"\n--- Page {page}/{self.max_pages} ---")
            
            html = self.fetch_page(page)
            if not html:
                print(f"  Failed to fetch page {page}")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print("  Multiple failed pages, stopping.")
                    break
                continue
            
            data = self.parse_nuxt_data(html)
            if not data:
                print(f"  No Nuxt data on page {page}")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
                continue
            
            resolved = self.resolve_references(data)
            products = self.extract_products(data, resolved)
            
            if not products:
                print(f"  No products found on page {page}")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print("  Multiple empty pages, stopping.")
                    break
                continue
            
            print(f"  Found {len(products)} products")
            consecutive_empty = 0
            
            filtered, stats = self.filter_products(products)
            print(f"  After filters: {stats['kept']} kept (non_moto: {stats['non_moto']}, outliers: {stats['outliers']}, no_price: {stats['no_price']}, duplicates: {stats['duplicates']})")
            print(f"  Currencies: {dict(stats['currencies'])}")
            for cat, count in stats['by_category'].items():
                print(f"    {cat}: {count}")
            
            self.all_products.extend(filtered)
            self.save_page_data(page, html, filtered, stats)
            
            reactive = data[5] if len(data) > 5 else {}
            load_more = reactive.get('loadMore')
            if not load_more:
                print("  No more pages (loadMore=false)")
                break
            
            time.sleep(1.0)
        
        self.save_manifest()
        print("\nSaving final listings...")
        self.save_final_listings()
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique motorcycles: {len(self.all_products)}")


if __name__ == "__main__":
    scraper = ElYerroMotoScraper(max_pages=100)
    scraper.run()