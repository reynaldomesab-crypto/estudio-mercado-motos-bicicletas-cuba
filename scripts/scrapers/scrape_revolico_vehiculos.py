#!/usr/bin/env python3
"""
Revolico Vehículos Scraper
Extracts vehicle listings from revolico.com and categorizes them into:
- Carro (cars)
- Motos_Bici (motorcycles, scooters, electric bikes)
- Triciclo (tricycles)

Saves raw HTML and extracted JSON per page, organized by category.
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


class RevolicoScraper:
    BASE_URL = "https://www.revolico.com/search"
    CATEGORY = "vehiculos"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Category classification keywords
    CATEGORY_KEYWORDS = {
        'Carro': [
            'carro', 'auto', 'automóvil', 'automovil', 'sedan', 'hatchback',
            'suv', 'pickup', 'camioneta', 'van', 'minivan', 'coupe',
            'convertible', 'wagon', 'familiar', 'kia', 'hyundai', 'toyota',
            'honda', 'nissan', 'mitsubishi', 'suzuki', 'chevrolet', 'ford',
            'volkswagen', 'peugeot', 'renault', 'fiat', 'citroen', 'bmw',
            'mercedes', 'audi', 'volvo', 'jeep', 'land rover', 'lexus'
        ],
        'Motos_Bici': [
            'moto', 'motocicleta', 'scooter', 'scuter', 'motorina', 'ciclomotor',
            'bicicleta', 'bici', 'eléctrica', 'electrica', 'bicicleta eléctrica',
            'bici eléctrica', 'ebike', 'e-bike', 'patinete', 'patineta',
            'hoverboard', 'monociclo', 'unicycle', 'yamaha', 'honda moto',
            'suzuki moto', 'kawasaki', 'ktm', 'ducati', 'harley', 'bj',
            'keeway', 'znen', 'loncin', 'lifan', 'cg125', 'cg150', 'cg200',
            'cg250', 'xr150', 'xr250', 'crf', 'wr', 'yzf', 'r15', 'r3',
            'mt07', 'mt09', 'r1', 'r6', 'cbr', 'cbf', 'cb125', 'cb190',
            'cb300', 'cb500', 'cb650', 'cb1000', 'hornet', 'shadow',
            'vstrom', 'v-strom', 'gsx', 'gsxr', 'hayabusa', 'bandit',
            'ninja', 'zx6r', 'zx10r', 'z900', 'z650', 'versys', 'vulcan',
            'duke', 'rc390', 'rc125', 'adventure', 'enduro', 'cross',
            'motard', 'supermoto', 'trail', 'dual sport'
        ],
        'Triciclo': [
            'triciclo', 'tricycle', 'tres ruedas', '3 ruedas', 'carguero',
            'triciclo de carga', 'triciclo eléctrico', 'triciclo electrico',
            'rickshaw', 'tuk tuk', 'tuk-tuk', 'tricar', 'mototaxi'
        ]
    }

    # Price outlier thresholds (USD)
    PRICE_FILTERS = {
        'Carro': {'min': 100, 'max': 500000},
        'Motos_Bici': {'min': 50, 'max': 50000},
        'Triciclo': {'min': 100, 'max': 30000},
    }

    def __init__(self, output_base: str = str(RAIZ), max_pages: int = 300):
        self.output_base = Path(output_base)
        self.max_pages = max_pages
        self.session_start = datetime.now().isoformat()
        self.source_id = f"revolico_vehiculos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest = {
            "source_id": self.source_id,
            "source_name": "revolico.com",
            "source_url": f"{self.BASE_URL}?category={self.CATEGORY}",
            "category_hint": "vehiculos",
            "scraped_at": self.session_start,
            "scraper_version": "1.0",
            "pages": [],
            "totals": {"pages_processed": 0, "listings_extracted": 0, "listings_by_category": defaultdict(int)}
        }
        self.province_cache: Dict[str, str] = {}
        self.municipality_cache: Dict[str, str] = {}
        self._load_geo_cache()

    def _load_geo_cache(self):
        """Load province/municipality from first page."""
        pass  # Will be populated from first page

    def fetch_page(self, page: int) -> Optional[str]:
        """Fetch a single page HTML."""
        params = {"category": self.CATEGORY, "page": page}
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

    def parse_next_data(self, html: str) -> Optional[Dict]:
        """Extract __NEXT_DATA__ JSON from page."""
        match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

    def extract_apollo_data(self, next_data: Dict) -> Dict[str, Any]:
        """Extract and resolve all data from Apollo state."""
        apollo = next_data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})
        
        # Build reference maps
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
        
        # Find Query object with adsPerPage
        for key, value in apollo.items():
            if isinstance(value, dict) and value.get('__typename') == 'Query':
                for qk, qv in value.items():
                    if isinstance(qv, dict) and 'adsPerPage' in qk and 'edges' in qv:
                        ad_edges = qv['edges']
                        break
        
        # Cache for this session
        self.province_cache.update({k: v['name'] for k, v in provinces.items()})
        self.municipality_cache.update({k: v['name'] for k, v in municipalities.items()})
        
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
        """Resolve all references in an ad."""
        # Province/Municipality names
        prov_id = ad.get('provinceId')
        mun_id = ad.get('municipalityId')
        province_name = provinces.get(prov_id, {}).get('name', '') if prov_id else ''
        municipality_name = municipalities.get(mun_id, {}).get('name', '') if mun_id else ''
        
        # Main image
        main_img = ad.get('mainImage', {})
        img_key = main_img.get('gcsKey', '') if isinstance(main_img, dict) else ''
        img_url = f"https://storage.googleapis.com/revolico-ads/{img_key}" if img_key else None
        
        # Phone info
        phone_info = ad.get('phoneInfo', {})
        first_phone = phone_info.get('firstPhone', {})
        second_phone = phone_info.get('secondPhone')
        
        def format_phone(p):
            if not p or not isinstance(p, dict):
                return None
            return f"{p.get('prefix', '')} {p.get('number', '')}".strip()
        
        # Category classification
        category = self._classify_category(ad.get('title', ''), ad.get('price'))
        
        # Price validation
        price = ad.get('price')
        currency = ad.get('currency', 'USD')
        price_usd = price if currency == 'USD' else (price * 0.024 if price else None)  # Rough CUP->USD
        
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
            'raw_ad': ad  # Keep original for reference
        }

    def _classify_category(self, title: str, price: Optional[float]) -> str:
        """Classify listing into Carro, Motos_Bici, or Triciclo."""
        title_lower = title.lower()
        
        # Score each category
        scores = defaultdict(int)
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    scores[cat] += 1
        
        # Price-based hints
        if price:
            if price > 5000:
                scores['Carro'] += 2
            elif price < 500:
                scores['Motos_Bici'] += 1
                scores['Triciclo'] += 1
        
        if scores:
            return max(scores, key=scores.get)
        return 'Motos_Bici'  # Default

    def _is_rental(self, title: str) -> bool:
        """Detect rental listings."""
        rental_keywords = ['arriendo', 'alquiler', 'renta', 'rent', 'lease', 'se alquila', 'se arrienda']
        title_lower = title.lower()
        return any(kw in title_lower for kw in rental_keywords)

    def _is_price_outlier(self, category: str, price_usd: Optional[float]) -> bool:
        """Check if price is an outlier for the category."""
        if price_usd is None:
            return True
        filters = self.PRICE_FILTERS.get(category, {'min': 0, 'max': float('inf')})
        return price_usd < filters['min'] or price_usd > filters['max']

    def filter_ads(self, ads: List[Dict]) -> tuple[List[Dict], Dict[str, int]]:
        """Filter out rentals and price outliers."""
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
        """Ensure source directory exists."""
        source_dir = self.output_base / "Carro" / "data" / "raw" / "scraped" / self.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    def save_page_data(self, page: int, html: str, extracted: Dict, stats: Dict):
        """Save raw HTML and extracted data for a page."""
        source_dir = self._ensure_source_dir()
        
        # Save raw HTML
        html_file = source_dir / f"page_{page:04d}.html"
        html_file.write_text(html, encoding='utf-8')
        
        # Save extracted JSON
        json_file = source_dir / f"extracted_{page:04d}.json"
        json_file.write_text(json.dumps(extracted, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # Update manifest
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
        """Save manifest file."""
        source_dir = self._ensure_source_dir()
        manifest_file = source_dir / "manifest.json"
        
        # Convert defaultdict to dict
        manifest_copy = self.manifest.copy()
        manifest_copy['totals']['listings_by_category'] = dict(manifest_copy['totals']['listings_by_category'])
        manifest_copy['completed_at'] = datetime.now().isoformat()
        
        manifest_file.write_text(json.dumps(manifest_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Manifest saved: {manifest_file}")

    def distribute_by_category(self):
        """Copy filtered ads to their respective category directories."""
        source_dir = self.output_base / "Carro" / "data" / "raw" / "scraped" / self.source_id
        
        # Read all extracted files
        all_ads = []
        for json_file in sorted(source_dir.glob("extracted_*.json")):
            data = json.loads(json_file.read_text(encoding='utf-8'))
            all_ads.extend(data['ads'])
        
        # Group by category
        by_category = defaultdict(list)
        for ad in all_ads:
            cat = ad['category_detected']
            # Create category-specific record (without raw_ad to save space)
            record = {k: v for k, v in ad.items() if k != 'raw_ad'}
            by_category[cat].append(record)
        
        # Save to each category's raw/scraped
        for cat, ads in by_category.items():
            if cat not in ['Carro', 'Motos_Bici', 'Triciclo']:
                continue
            cat_dir = self.output_base / cat / "data" / "raw" / "scraped" / self.source_id
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            out_file = cat_dir / f"listings_{cat.lower()}.json"
            out_file.write_text(json.dumps(ads, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Category manifest
            cat_manifest = {
                "source_id": self.source_id,
                "category": cat,
                "source_file": f"listings_{cat.lower()}.json",
                "total_listings": len(ads),
                "extracted_at": datetime.now().isoformat(),
                "parent_manifest": str(source_dir / "manifest.json")
            }
            (cat_dir / "manifest.json").write_text(json.dumps(cat_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            
            print(f"  {cat}: {len(ads)} listings saved to {out_file}")

    def run(self):
        """Main scraping loop."""
        print(f"Starting scrape: {self.source_id}")
        print(f"Target: {self.max_pages} pages from {self.BASE_URL}?category={self.CATEGORY}")
        
        for page in range(1, self.max_pages + 1):
            print(f"\n--- Page {page}/{self.max_pages} ---")
            
            html = self.fetch_page(page)
            if not html:
                print(f"  Failed to fetch page {page}, stopping.")
                break
            
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
            
            filtered_ads, stats = self.filter_ads(ads)
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
        print("\nDistributing by category...")
        self.distribute_by_category()
        print(f"\nScraping complete! Source ID: {self.source_id}")


if __name__ == "__main__":
    scraper = RevolicoScraper(max_pages=300)
    scraper.run()