#!/usr/bin/env python3
"""
Unified Spare Parts Processor
Processes spare parts from all sources (Revolico, itencel, ElYerro, Facebook)
into a unified curated dataset with 5 categories + generic.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict


class SparePartsProcessor:
    """Unified processor for spare parts from all sources."""

    # Standardized part categories (5 + generic)
    PART_CATEGORIES = [
        'Repuesto Moto',
        'Repuesto Bicicleta',
        'Repuesto Moto Eléctrica',
        'Repuesto Bicicleta Eléctrica',
        'Repuesto Patinete',
        'Repuesto Generico'
    ]

    # Vehicle category mapping
    VEHICLE_CATEGORY_MAP = {
        'Repuesto Moto': 'Moto Combustión',
        'Repuesto Bicicleta': 'Bicicleta',
        'Repuesto Moto Eléctrica': 'Moto Eléctrica',
        'Repuesto Bicicleta Eléctrica': 'Bicicleta Eléctrica',
        'Repuesto Patinete': 'Patinete Eléctrico',
        'Repuesto Generico': 'Otro',
    }

    # Part type taxonomy (extensible)
    PART_TYPES = {
        'motor': ['motor ', 'cilindro', 'pistón', 'piston', 'biela', 'cigueñal', 'ciguenal', 'embrague', 'variador'],
        'eléctrico': ['batería', 'bateria', 'cargador', 'controlador', 'ecu', 'cdi', 'bobina', 'estator', 'rotor', 'magneto'],
        'frenos': ['freno', 'frenos', 'pastilla', 'pastillas', 'disco', 'tambor', 'líquido de frenos', 'bomba de freno'],
        'transmisión': ['cadena', 'piñon', 'piñón', 'corona', 'cassette', 'cambio', 'desviador', 'shifter', 'embrague'],
        'suspensión': ['amortiguador', 'horquilla', 'horquillas', 'amortiguador ', 'horquilla ', 'resorte', 'muelle'],
        'ruedas': ['llanta', 'llantas', 'neumático', 'neumáticos', 'cubierta', 'cubiertas', 'cámara', 'camara', 'radio', 'radios'],
        'carrocería': ['carroceria', 'carrocería', 'tanque', 'deposito', 'depósito', 'asiento', 'sillin', 'sillín', 'manillar', 'puño', 'puños', 'espejo', 'espejos', 'farol', 'luz', 'luces', 'guardabarros', 'parrilla', 'portabultos'],
        'eléctrico_general': ['batería', 'bateria', 'cargador', 'bateria ', 'cargador ', 'acumulador', 'banco de baterias', 'banco de baterías'],
        'consumibles': ['aceite', 'aceite ', 'filtro', 'filtro ', 'bujía', 'bujia', 'bujía ', 'filtro de aceite', 'filtro de aire', 'filtro de gasolina', 'líquido refrigerante', 'líquido de frenos'],
        'herramientas': ['llave', 'llaves', 'destornillador', 'gato', 'elevador', 'compresor', 'bomba', 'bomba de aire', 'inflador'],
    }

    # Price filters per category (USD)
    PRICE_FILTERS = {
        'Repuesto Moto': {'min': 1, 'max': 3000},
        'Repuesto Bicicleta': {'min': 1, 'max': 2000},
        'Repuesto Moto Eléctrica': {'min': 1, 'max': 2000},
        'Repuesto Bicicleta Eléctrica': {'min': 1, 'max': 2000},
        'Repuesto Patinete': {'min': 1, 'max': 1000},
        'Repuesto Generico': {'min': 1, 'max': 1000},
    }

    def __init__(self, project_root: str = "/home/reynaldomesab/Project/motos_bicis_project"):
        self.project_root = Path(project_root)
        self.curated_dir = self.project_root / "data" / "curated"
        self.raw_base = self.project_root / "data" / "raw" / "scraped"

    def load_all_raw_data(self) -> List[Dict]:
        """Load all raw scraped data from all sources."""
        all_items = []
        
        # 1. Load from raw scraped extracted files
        for extracted_file in self.project_root.glob("data/raw/scraped/**/extracted_*.json"):
            try:
                with open(extracted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                items = data.get('listings', [])
                source_name = extracted_file.parent.name
                
                for item in items:
                    item['_source_file'] = str(extracted_file)
                    item['_source_name'] = extracted_file.parent.name
                    yield item
                    
            except Exception as e:
                print(f"Error loading {extracted_file}: {e}")
        
        # 2. Load from curated Facebook data
        facebook_curated = self.project_root / "data" / "curated" / "facebook_curated_*.json"
        for curated_file in self.project_root.glob("data/curated/facebook_curated_*.json"):
            try:
                with open(curated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                items = data.get('items', [])
                for item in items:
                    item['_source_file'] = str(curated_file)
                    item['_source_name'] = 'facebook'
                    yield item
            except Exception as e:
                print(f"Error loading {curated_file}: {e}")
        
        # 3. Load from curated motos_bicis data (has revolico, elyerro data)
        for curated_file in self.project_root.glob("data/curated/motos_bicis_curated*.json"):
            try:
                with open(curated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                items = data.get('items', [])
                for item in items:
                    item['_source_file'] = str(curated_file)
                    item['_source_name'] = item.get('source', 'curated')
                    yield item
            except Exception as e:
                print(f"Error loading {curated_file}: {e}")

    def classify_part_category(self, title: str, source_category: str = '') -> str:
        """
        Classify a listing into one of the 5 standard part categories.
        Uses title text and source category hint.
        """
        title_lower = title.lower()
        
        # Check for electric vehicle parts first (more specific)
        if any(kw in title_lower for kw in ['batería bici', 'bateria bici', 'cargador bici', 'controlador bici', 
                                               'motor eléctrico bici', 'motor electrico bici', 'batería litio bici',
                                               'bateria litio bici', 'lifepo4 bici', 'motor central bici', 'motor buje bici']):
            return 'Repuesto Bicicleta Eléctrica'
        
        if any(kw in title_lower for kw in ['batería moto', 'bateria moto', 'cargador moto', 'controlador moto',
                                               'controlador ', 'ecu moto', 'cdi moto', 'bobina moto', 'estator moto',
                                               'rotor moto', 'motor eléctrico moto', 'motor electrico moto',
                                               'batería litio moto', 'bateria litio moto', 'lifepo4 moto',
                                               'cargador moto', 'cargador de moto', 'controlador moto electrica']):
            return 'Repuesto Moto Eléctrica'
        
        if any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'scooter electrico',
                                               'hoverboard', 'monociclo', 'unicycle']):
            return 'Repuesto Patinete'
        
        # Check for electric bike parts
        if any(kw in title_lower for kw in ['batería bici', 'bateria bici', 'cargador bici', 'controlador bici',
                                               'motor eléctrico bici', 'motor electrico bici', 'batería litio bici',
                                               'bateria litio bici', 'lifepo4 bici', 'motor central bici',
                                               'motor buje bici', 'cargador bici', 'controlador bici electrica']):
            return 'Repuesto Bicicleta Eléctrica'
        
        if any(kw in title_lower for kw in ['batería moto', 'bateria moto', 'cargador moto', 'controlador moto',
                                               'controlador ', 'ecu moto', 'cdi moto', 'bobina moto', 'estator moto',
                                               'rotor moto', 'motor eléctrico moto', 'motor electrico moto',
                                               'batería litio moto', 'bateria litio moto', 'lifepo4 moto',
                                               'cargador moto', 'cargador de moto', 'controlador moto electrica']):
            return 'Repuesto Moto Eléctrica'
        
        if any(kw in title_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'scooter electrico',
                                               'hoverboard', 'monociclo', 'unicycle']):
            return 'Repuesto Patinete'
        
        # Check for regular bike parts
        if any(kw in title_lower for kw in ['aro ', 'llanta bici', 'neumático bici', 'cadena bici', 'piñon bici',
                                             'cambio bici', 'desviador', 'freno bici', 'manillar bici',
                                             'sillin bici', 'sillín bici', 'pedal bici', 'biela bici',
                                             'cuadro bici', 'horquilla bici', 'amortiguador bici', 'suspensión bici']):
            return 'Repuesto Bicicleta'
        
        # Check for regular moto parts
        if any(kw in title_lower for kw in ['motor ', 'cilindro', 'pistón', 'piston', 'carburador', 'bujía', 'bujia',
                                             'freno moto', 'freno moto ', 'llanta moto', 'neumático moto', 'cadena moto',
                                             'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto',
                                             'bujia moto', 'bobina moto', 'carburador moto', 'cigueñal', 'ciguenal',
                                             'biela', 'embrague', 'variador', 'piñon', 'corona', 'filtro', 'aceite',
                                             'bujía', 'bujia', 'bobina', 'carburador', 'cigueñal', 'ciguenal']):
            return 'Repuesto Moto'
        
        if any(kw in title_lower for kw in ['aro ', 'llanta bici', 'neumático bici', 'cadena bici', 'piñon bici',
                                             'cambio bici', 'desviador', 'freno bici', 'manillar bici', 'sillin bici',
                                             'sillín bici', 'pedal bici', 'biela bici', 'cuadro bici', 'horquilla bici',
                                             'amortiguador bici', 'suspensión bici', 'cambio bici', 'desviador bici',
                                             'freno bici', 'manillar bici', 'sillin bici', 'sillín bici', 'pedal bici',
                                             'biela bici', 'cuadro bici', 'horquilla bici', 'amortiguador bici']):
            return 'Repuesto Bicicleta'
        
        return 'Repuesto Generico'

    def normalize_vehicle_category(self, part_category: str) -> str:
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

    def classify_part(self, title: str, source_category: str = '') -> str:
        """Main classification method."""
        return self.classify_part_category(title)

    def is_valid_part(self, item: Dict) -> bool:
        """Validate if item is a legitimate spare part."""
        title = item.get('title', '')
        title_lower = title.lower()
        
        # Exclude complete vehicles
        exclude_terms = [
            'triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
            'bicicleta ', 'bicicletas ', 'bici ', ' ebike', 'e-bike', 'e bike',
            'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
            'patinete', 'patinetes', 'scooter eléctrico', 'hoverboard', 'monociclo',
            'carro', 'auto', 'automovil', 'automóvil',
            'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
            'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor',
            'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
        ]
        
        for kw in ['triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad']:
            if kw in title_lower:
                return False
        
        # Must have at least one part keyword
        part_keywords = ['repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
                         'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
                         'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
                         'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
                         'batería', 'bateria', 'controlador', 'motor eléctrico',
                         'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
                         'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
                         'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
                         'cargador para', 'cargador de', 'cargador ',
                         'batería ', 'bateria ', 'batería de', 'bateria de',
                         'extensor de rango', 'extensor de rango']
        
        # Must contain at least one part-related keyword
        has_part_kw = any(kw in title_lower for kw in [
            'repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
            'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
            'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
            'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
            'batería', 'bateria', 'controlador', 'motor eléctrico',
            'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
            'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
            'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
            'cargador para', 'cargador de', 'cargador ',
            'batería ', 'bateria ', 'batería de', 'bateria de',
            'extensor de rango', 'extensor de rango',
        ])
        
        return has_part_kw

    def standardize_item(self, raw_item: Dict) -> Optional[Dict]:
        """Convert raw item from any source to standardized format."""
        title = raw_item.get('title', '')
        if not title:
            return None
        
        if not self.is_valid_part(raw_item):
            return None
        
        # Classify part category
        part_category = self.classify_part_category(raw_item.get('title', ''))
        vehicle_category = self.normalize_vehicle_category(part_category)
        
        # Get price
        price_usd = raw_item.get('price_usd')
        if price_usd is None:
            price = raw_item.get('price')
            currency = raw_item.get('currency', 'USD')
            if price is not None:
                if currency == 'USD':
                    price_usd = price
                elif currency == 'CUP':
                    price_usd = price * 0.000417  # ~2400 CUP = 1 USD
                elif currency == 'ZELLE':
                    price_usd = price
                elif currency == 'EUR':
                    price_usd = price * 1.08
        
        # Validate price
        if price_usd is not None:
            filters = self.PRICE_FILTERS.get(part_category, {'min': 1, 'max': 2000})
            if price_usd < filters['min'] or price_usd > filters['max']:
                return None
        
        # Extract location
        location = raw_item.get('location') or raw_item.get('location_class') or ''
        if isinstance(location, str):
            location = location.replace('-', ' ').title()
        
        # Build standardized item
        return {
            'source': raw_item.get('source', 'unknown'),
            'source_id': raw_item.get('source_id', ''),
            'source_url': raw_item.get('source_url', raw_item.get('source_url', '')),
            'listing_id': raw_item.get('listing_id', raw_item.get('id', '')),
            'title': raw_item.get('title', ''),
            'price_original': raw_item.get('price'),
            'currency_original': raw_item.get('currency', 'USD'),
            'price_usd': price_usd,
            'currency': 'USD',
            'image': raw_item.get('image') or raw_item.get('main_image_url'),
            'location': location,
            'province': raw_item.get('province_name', ''),
            'municipality': raw_item.get('municipality_name', ''),
            'category': part_category,
            'vehicle_category': vehicle_category,
            'part_category': part_category,
            'date_text': raw_item.get('date_text', raw_item.get('updated_at', '')),
            'views': raw_item.get('views'),
            'badges': raw_item.get('badges', []),
            'scraped_at': raw_item.get('scraped_at', datetime.now().isoformat()),
            'source_post_id': raw_item.get('source_post_id', raw_item.get('post_id', '')),
            'listing_id': raw_item.get('listing_id', raw_item.get('id', '')),
            'source_file': raw_item.get('_source_file', ''),
            'source_name': raw_item.get('_source_name', raw_item.get('source', '')),
        }

    def process_all(self) -> Dict:
        """Process all raw data and return curated dataset."""
        all_items = []
        
        for item in self.load_all_raw_data():
            standardized = self.standardize_item(item)
            if standardized:
                all_items.append(standardized)
        
        print(f"Total standardized items: {len(all_items)}")
        
        # Stats
        types = Counter(item['part_category'] for item in all_items)
        vehicle_types = Counter(item['vehicle_category'] for item in all_items)
        sources = Counter(item['source'] for item in all_items)
        
        print(f"\nPart Categories: {dict(types)}")
        print(f"Vehicle Categories: {dict(vehicle_types)}")
        print(f"Sources: {dict(sources)}")
        
        # Price stats
        priced = [i for i in all_items if i['price_usd'] is not None]
        if priced:
            prices = [i['price_usd'] for i in priced]
            print(f"Priced items: {len(priced)}/{len(all_items)}")
            print(f"Price range: ${min(prices):,.0f} - ${max(prices):,.0f}")
            print(f"Avg price: ${sum(prices)/len(prices):,.0f}")
        
        # Save curated dataset
        output = {
            'source_id': 'unified_spare_parts',
            'source_name': 'Unified Spare Parts Dataset',
            'created_at': datetime.now().isoformat(),
            'total_items': len(all_items),
            'part_categories': dict(types),
            'vehicle_categories': dict(vehicle_types),
            'sources': dict(sources),
            'price_stats': {
                'count': len(priced),
                'min': min(prices) if priced else 0,
                'max': max(prices) if priced else 0,
                'avg': sum(prices)/len(priced) if priced else 0
            } if priced else {},
            'items': all_items
        }
        
        output_file = self.curated_dir / "spare_parts_curated.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved curated spare parts dataset: {output_file}")
        return output


def main():
    processor = SparePartsProcessor()
    processor.process_all()


if __name__ == "__main__":
    main()