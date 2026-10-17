#!/usr/bin/env python3
"""
Revolico Repuestos Scraper
Extracts motorcycle/bicycle spare parts listings from revolico.com
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
from typing import Dict, List, Any, Optional
from collections import defaultdict

RAIZ = Path(__file__).resolve().parents[2]

ssl._create_default_https_context = ssl._create_unverified_context


class RevolicoRepuestosScraper:
    BASE_URL = "https://www.revolico.com/search"
    CATEGORY = "repuestos-accesorios"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Price filters (USD)
    PRICE_FILTERS = {
        'Repuesto Moto': {'min': 1, 'max': 5000},
        'Repuesto Bicicleta': {'min': 1, 'max': 2000},
        'Repuesto Moto Eléctrica': {'min': 1, 'max': 3000},
        'Repuesto Bicicleta Eléctrica': {'min': 1, 'max': 2000},
        'Repuesto Patinete': {'min': 1, 'max': 1000},
        'Repuesto Generico': {'min': 1, 'max': 1000},
    }

    def __init__(self, output_base: str = str(RAIZ), max_pages: int = 100):
        self.output_base = Path(str(RAIZ))
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"revolico_repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "revolico.com",
            "source_url": f"{self.BASE_URL}?category={self.CATEGORY}",
            "category_hint": "repuestos",
            "scraped_at": datetime.now().isoformat(),
            "scraper_version": "1.0",
            "pages": [],
            "totals": {"pages_processed": 0, "listings_extracted": 0, "listings_by_category": defaultdict(int)}
        }
        self.seen_listing_ids: set = set()
        self.all_listings: List[Dict] = []

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = self._get_page_params(page)
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

    def _get_page_params(self, page: int) -> Dict:
        params = {"category": self.CATEGORY}
        if page > 1:
            params["page"] = page
        return params

    def parse_next_data(self, html: str) -> Optional[Dict]:
        match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

    def extract_apollo_data(self, next_data: Dict) -> Dict[str, Any]:
        apollo = next_data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})
        
        provinces = {}
        municipalities = {}
        images = {}
        phones = {}
        ad_edges = []
        
        for key, value in apollo.items():
            if not isinstance(value, dict):
                continue
            typename = value.get('__typename')
            if typename == 'ProvinceType':
                provinces[value['id']] = value
            elif typename == 'MunicipalityType':
                municipalities[value['id']] = value
            elif typename == 'ImageType':
                images[value.get('gcsKey', '')] = value
            elif typename == 'Phone':
                phone_key = f"{value.get('prefix', '')}{value.get('number', '')}"
                phones[phone_key] = value
            elif typename == 'AdTypeESEdge':
                ad_edges.append(value)
        
        # Cache for this session
        self.province_cache = {k: v['name'] for k, v in provinces.items()}
        self.municipality_cache = {k: v['name'] for k, v in municipalities.items()}
        
        # Resolve ads
        ads = []
        for edge in ad_edges:
            node_ref = edge.get('node', {})
            if isinstance(node_ref, dict) and '__ref' in node_ref:
                ad_key = node_ref['__ref']
                if ad_key in apollo:
                    ad = apollo[ad_key]
                    resolved = self._resolve_ad(ad, provinces, municipalities, images, phones)
                    ads.append(resolved)
        
        return {
            'ads': ads,
            'provinces': provinces,
            'municipalities': municipalities
        }

    def _resolve_ad(self, ad: Dict, provinces: Dict, municipalities: Dict, images: Dict, phones: Dict) -> Dict:
        prov_id = ad.get('provinceId')
        mun_id = ad.get('municipalityId')
        province_name = provinces.get(prov_id, {}).get('name', '') if prov_id else ''
        municipality_name = municipalities.get(mun_id, {}).get('name', '') if mun_id else ''
        
        main_img = ad.get('mainImage', {})
        img_key = main_img.get('gcsKey', '') if isinstance(main_img, dict) else ''
        img_url = f"https://storage.googleapis.com/revolico-ads/{img_key}" if img_key else None
        
        phone_info = ad.get('phoneInfo', {})
        first_phone = phone_info.get('firstPhone', {})
        second_phone = phone_info.get('secondPhone')
        
        def format_phone(p):
            if not p or not isinstance(p, dict):
                return None
            return f"{p.get('prefix', '')} {p.get('number', '')}".strip()
        
        # Category classification
        category = self._classify_part(ad.get('title', ''))
        
        # Price validation
        price = ad.get('price')
        currency = ad.get('currency', 'USD')
        price_usd = price if currency == 'USD' else (price * 0.024 if price else None)
        
        return {
            'source_id': self.source_id,
            'source_url': f"https://www.revolico.com{ad.get('permalink', '')}",
            'scraped_at': datetime.now().isoformat(),
            'listing_id': ad.get('id'),
            'title': ad.get('title', ''),
            'price': price,
            'currency': currency,
            'price_usd': price_usd,
            'permalink': ad.get('permalink', ''),
            'images_count': ad.get('imagesCount', 0),
            'main_image_url': img_url,
            'updated_at': ad.get('updatedOnToOrder'),
            'is_promoted': ad.get('isPromoted', False),
            'province_id': prov_id,
            'province_name': province_name,
            'municipality_id': mun_id,
            'municipality_name': municipality_name,
            'view_count': ad.get('viewCount', 0),
            'contact_info_type': ad.get('contactInfo'),
            'phone_1': format_phone(first_phone),
            'phone_2': format_phone(second_phone) if second_phone else None,
            'phone_1_whatsapp': first_phone.get('isWhatsapp', False) if isinstance(first_phone, dict) else False,
            'category_detected': category,
            'raw_ad': ad
        }

    def _classify_part(self, title: str) -> str:
        """Classify part into one of the 5 categories + generic."""
        title_lower = title.lower()
        
        # Check for specific vehicle type in title
        if any(kw in title_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'bici eléctrica']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in title_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard']):
            return 'Repuesto Patinete'
        elif any(kw in title_lower for kw in ['triciclo', 'mototrina', 'mototrin']):
            return 'Repuesto Mototrina'
        elif any(kw in title_lower for kw in ['bicicleta ', 'bicicletas ', 'bici ', 'mtb', 'mountain bike', 'aro 26', 'aro 29', 'aro 27', 'huffy', 'vivamax']):
            return 'Repuesto Bicicleta'
        elif any(kw in title_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motoneta', 'scooter', 'bicimoto', 'bici moto', 'bici-moto']):
            return 'Repuesto Moto'
        
        # Check for specific part keywords
        part_keywords = {
            'Repuesto Moto': ['motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia', 'freno', 'freno ', 'llanta moto', 'neumático moto', 'cadena moto', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto', 'bobina moto', 'carburador moto'],
            'Repuesto Bicicleta': ['aro ', 'llanta bici', 'neumático bici', 'cadena bici', 'piñon bici', 'freno bici', 'pastilla bici', 'manillar bici', 'sillin bici', 'pedal bici', 'cambio bici', 'desviador'],
            'Repuesto Moto Eléctrica': ['batería moto', 'bateria moto', 'controlador moto', 'motor eléctrico moto', 'cargador moto', 'controlador moto'],
            'Repuesto Bicicleta Eléctrica': ['batería bici', 'bateria bici', 'controlador bici', 'motor eléctrico bici', 'cargador bici', 'controlador bici'],
            'Repuesto Patinete': ['patinete', 'patineta', 'hoverboard', 'monociclo'],
        }
        
        title_lower = title.lower()
        for category, keywords in part_keywords.items():
            for kw in keywords:
                if kw in title_lower:
                    return category
        
        return 'Repuesto Generico'

    def _is_rental(self, title: str) -> bool:
        rental_keywords = ['arriendo', 'alquiler', 'renta', 'rent', 'lease', 'se alquila', 'se arrienda']
        title_lower = title.lower()
        return any(kw in title_lower for kw in rental_keywords)

    def _is_price_outlier(self, category: str, price_usd: Optional[float]) -> bool:
        if price_usd is None:
            return True
        filters = self.PRICE_FILTERS.get(category, {'min': 1, 'max': 5000})
        return price_usd < filters['min'] or price_usd > filters['max']

    def filter_listings(self, ads: List[Dict]) -> tuple[List[Dict], Dict[str, int]]:
        filtered = []
        stats = {'total': len(ads), 'rentals': 0, 'outliers': 0, 'no_price': 0, 'by_category': defaultdict(int)}
        
        for ad in ads:
            if self._is_rental(ad['title']):
                stats['rentals'] += 1
                continue
            
            cat = ad['category_detected']
            price_usd = ad['price_usd']
            
            if price_usd is None:
                stats['no_price'] += 1
                continue
            
            if self._is_price_outlier(cat, price_usd):
                stats['outliers'] += 1
                continue
            
            filtered.append(ad)
            stats['by_category'][cat] += 1
        
        stats['kept'] = len(filtered)
        return filtered, stats

    def _ensure_source_dir(self) -> Path:
        source_dir = self.output_base / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def fetch_page(self, page: int) -> Optional[str]:
        params = self._get_page_params(page)
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

    def _get_page_params(self, page: int) -> Dict:
        params = {"category": self.CATEGORY}
        if page > 1:
            params["page"] = page
        return params

    def save_page_data(self, page: int, html: str, extracted: Dict, stats: Dict):
        source_dir = self._ensure_source_dir()
        
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps(extracted, ensure_ascii=False, indent=2), encoding='utf-8')
        
        page_manifest = {
            "page": page,
            "url": f"{self.BASE_URL}?category={self.CATEGORY}&page={page}",
            "status": 200,
            "html_file": f"page_{page:04d}.html",
            "json_file": f"extracted_{page:04d}.json",
            "listings_found": stats['total'],
            "listings_rentals": stats['rentals'],
            "listings_outliers": stats['outliers'],
            "listings_no_price": stats['no_price'],
            "listings_kept": stats['kept'],
            "listings_by_category": dict(stats['by_category']),
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
        print(f"Filtering for repuestos only, excluding vehicles...")
        
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
            
            next_data = self.parse_next_data(html)
            if not next_data:
                print(f"  No __NEXT_DATA__ on page {page}, stopping.")
                break
            
            extracted = self.extract_apollo_data(next_data)
            ads = extracted['ads']
            
            if not ads:
                print(f"  No ads found on page {page}, stopping.")
                break
            
            print(f"  Found {len(ads)} ads")
            
            filtered_ads, stats = self.filter_listings(ads)
            print(f"  After filters: {stats['kept']} kept (rentals: {stats['rentals']}, outliers: {stats['outliers']}, no_price: {stats['no_price']})")
            for cat, count in stats['by_category'].items():
                print(f"    {cat}: {count}")
            
            # Update extracted with filtered ads
            extracted['ads'] = filtered_ads
            extracted['filter_stats'] = stats
            
            self.save_page_data(page, html, extracted, stats)
            
            # Check if there are more pages
            apollo = next_data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})
            query_key = [k for k in apollo.keys() if k.startswith('adsPerPage(') and 'page' in k]
            if query_key:
                page_info = apollo[query_key[0]].get('pageInfo', {})
                if not page_info.get('hasNextPage', False):
                    print("  No more pages.")
                    break
            
            # Rate limiting
            time.sleep(1.5)
        
        self.save_manifest()
        print("\nSaving final filtered listings...")
        self.save_final_listings()
        print(f"\nScraping complete! Source ID: {self.source_id}")
        print(f"Total unique repuesto listings: {len(self.all_listings)}")


if __name__ == "__main__":
    scraper = RevolicoRepuestosScraper(max_pages=100)
    scraper.run()