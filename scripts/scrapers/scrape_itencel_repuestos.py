#!/usr/bin/env python3
"""
itencel.com Repuestos Scraper
Extracts motorcycle/bicycle spare parts listings from itencel.com
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


class ItencelRepuestosScraper:
    BASE_URL = "https://itencel.com/anuncios/repuestos/"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Vehicle classification keywords for parts
    PART_CATEGORIES = {
        'Repuesto Moto': [
            'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
            'motoneta', 'motonetas', 'scooter', 'scooters',
            'ciclomotor', 'ciclomotores', 'bicimoto', 'bicimotos',
            'bici moto', 'bici-moto',
            'moto eléctrica', 'moto electrica', 'motos eléctricas', 'motos electricas',
            'motorina eléctrica', 'motorina electrica', 'motorinas eléctricas',
            'bicimoto eléctrica', 'bicimoto electrica', 'bicimotos eléctricas',
            'bicimotos ', 'bicimotos',
            'motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia',
            'freno moto', 'freno moto ', 'llanta moto', 'neumático moto', 'cadena moto',
            'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto',
            'bobina moto', 'carburador moto', 'cigueñal', 'ciguenal', 'biela',
            'embrague', 'variador', 'piñon', 'corona', 'filtro', 'aceite', 'bujía', 'bujia',
        ],
        'Repuesto Bicicleta': [
            'bicicleta ', 'bicicletas ', 'bici ', ' ebike', 'e-bike', 'e bike',
            'bicicleta de montaña', 'bicicleta montaña', 'mtb', 'mountain bike',
            'bicicleta de paseo', 'bicicleta paseo', 'bicicleta de ruta', 'bicicleta ruta',
            'bicicleta plegable', 'bici plegable', 'folding bike',
            'bicicleta infantil', 'bicicleta para niños', 'bicicleta para ninos',
            'bicicleta 12', 'bicicleta 14', 'bicicleta 16', 'bicicleta 18', 'bicicleta 20', 'bicicleta 24', 'bicicleta 26', 'bicicleta 29',
            'aro 26', 'aro 27', 'aro 29', 'aro 24', 'aro 20',
            'huffy', 'vivamax', 'spiderman', 'equilibrio', 'balance bike',
            'bicicleta de montaña', 'bicicleta montaña', 'mtb', 'mountain bike',
            'bicicleta de paseo', 'bicicleta paseo', 'bicicleta de ruta', 'bicicleta ruta',
            'bicicleta plegable', 'bici plegable', 'folding bike',
            'bicicleta infantil', 'bicicleta para niños', 'bicicleta para ninos',
            'bicicleta 12', 'bicicleta 14', 'bicicleta 16', 'bicicleta 18', 'bicicleta 20', 'bicicleta 24', 'bicicleta 26', 'bicicleta 29',
            'aro 26', 'aro 27', 'aro 29', 'aro 24', 'aro 20',
            'huffy', 'vivamax', 'spiderman', 'equilibrio', 'balance bike',
        ],
        'Repuesto Moto Eléctrica': [
            'moto eléctrica', 'moto electrica', 'motos eléctricas', 'motos electricas',
            'motorina eléctrica', 'motorina electrica', 'motorinas eléctricas',
            'bicimoto eléctrica', 'bicimoto electrica', 'bicimotos eléctricas',
            'bicimotos ', 'bicimotos',
            'batería moto', 'bateria moto', 'cargador moto', 'controlador moto',
            'controlador ', 'ecu moto', 'cdi moto', 'bobina moto', 'estator moto',
            'rotor moto', 'motor eléctrico moto', 'motor electrico moto',
            'batería litio moto', 'bateria litio moto', 'lifepo4 moto',
            'cargador moto', 'cargador de moto', 'controlador moto electrica',
        ],
        'Repuesto Bicicleta Eléctrica': [
            'bicicleta eléctrica', 'bicicleta electrica', 'bicicletas eléctricas',
            'bici eléctrica', 'bici electrica', 'bicis eléctricas',
            'ebike', 'e-bike', 'e bike', 'bicicleta a bateria', 'bicicleta a pilas',
            'bicicleta con motor', 'bicicleta motorizada',
            'batería bici', 'bateria bici', 'cargador bici', 'controlador bici',
            'motor eléctrico bici', 'motor electrico bici', 'motor central bici',
            'batería litio bici', 'bateria litio bici', 'lifepo4 bici',
            'cargador bici', 'cargador de bici', 'controlador bici electrica',
            'motor central bici', 'motor buje bici',
        ],
        'Repuesto Patinete': [
            'patinete', 'patinetes', 'patineta', 'scooter eléctrico', 'scooter electrico',
            'scooters eléctricos', 'hoverboard', 'monociclo', 'unicycle',
        ],
    }

    # Exclude complete vehicles and non-parts
    EXCLUDE_KEYWORDS = [
        # Complete vehicles
        'triciclo', 'triciclos', 'tricos', 'triciclo eléctrico', 'triciclo electrico',
        'triciclo híbrido', 'triciclo hibrido', 'triciclo de carga',
        'mototrina', 'mototrin', 'mototaxi',
        'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
        'bicicleta ', 'bicicletas ', 'bici ', ' ebike', 'e-bike', 'e bike',
        'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
        'patinete', 'patinetes', 'scooter eléctrico', 'hoverboard', 'monociclo',
        'carro', 'auto', 'automovil', 'automóvil',
        'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
        'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor',
        'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
        'bicicletas ', 'bici ',
        'bicicleta de montaña', 'bicicleta montaña', 'mtb', 'mountain bike',
        'bicicleta de paseo', 'bicicleta paseo', 'bicicleta de ruta', 'bicicleta ruta',
        'bicicleta plegable', 'bici plegable', 'folding bike',
        'bicicleta infantil', 'bicicleta para niños', 'bicicleta para ninos',
        'patinete', 'patinetes', 'scooter eléctrico', 'scooter electrico',
        'scooters eléctricos', 'hoverboard', 'monociclo',
        'triciclo', 'triciclos', 'triciclo eléctrico', 'triciclo electrico',
        'mototrina', 'mototrin', 'mototaxi',
        # Non-vehicle items
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
        self.source_id = f"itencel_repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "itencel.com",
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
        
        # Find all listing card starts
        card_pattern = r'<div[^>]*class="rtcl-listing-card it-app listing-item rtcl-listing-item[^"]*"'
        card_starts = [(m.start(), m.end()) for m in re.finditer(card_pattern, html)]
        
        # Extract each card by finding from one start to the next start
        cards = []
        for i, (start, end) in enumerate(card_starts):
            if i + 1 < len(card_starts):
                card_html = html[start:card_starts[i+1][0]]
            else:
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
        
        # Check for excluded items (complete vehicles)
        if self._is_excluded(title):
            return None
        
        # Image
        img_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="rtcl-thumbnail"', card_html)
        image = img_match.group(1) if img_match else None
        
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
        
        # Location
        loc_match = re.search(r'<li class="rt-location"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', card_html, re.DOTALL)
        location = re.sub(r'<[^>]+>', '', loc_match.group(1)).strip() if loc_match else None
        
        # Category
        cat_match = re.search(r'<li class="rt-categories"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', card_html, re.DOTALL)
        category = re.sub(r'<[^>]+>', '', cat_match.group(1)).strip() if cat_match else None
        
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
        
        # Post ID
        post_id_match = re.search(r'post-(\d+)', card_html)
        post_id = post_id_match.group(1) if post_id_match else None
        
        if post_id and post_id in self.seen_listing_ids:
            return None
        
        # Classify part category
        category = self._classify_part(title)
        
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
            'vehicle_category': self._get_vehicle_category(category),
            'part_category': category,
        }
        
        return listing

    def _is_excluded(self, title: str) -> bool:
        """Check if listing should be excluded (complete vehicles, non-parts)."""
        title_lower = title.lower()
        for kw in self.EXCLUDE_KEYWORDS:
            if kw in title_lower:
                return True
        return False

    def _classify_part(self, title: str) -> str:
        """Classify part into one of the 5 categories + generic."""
        title_lower = title.lower()
        
        # Check for specific vehicle type in title
        if any(kw in title_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'e bike', 'bicicleta eléctrica', 'bicicleta electrica']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in title_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico', 'motorina eléctrica', 'motorina electrica']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard', 'monociclo', 'unicycle']):
            return 'Repuesto Patinete'
        elif any(kw in title_lower for kw in ['triciclo', 'mototrina', 'mototrin']):
            return 'Repuesto Mototrina'
        elif any(kw in title_lower for kw in ['bicicleta ', 'bicicletas ', 'bici ', ' mtb', 'mountain bike', 'huffy', 'vivamax', 'spiderman', 'equilibrio', 'aro 26', 'aro 29', 'aro 27', 'aro 24', 'aro 20']):
            return 'Repuesto Bicicleta'
        elif any(kw in title_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas', 'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor', 'bicimoto', 'bicimotos', 'bici moto', 'bici-moto']):
            return 'Repuesto Moto'
        
        # Check for specific part keywords
        part_keywords = {
            'Repuesto Moto': ['motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia', 'freno moto', 'freno moto ', 'llanta moto', 'neumático moto', 'cadena moto', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto', 'bujia moto', 'bobina moto', 'carburador moto', 'cigueñal', 'ciguenal', 'biela', 'embrague', 'variador', 'piñon', 'corona', 'filtro', 'aceite', 'bujía', 'bujia'],
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
        """Map part category to vehicle category."""
        mapping = {
            'Repuesto Moto': 'Moto Combustión',
            'Repuesto Bicicleta': 'Bicicleta',
            'Repuesto Moto Eléctrica': 'Moto Eléctrica',
            'Repuesto Bicicleta Eléctrica': 'Bicicleta Eléctrica',
            'Repuesto Patinete': 'Patinete Eléctrico',
            'Repuesto Generico': 'Otro',
        }
        return mapping.get(part_category, 'Otro')

    def filter_listing(self, listing: Dict) -> bool:
        """Filter listing - keep only parts, exclude complete vehicles."""
        title = listing.get('title', '')
        
        # Check if excluded
        if self._is_excluded(listing.get('title', '')):
            return False
        
        # Price validation
        price = listing.get('price_usd')
        if price is not None:
            cat = listing.get('part_category', 'Repuesto Generico')
            filters = self.PRICE_FILTERS.get(cat, {'min': 1, 'max': 2000})
            if price < filters['min'] or price > filters['max']:
                return False
        
        return True

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
        
        # Find all listing card starts
        card_pattern = r'<div[^>]*class="rtcl-listing-card it-app listing-item rtcl-listing-item[^"]*"'
        card_starts = [(m.start(), m.end()) for m in re.finditer(card_pattern, html)]
        
        # Extract each card by finding from one start to the next start
        cards = []
        for i, (start, end) in enumerate(card_starts):
            if i + 1 < len(card_starts):
                card_html = html[start:card_starts[i+1][0]]
            else:
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
        
        # Check for excluded items (complete vehicles)
        if self._is_excluded(title):
            return None
        
        # Image
        img_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="rtcl-thumbnail"', card_html)
        image = img_match.group(1) if img_match else None
        
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
        
        # Location
        loc_match = re.search(r'<li class="rt-location"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', card_html, re.DOTALL)
        location = re.sub(r'<[^>]+>', '', loc_match.group(1)).strip() if loc_match else None
        
        # Category
        cat_match = re.search(r'<li class="rt-categories"[^>]*>.*?<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', card_html, re.DOTALL)
        category = re.sub(r'<[^>]+>', '', cat_match.group(1)).strip() if cat_match else None
        
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
        
        # Post ID
        post_id_match = re.search(r'post-(\d+)', card_html)
        post_id = post_id_match.group(1) if post_id_match else None
        
        if post_id and post_id in self.seen_listing_ids:
            return None
        
        # Classify part category
        category = self._classify_part(title)
        
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
            'vehicle_category': self._get_vehicle_category(category),
            'part_category': category,
        }
        
        return listing

    def _is_excluded(self, title: str) -> bool:
        """Check if listing should be excluded (complete vehicles, non-parts)."""
        title_lower = title.lower()
        for kw in self.EXCLUDE_KEYWORDS:
            if kw in title_lower:
                return True
        return False

    def _classify_part(self, title: str) -> str:
        """Classify part into one of the 5 categories + generic."""
        title_lower = title.lower()
        
        # Check for specific vehicle type in title
        if any(kw in title_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'e bike', 'bicicleta eléctrica', 'bicicleta electrica']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in title_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico', 'motorina eléctrica', 'motorina electrica']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard', 'monociclo', 'unicycle']):
            return 'Repuesto Patinete'
        elif any(kw in title_lower for kw in ['triciclo', 'mototrina', 'mototrin']):
            return 'Repuesto Mototrina'
        elif any(kw in title_lower for kw in ['bicicleta ', 'bicicletas ', 'bici ', ' mtb', 'mountain bike', 'huffy', 'vivamax', 'spiderman', 'equilibrio', 'aro 26', 'aro 29', 'aro 27', 'aro 24', 'aro 20']):
            return 'Repuesto Bicicleta'
        elif any(kw in title_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas', 'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor', 'bicimoto', 'bicimotos', 'bici moto', 'bici-moto']):
            return 'Repuesto Moto'
        
        # Check for specific part keywords
        part_keywords = {
            'Repuesto Moto': ['motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia', 'freno moto', 'freno moto ', 'llanta moto', 'neumático moto', 'cadena moto', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto', 'bujia moto', 'bobina moto', 'carburador moto', 'cigueñal', 'ciguenal', 'biela', 'embrague', 'variador', 'piñon', 'corona', 'filtro', 'aceite', 'bujía', 'bujia'],
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
        """Map part category to vehicle category."""
        mapping = {
            'Repuesto Moto': 'Moto Combustión',
            'Repuesto Bicicleta': 'Bicicleta',
            'Repuesto Moto Eléctrica': 'Moto Eléctrica',
            'Repuesto Bicicleta Eléctrica': 'Bicicleta Eléctrica',
            'Repuesto Patinete': 'Patinete Eléctrico',
            'Repuesto Generico': 'Otro',
        }
        return mapping.get(part_category, 'Otro')

    def filter_listing(self, listing: Dict) -> bool:
        """Filter listing - keep only parts, exclude complete vehicles."""
        title = listing.get('title', '')
        
        # Check if excluded
        if self._is_excluded(listing.get('title', '')):
            return False
        
        # Price validation
        price = listing.get('price_usd')
        if price is not None:
            cat = listing.get('part_category', 'Repuesto Generico')
            filters = self.PRICE_FILTERS.get(cat, {'min': 1, 'max': 2000})
            if price < filters['min'] or price > filters['max']:
                return False
        
        return True

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

    def save_page_data(self, page: int, html: str, listings: List[Dict]):
        source_dir = self._ensure_source_dir()
        
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps({
            'listings': listings,
            'page': page,
            'total_on_page': len(listings)
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        
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
        for listing in listings:
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
        print(f"Filtering for repuestos only, excluding complete vehicles...")
        
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
            
            # Rate limiting
            time.sleep(1.5)
        
        self.save_manifest()
        print("\nSaving final filtered listings...")
        self.save_final_listings()
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique repuesto listings: {len(self.all_listings)}")


if __name__ == "__main__":
    scraper = ItencelRepuestosScraper(max_pages=50)
    scraper.run()