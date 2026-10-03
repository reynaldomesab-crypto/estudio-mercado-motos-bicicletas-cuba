#!/usr/bin/env python3
"""
Clase base para scrapers - Funcionalidad común compartida
"""

import urllib.request
import urllib.parse
import ssl
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from abc import ABC, abstractmethod

ssl._create_default_https_context = ssl._create_unverified_context


class BaseScraper(ABC):
    """Clase base abstracta para todos los scrapers."""
    
    BASE_URL: str = ""
    HEADERS: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    
    def __init__(self, output_base: str = "/home/reynaldomesab/Project/motos_bicis_project", max_pages: int = 100):
        self.output_base = Path(output_base)
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": self.__class__.__name__,
            "source_url": self.BASE_URL,
            "category_hint": getattr(self, 'CATEGORY_HINT', 'unknown'),
            "scraped_at": self.session_start,
            "scraper_version": "1.0",
            "pages": [],
            "totals": {"pages_processed": 0, "listings_extracted": 0, "listings_by_category": defaultdict(int)}
        }
        self.seen_listing_ids: Set[str] = set()
        self.all_listings: List[Dict] = []
    
    @property
    @abstractmethod
    def BASE_URL(self) -> str:
        pass
    
    @property
    @abstractmethod
    def CATEGORY_HINT(self) -> str:
        pass
    
    @abstractmethod
    def extract_listings_from_page(self, html: str) -> List[Dict]:
        """Extraer listings de una página HTML. Debe implementarse en cada scraper."""
        pass
    
    @abstractmethod
    def filter_listing(self, listing: Dict) -> bool:
        """Filtrar un listing según criterios del scraper."""
        pass
    
    def _ensure_source_dir(self) -> Path:
        """Asegurar que existe el directorio de salida."""
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir
    
    def fetch_page(self, page: int) -> Optional[str]:
        """Obtener HTML de una página."""
        params = self._get_page_params(page)
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}" if params else self.BASE_URL
        
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
    
    @abstractmethod
    def _get_page_params(self, page: int) -> Dict:
        """Obtener parámetros de URL para una página."""
        pass
    
    def save_page_data(self, page: int, html: str, listings: List[Dict]):
        """Guardar HTML raw y datos extraídos de una página."""
        source_dir = self._ensure_source_dir()
        
        # Guardar HTML raw
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        # Guardar JSON extraído
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps({
            'listings': listings,
            'page': page,
            'total_on_page': len(listings)
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # Actualizar manifest
        page_manifest = {
            "page": page,
            "url": self._get_page_url(page),
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
            cat = listing.get('vehicle_type', 'Unknown')
            self.manifest['totals']['listings_by_category'][cat] += 1
    
    @abstractmethod
    def _get_page_url(self, page: int) -> str:
        pass
    
    def save_manifest(self):
        """Guardar archivo manifest."""
        source_dir = self._ensure_source_dir()
        manifest_file = source_dir / "manifest.json"
        
        manifest_copy = self.manifest.copy()
        manifest_copy['totals']['listings_by_category'] = dict(manifest_copy['totals']['listings_by_category'])
        manifest_copy['completed_at'] = datetime.now().isoformat()
        manifest_copy['unique_listings'] = len(self.seen_listing_ids)
        
        manifest_file.write_text(json.dumps(manifest_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Manifest saved: {manifest_file}")
    
    def save_final_listings(self, category_dir_name: str, listings_filename: str):
        """Guardar listings finales en directorio de categoría."""
        cat_dir = self.output_base / category_dir_name / "data" / "raw" / "scraped" / self.source_id
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        out_file = cat_dir / listings_filename
        out_file.write_text(json.dumps(self.all_listings, ensure_ascii=False, indent=2), encoding='utf-8')
        
        cat_manifest = {
            "source_id": self.source_id,
            "category": category_dir_name,
            "source_file": listings_filename,
            "total_listings": len(self.all_listings),
            "extracted_at": datetime.now().isoformat(),
            "parent_manifest": str(self._ensure_source_dir() / "manifest.json")
        }
        (cat_dir / "manifest.json").write_text(json.dumps(cat_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"  {category_dir_name}: {len(self.all_listings)} listings saved to {out_file}")
    
    def run(self):
        """Loop principal de scraping."""
        print(f"Starting scrape: {self.source_id}")
        print(f"Target: up to {self.max_pages} pages from {self.BASE_URL}")
        
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
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique listings: {len(self.all_listings)}")
    
    def fetch_page(self, page: int) -> Optional[str]:
        """Fetch a single page HTML."""
        params = self._get_page_params(page)
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}" if params else self.BASE_URL
        
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


class VehicleScraperMixin:
    """Mixin para scrapers de vehículos con filtrado común."""
    
    # Palabras clave para detectar vehículos
    VEHICLE_KEYWORDS = {
        'moto_combustion': [
            'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
            'motoneta', 'motonetas', 'scooter', 'scooters',
            'ciclomotor', 'ciclomotores', 'bicimoto', 'bicimotos',
            'bici moto', 'bici-moto', 'moto de', 'moto ',
        ],
        'moto_electrica': [
            'moto eléctrica', 'moto electrica', 'motorina eléctrica',
            'bicimoto eléctrica', 'bicimoto eléctrica', 'scooter eléctrico',
            'moto eléctrica', 'bicimoto eléctrica', 'motocicleta eléctrica',
        ],
        'bicicleta': [
            'bicicleta ', 'bicicletas ', 'bici ', 'bicicleta de montaña',
            'mtb', 'mountain bike', 'bicicleta de paseo', 'bicicleta plegable',
            'bicicleta infantil', 'bicicleta para', 'aro 26', 'aro 29',
            'huffy', 'vivamax', 'equilibrio', 'balance bike',
        ],
        'bicicleta_electrica': [
            'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
            'e-bike', 'ebike', 'e bike', 'bici eléctrica',
            'bicicleta electrica', 'bici electrica',
        ],
        'patinete': [
            'patinete', 'patinetes', 'patineta', 'scooter eléctrico',
            'hoverboard', 'monociclo', 'unicycle',
        ],
    }
    
    # Palabras a excluir (partes, accesorios, no vehículos)
    EXCLUDE_KEYWORDS = [
        'repuesto', 'repuestos', 'accesorio', 'accesorios', 'pieza', 'piezas',
        'candado', 'bombín', 'bombin', 'inflador', 'bomba de aire',
        'cargador', 'batería', 'bateria', 'llanta', 'neumático',
        'pastilla', 'freno', 'frenos', 'cadena', 'piñon', 'corona',
        'espejo', 'retrovisor', 'candado', 'casco', 'guantes',
        'repuesto', 'repuestos', 'accesorio', 'accesorios',
        'batería', 'bateria', 'cargador', 'pastilla', 'llanta',
        'neumático', 'neumáticos', 'repuesto', 'kit',
    ]
    
    def _is_vehicle(self, title: str) -> bool:
        """Verificar si el título indica un vehículo."""
        title_lower = title.lower()
        for category, keywords in self.VEHICLE_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    return True
        return False
    
    def _is_part_or_accessory(self, title: str) -> bool:
        """Verificar si es una pieza/accesorio (no vehículo completo)."""
        title_lower = title.lower()
        for kw in self.EXCLUDE_KEYWORDS:
            if kw in title_lower:
                # Solo excluir si NO empieza con palabra de vehículo
                vehicle_starts = any(title.lower().startswith(v) for v in [
                    'moto ', 'motorina', 'motoneta', 'scooter', 'bicimoto',
                    'bicicleta ', 'bici ', 'patinete', 'triciclo'
                ])
                if not vehicle_starts:
                    return True
        return False
    
    def _is_triciclo(self, title: str) -> bool:
        """Verificar si es triciclo (excluir)."""
        title_lower = title.lower()
        return any(kw in title_lower for kw in ['triciclo', 'triciclos', 'mototrina', 'mototrin'])
    
    def filter_listing(self, listing: Dict) -> bool:
        """Filtro estándar para vehículos."""
        title = listing.get('title', '')
        
        # Debe ser un vehículo
        if not self._is_vehicle(title):
            return False
        
        # No debe ser triciclo
        if self._is_triciclo(title):
            return False
        
        # No debe ser pieza/accesorio suelto
        if self._is_part_or_accessory(title):
            return False
        
        return True
    
    def classify_vehicle_type(self, title: str) -> str:
        """Clasificar tipo de vehículo basado en título."""
        title_lower = title.lower()
        
        # Verificar cada categoría
        if any(kw in title_lower for kw in ['triciclo', 'mototrina', 'mototrin']):
            return 'Mototrina'
        
        if any(kw in title_lower for kw in ['patinete', 'patineta', 'hoverboard', 'monociclo']):
            return 'Patinete Eléctrico'
        
        if any(kw in title_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'e bike', 'bicicleta eléctrica', 'bicicleta electrica']):
            return 'Bicicleta Eléctrica'
        
        if any(kw in title_lower for kw in ['bicicleta ', 'bicicletas ', 'bici ', 'mtb', 'mountain bike', 'huffy', 'vivamax', 'aro 26', 'aro 29', 'aro 27']):
            return 'Bicicleta'
        
        if any(kw in title_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico']):
            return 'Moto Eléctrica'
        
        if any(kw in title_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motoneta', 'scooter', 'bicimoto', 'bici moto']):
            return 'Moto Combustión'
        
        return 'Otro'