#!/usr/bin/env python3
"""
itencel.com Motorcycle Scraper
Scrapes motorcycle listings from itencel.com/anuncio-categoria/vehiculos/motos/
Filters out tricycles (triciclos) and other non-motorcycle vehicles
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


class ItencelMotoScraper:
    BASE_URL = "https://itencel.com/anuncio-categoria/vehiculos/motos/"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Vehicle classification keywords
    MOTO_KEYWORDS = [
        'moto ', 'motos ', 'motocicleta', 'motocicletas',
        'motorina', 'motorinas', 'motoneta', 'motonetas',
        'scooter', 'scooters', 'scuter',
        'ciclomotor', 'ciclomotores',
        'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
        'moto eléctrica', 'moto electrica', 'motos eléctricas', 'motos electricas',
        'motorina eléctrica', 'motorina electrica', 'motorinas eléctricas',
        'bicimoto eléctrica', 'bicimoto electrica', 'bicimotos eléctricas',
        'bicimotos ', 'bicimotos',
        # Marcas
        'yamaha', 'honda ', 'suzuki ', 'kawasaki', 'ktm ', 'ducati', 'harley',
        'bj ', 'keeway', 'znen', 'loncin', 'lifan', 'cg125', 'cg150', 'cg200',
        'xr150', 'xr250', 'crf', 'yzf', 'r15', 'r3', 'mt07', 'mt09', 'r1', 'r6',
        'cbr', 'cbf', 'cb125', 'cb190', 'cb300', 'cb500', 'cb650', 'cb1000',
        'hornet', 'shadow', 'vstrom', 'gsx', 'gsxr', 'hayabusa', 'bandit',
        'ninja', 'zx6r', 'zx10r', 'z900', 'z650', 'versys', 'vulcan',
        'duke', 'rc390', 'rc125', 'adv ', 'enduro', 'cross', 'motard', 'trail',
        'jin ', 'krathos', 'restrepa', 'mt ', 'halcón', 'halcon', 'vedca',
        'lifan', 'izuki', 'unison', 'topmaq', 'ava pantera', 'mountain',
        'kvitova', 'pla51', 'pla 51',
        'mikazuki', 'caiman', 'vedca ', 'mvp ', 'jinpeng', 'qlife',
        'onebot', 'power ', 'extensor de rango', 'refrigerado',
        'shikra', 'avisp', 'predator', 'challenger', 'voltus', 'eagle',
        'pron', 'prontezza', 'corleone', 'maf ', 'maf eagle',
        'motico', 'matico', 'motico ',
        'challenger', 'prontezza', 'corleone',
        'maf ', 'maf eagle', 'eagle',
    ]

    # Exclude triciclos and other non-motorcycle vehicles
    EXCLUDE_KEYWORDS = [
        'triciclo', 'triciclos', 'tricos', 'triciclo eléctrico', 'triciclo electrico',
        'triciclo híbrido', 'triciclo hibrido', 'triciclo de carga',
        'mototrina', 'mototrin', 'mototaxi',
        'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
        'bicicleta', 'bici ', 'ebike', 'e-bike', 'e bike',
        'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
        'patinete', 'patineta', 'hoverboard', 'monociclo',
        'carro', 'auto', 'automovil', 'automóvil',
        # Parts/accessories - standalone sales
        'repuesto', 'repuestos', 'accesorio', 'accesorios', 'pieza', 'piezas',
        'componente', 'componentes', 'kit conversión', 'kit conversion',
        'candado', 'lock', 'base para', 'soporte para', 'parrilla', 'portabici',
        'portabicicleta', 'bombín', 'bombin', 'inflador', 'bomba de aire',
        'luz para', 'luz bici', 'luz trasera', 'luz delantera', 'farol bici',
        'espejo', 'retrovisor', 'timbre', 'bocina', 'guarda', 'guardabarros',
        'asiento', 'sillin', 'sillín', 'silla bici', 'manillar', 'puño', 'puños',
        'maneta', 'pedal', 'pedales', 'pedalier', 'biela', 'bielas',
        'cadena', 'piñón', 'piñon', 'corona', 'cassette', 'piñones',
        'cambio', 'desviador', 'shifter', 'palanca cambio', 'freno', 'frenos',
        'pastilla', 'pastillas', 'disco', 'caliper', 'llanta', 'neumático',
        'neumáticos', 'cubierta', 'cubiertas', 'cámara', 'camara', 'parche',
        'parches', 'válvula', 'valvula', 'rayo', 'rayos', 'radio', 'radios',
        'horquilla', 'horquillas', 'amortiguador', 'suspensión', 'suspension',
        'cuadro', 'frame', 'chasis', 'tija', 'tija de sillín',
        'reparación', 'reparacion', 'taller', 'mecanico', 'mecánico',
        'mantenimiento', 'ajuste', 'centrado', 'alineación', 'alineacion',
        'filtro', 'aceite', 'lubricante', 'refrigerante', 'bujía', 'bujia',
        'bobina', 'carburador', 'inyector', 'arranque', 'alternador',
        'generador', 'breque', 'breques', 'neumático de',
        'instalación eléctrica', 'instalacion electrica', 'electricista',
        'motor evaporador', 'fan motor', 'motor de', 'motor para',
        'planta eléctrica', 'planta electrica', 'generador', 'inverter',
        'ventilador', 'cocina', 'hornilla', 'estufa',
        'cargador para', 'cargador de', 'cargador ',
        'capa de moto', 'capa de', 'funda', 'protector',
        'intercomunicador', 'gps', 'soporte celular', 'soporte movil',
        'cremallera', 'puntas de inyección', 'tractor', 'lada',
        'nike air max', 'zapatilla', 'zapato', 'tenis', 'ropa', 'camisa',
        'pantalon', 'pantalón', 'chaqueta', 'guantes', 'casco', 'cascos',
        'gafas', 'lentes', 'mochila', 'bolso', 'cartera', 'reloj',
        'celular', 'móvil', 'movil', 'tablet', 'laptop', 'computadora',
        'televisor', 'tv', 'nevera', 'refrigerador', 'lavadora', 'microondas',
        'licuadora', 'batidora', 'cafetera', 'perfume', 'crema', 'shampoo',
        'trailer', 'remolque', 'carreta',
        'consola', 'caja 5ta', 'forro de', 'kit de bases', 'vendo neumáticos',
        'reproductor', 'cámara', 'android', 'carplay', 'ojos del diablo',
        'interesados', 'me ajusto', 'arrancador portátil',
        'oferta', 'se recogen',
        'compresor', 'enganche', 'bola de trailler',
        # Battery/charger standalone
        'batería topmaq', 'bateria topmaq', 'batería 72v', 'bateria 72v',
        'batería 48v', 'bateria 48v', 'batería litio', 'bateria litio',
        'batería gel', 'bateria gel', 'batería agm', 'bateria agm',
        'batería de litio', 'bateria de litio', 'banco de baterías',
        'banco de baterias', 'batería para', 'bateria para', 'batería de',
        'bateria de', 'baterías de', 'baterias de', 'batería x', 'bateria x',
        'cargador para', 'cargador de', 'cargador ',
    ]

    # Price filters (USD)
    PRICE_FILTERS = {
        'Moto': {'min': 50, 'max': 100000},
    }

    def __init__(self, output_base: str = str(RAIZ), max_pages: int = 109):
        self.output_base = Path(output_base)
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"itencel_motos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "itencel.com",
            "source_url": self.BASE_URL,
            "category_hint": "motos",
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
        if page == 1:
            url = self.BASE_URL
        else:
            url = f"{self.BASE_URL}page/{page}/"
        
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

    def extract_listings_from_page(self, html: str) -> List[Dict]:
        """Extract all listing cards from a page HTML."""
        listings = []
        
        # Find all listing card starts using the exact class pattern
        card_pattern = r'<div[^>]*class="rtcl-listing-card it-app listing-item rtcl-listing-item[^"]*"'
        card_starts = [(m.start(), m.end()) for m in re.finditer(card_pattern, html)]
        
        # Extract each card by finding from one start to the next start
        cards = []
        for i, (start, end) in enumerate(card_starts):
            if i + 1 < len(card_starts):
                card_html = html[start:card_starts[i+1][0]]
            else:
                # Last card - extract up to a reasonable length
                card_html = html[start:start+8000]
            cards.append(card_html)
        
        # Parse each card
        for card_html in cards:
            listing = self._parse_listing_card(card_html)
            if listing:
                listings.append(listing)
        
        return listings

    def _parse_listing_card(self, card_html: str) -> Optional[Dict]:
        """Parse a single listing card and extract all data."""
        
        # Post ID
        post_id_match = re.search(r'post-(\d+)', card_html)
        post_id = post_id_match.group(1) if post_id_match else None
        
        if post_id and post_id in self.seen_listing_ids:
            return None
        
        # URL and Title
        title_match = re.search(r'<h3[^>]*class="[^"]*listing-title[^"]*"[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', card_html, re.DOTALL)
        if not title_match:
            return None
        
        url = title_match.group(1)
        title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
        
        # Check for triciclo exclusion
        if self._is_triciclo(title):
            return None
        
        # Image - try multiple patterns
        img_patterns = [
            r'<img[^>]+src="([^"]+)"[^>]*class="rtcl-thumbnail"',
            r'<img[^>]+class="rtcl-thumbnail"[^>]*src="([^"]+)"',
        ]
        image = None
        for pattern in img_patterns:
            img_match = re.search(pattern, card_html)
            if img_match:
                image = img_match.group(1)
                break
        
        # Price
        price_match = re.search(r'<bdi>([^<]+)&nbsp;<span class="rtcl-price-currencySymbol">([^<]+)</span></bdi>', card_html)
        if price_match:
            price_text = price_match.group(1).replace(',', '').replace('&nbsp;', '').strip()
            currency_symbol = price_match.group(2).strip()
            try:
                price = float(price_text)
            except:
                price = None
        else:
            price = None
            currency_symbol = None
        
        # Location - try multiple patterns
        loc_patterns = [
            r'<li class="rt-location"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>',
            r'class="rt-location"[^>]*><a[^>]*href="[^"]+"[^>]*>(.*?)</a>',
        ]
        location = None
        for pattern in loc_patterns:
            loc_match = re.search(pattern, card_html, re.DOTALL)
            if loc_match:
                location = re.sub(r'<[^>]+>', '', loc_match.group(1)).strip()
                break
        
        # Category - try multiple patterns
        cat_patterns = [
            r'<li class="rt-categories"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>',
            r'class="rt-categories"[^>]*><a[^>]*href="[^"]+"[^>]*>(.*?)</a>',
        ]
        category = None
        for pattern in cat_patterns:
            cat_match = re.search(pattern, card_html, re.DOTALL)
            if cat_match:
                category = re.sub(r'<[^>]+>', '', cat_match.group(1)).strip()
                break
        
        # Date
        date_match = re.search(r'class="updated"[^>]*><i[^>]*></i>&nbsp;(.*?)</li>', card_html, re.DOTALL)
        date_text = re.sub(r'<[^>]+>', '', date_match.group(1)).strip() if date_match else None
        
        # Views
        views_match = re.search(r'class="rt-views"[^>]*>.*?(\d+)\s*vistas', card_html, re.DOTALL)
        if not views_match:
            views_match = re.search(r'class="rt-views"[^>]*>.*?(\d+)', card_html, re.DOTALL)
        views = int(views_match.group(1)) if views_match else None
        
        # Badges
        badges = []
        badge_matches = re.findall(r'class="badge[^"]*"[^>]*>(.*?)</span>', card_html, re.DOTALL)
        for b in badge_matches:
            badges.append(re.sub(r'<[^>]+>', '', b).strip())
        
        # Category and Location from class attributes
        class_attr_match = re.search(r'class="[^"]*rtcl_category-([a-z0-9-]+)', card_html)
        category_class = class_attr_match.group(1) if class_attr_match else None
        
        loc_class_match = re.search(r'class="[^"]*rtcl_location-([a-z0-9-]+)', card_html)
        location_class = loc_class_match.group(1) if loc_class_match else None
        
        # Listing ID from meta buttons
        listing_id_match = re.search(r'data-listing_id="(\d+)"', card_html)
        listing_id = listing_id_match.group(1) if listing_id_match else post_id
        
        # Build the listing
        listing = {
            'source': 'itencel',
            'source_id': self.source_id,
            'source_url': url,
            'listing_id': listing_id,
            'title': title,
            'price': price,
            'currency': currency_symbol.rstrip() if currency_symbol else 'USD',
            'price_usd': price,  # Assuming USD for now
            'image': image,
            'location': location,
            'location_class': location_class,
            'category': category,
            'category_class': category_class,
            'date_text': date_text,
            'views': views,
            'badges': badges,
            'post_id': post_id,
            'source_post_id': post_id,
            'scraped_at': datetime.now().isoformat(),
            'vehicle_type': 'Moto',
        }
        
        return listing

    def _is_triciclo(self, title: str) -> bool:
        """Check if listing is a triciclo (should be excluded)."""
        title_lower = title.lower()
        for kw in self.EXCLUDE_KEYWORDS:
            if kw in title_lower:
                return True
        return False

    def _is_motorcycle(self, title: str) -> bool:
        """Check if listing is a motorcycle."""
        title_lower = title.lower()
        for kw in self.MOTO_KEYWORDS:
            if kw in title_lower:
                return True
        return False

    def filter_listing(self, listing: Dict) -> bool:
        """Filter listing - keep only motorcycles, exclude triciclos."""
        title = listing.get('title', '')
        
        # Must be a motorcycle
        if not self._is_motorcycle(title):
            return False
        
        # Must not be a triciclo
        if self._is_triciclo(title):
            return False
        
        # Price validation
        price = listing.get('price_usd')
        if price is not None:
            filters = self.PRICE_FILTERS.get('Moto', {'min': 50, 'max': 100000})
            if price < filters['min'] or price > filters['max']:
                return False
        
        return True

    def save_page_data(self, page: int, html: str, listings: List[Dict]):
        """Save raw HTML and extracted data for a page."""
        source_dir = self._ensure_source_dir()
        
        # Save raw HTML
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        # Save extracted JSON
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps({
            'listings': listings,
            'page': page,
            'total_on_page': len(listings)
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # Update manifest
        page_manifest = {
            "page": page,
            "url": f"{self.BASE_URL}page/{page}/" if page > 1 else self.BASE_URL,
            "status": 200,
            "html_file": f"page_{page:04d}.html",
            "json_file": f"extracted_{page:04d}.json",
            "listings_found": len(listings),
            "scraped_at": datetime.now().isoformat()
        }
        self.manifest['pages'].append(page_manifest)
        self.manifest['totals']['pages_processed'] += 1
        self.manifest['totals']['listings_extracted'] += len(listings)
        self.manifest['totals']['listings_by_category']['Moto'] += len(listings)

    def save_manifest(self):
        """Save manifest file."""
        source_dir = self._ensure_source_dir()
        manifest_file = source_dir / "manifest.json"
        
        manifest_copy = self.manifest.copy()
        manifest_copy['totals']['listings_by_category'] = dict(manifest_copy['totals']['listings_by_category'])
        manifest_copy['completed_at'] = datetime.now().isoformat()
        manifest_copy['unique_listings'] = len(self.seen_listing_ids)
        
        manifest_file.write_text(json.dumps(manifest_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Manifest saved: {manifest_file}")

    def save_final_listings(self):
        """Save all filtered listings to category directory."""
        cat_dir = self.output_base / "Motos_Bici" / "data" / "raw" / "scraped" / self.source_id
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        out_file = cat_dir / "listings_motos_bici.json"
        out_file.write_text(json.dumps(self.all_listings, ensure_ascii=False, indent=2), encoding='utf-8')
        
        cat_manifest = {
            "source_id": self.source_id,
            "category": "Motos_Bici",
            "source_file": "listings_motos_bici.json",
            "total_listings": len(self.all_listings),
            "extracted_at": datetime.now().isoformat(),
            "parent_manifest": str(self._ensure_source_dir() / "manifest.json")
        }
        (cat_dir / "manifest.json").write_text(json.dumps(cat_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"  Motos_Bici: {len(self.all_listings)} listings saved to {out_file}")

    def run(self):
        """Main scraping loop."""
        print(f"Starting scrape: {self.source_id}")
        print(f"Target: up to {self.max_pages} pages from {self.BASE_URL}")
        print(f"Filtering for motorcycles only, excluding triciclos...")
        
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
            
            listings = self.extract_listings_from_page(html)
            
            if not listings:
                print(f"  No listings found on page {page}")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print("  Multiple empty pages, stopping.")
                    break
                continue
            
            print(f"  Found {len(listings)} raw listings")
            consecutive_empty = 0
            
            # Filter listings
            filtered = [l for l in listings if self.filter_listing(l)]
            print(f"  After filters: {len(filtered)} kept")
            
            # Track seen IDs
            for l in filtered:
                if l.get('listing_id'):
                    self.seen_listing_ids.add(l['listing_id'])
            
            # Accumulate
            self.all_listings.extend(filtered)
            
            # Save page data
            self.save_page_data(page, html, filtered)
            
            # Check for pagination - if less than expected items, might be last page
            if len(listings) < 20:  # Expecting ~20-50 per page
                print("  Few listings found, might be last page")
            
            # Rate limiting
            time.sleep(1.5)
        
        self.save_manifest()
        print("\nSaving final filtered listings...")
        self.save_final_listings()
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique motorcycle listings: {len(self.all_listings)}")


if __name__ == "__main__":
    scraper = ItencelMotoScraper(max_pages=109)
    scraper.run()