#!/usr/bin/env python3
"""
Facebook Groups Repuestos Scraper
Processes Facebook group posts for spare parts listings
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict


class FacebookRepuestosProcessor:
    def __init__(self, project_root: str = "/home/reynaldomesab/Project/motos_bicis_project"):
        self.project_root = Path(project_root)
        self.raw_dir = self.project_root / "data" / "raw" / "facebook"
        self.curated_dir = self.project_root / "data" / "curated"
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_id = f"facebook_repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now().isoformat()
        
        # Spare parts category indicators
        self.PART_INDICATORS = {
            'Repuesto Moto': [
                'moto ', 'motorina', 'motoneta', 'scooter', 'cilindro', 'pistón', 'carburador', 'bujía',
                'freno moto', 'cadena moto', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto',
                'bujía moto', 'bobina moto', 'carburador moto', 'cigueñal', 'biela', 'embrague',
                'variador', 'piñon moto', 'corona moto', 'filtro moto', 'aceite moto', 'bujía moto',
            ],
            'Repuesto Bicicleta': [
                'bicicleta ', 'bici ', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici', 'cambio bici',
                'desviador', 'freno bici', 'manillar bici', 'sillin bici', 'pedal bici', 'biela bici',
                'cuadro bici', 'horquilla bici', 'amortiguador bici', 'suspensión bici',
            ],
            'Repuesto Moto Eléctrica': [
                'batería moto', 'bateria moto', 'cargador moto', 'controlador moto', 'controlador ',
                'ecu moto', 'cdi moto', 'bobina moto', 'estator moto', 'rotor moto',
                'motor eléctrico moto', 'motor electrico moto', 'batería litio moto', 'bateria litio moto',
                'lifepo4 moto', 'cargador moto', 'cargador de moto', 'controlador moto electrica',
            ],
            'Repuesto Bicicleta Eléctrica': [
                'batería bici', 'bateria bici', 'cargador bici', 'controlador bici',
                'motor eléctrico bici', 'motor electrico bici', 'batería litio bici', 'bateria litio bici',
                'lifepo4 bici', 'cargador bici', 'cargador de bici', 'controlador bici electrica',
                'motor central bici', 'motor buje bici', 'batería litio bici', 'bateria litio bici',
                'lifepo4 bici', 'cargador bici', 'cargador de bici', 'controlador bici electrica',
            ],
            'Repuesto Patinete': [
                'patinete', 'patineta', 'scooter eléctrico', 'scooter electrico',
                'hoverboard', 'monociclo', 'unicycle',
            ],
        }

        # Exclude complete vehicles
        self.EXCLUDE_KEYWORDS = [
            'triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
            'bicicleta ', 'bicicletas ', 'bici ', ' ebike', 'e-bike', 'e bike',
            'bicicleta eléctrica', 'bicicleta electrica', 'bici eléctrica',
            'patinete', 'patinetes', 'scooter eléctrico', 'hoverboard', 'monociclo',
            'carro', 'auto', 'automovil', 'automóvil',
            'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
            'motoneta', 'motonetas', 'scooter', 'scooters',
            'bicimoto', 'bicimotos', 'bici moto', 'bici-moto',
            'triciclo', 'mototrina', 'mototrin', 'cuatriciclo', 'cuatrimoto', 'atv', 'quad',
        ]

        # Currency patterns
        self.CURRENCY_PATTERNS = {
            'USD': [r'\$\s*([\d,]+\.?\d*)', r'USD\s*([\d,]+\.?\d*)', r'(\d+)\s*usd', r'(\d+)\s*us\$'],
            'CUP': [r'(\d+)\s*cup', r'(\d+)\s*c\.u\.p\.', r'cup\s*(\d+)', r'peso', r'mn\s*(\d+)', r'moneda nacional'],
            'ZELLE': [r'zelle', r'zelle\s*(\d+)'],
            'EUR': [r'eur\s*([\d,]+\.?\d*)', r'€\s*([\d,]+\.?\d*)', r'(\d+)\s*eur'],
        }

    def __init__(self, project_root: str = "/home/reynaldomesab/Project/motos_bicis_project"):
        self.project_root = Path(project_root)
        self.raw_dir = Path(project_root) / "data" / "raw" / "facebook"
        self.curated_dir = Path(project_root) / "data" / "curated"
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_id = f"facebook_repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now().isoformat()

    def load_raw_data(self) -> List[Dict]:
        json_file = self.raw_dir / "facebook.json"
        if not json_file.exists():
            print(f"Facebook raw data not found at {json_file}")
            return []
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} raw Facebook posts")
        return data

    def extract_text_content(self, post: Dict) -> str:
        texts = []
        if post.get('text'):
            texts.append(str(post['text']))
        if post.get('sharedPost'):
            shared = post['sharedPost']
            if shared.get('text'):
                texts.append(str(shared['text']))
            if shared.get('attachments'):
                for att in shared['attachments']:
                    if isinstance(att, dict):
                        if att.get('ocrText'):
                            texts.append(str(att['ocrText']))
                        if att.get('description'):
                            texts.append(str(att['description']))
        if post.get('attachments'):
            for att in post['attachments']:
                if isinstance(att, dict):
                    if att.get('ocrText'):
                        texts.append(str(att['ocrText']))
                    if att.get('description'):
                        texts.append(str(att['description']))
        return ' '.join(texts)

    def extract_price_and_currency(self, text: str) -> Dict:
        text_lower = text.lower()
        for currency, patterns in self.CURRENCY_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    for match in matches:
                        try:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            price_str = re.sub(r'[^\d.,]', '', str(match))
                            price_str = price_str.replace(',', '')
                            if price_str:
                                price = float(price_str)
                                if currency == 'CUP' and price > 100000: continue
                                if currency == 'USD' and price > 50000: continue
                                if currency == 'CUP' and price < 100: continue
                                if currency == 'USD' and price < 10: continue
                                return {'price': price, 'currency': currency}
                        except (ValueError, IndexError):
                            continue
        return {'price': None, 'currency': None}

    def extract_location(self, text: str) -> Optional[str]:
        locations = ['la habana', 'centro habana', 'plaza', 'cerro', 'boyeros', 'arroyo naranjo',
                     'cotorro', 'san miguel del padrón', 'guanabacoa', 'habana del este',
                     'regla', 'marianao', 'santiago de cuba', 'santiago', 'holguín', 'holguin',
                     'camagüey', 'camaguey', 'villa clara', 'santa clara', 'matanzas', 'cienfuegos',
                     'ciego de ávila', 'ciego de avila', 'sancti spíritus', 'sancti spiritus',
                     'las tunas', 'granma', 'bayamo', 'guantánamo', 'guantanamo',
                     'pinar del río', 'pinar del rio', 'artemisa', 'mayabeque', 'isla de la juventud']
        text_lower = text.lower()
        for loc in locations:
            if loc in text_lower:
                if loc in ['la habana', 'habana', 'centro habana', 'plaza', 'cerro', 'boyeros']:
                    return 'La Habana'
                elif loc in ['santiago de cuba', 'santiago']:
                    return 'Santiago de Cuba'
                elif loc in ['holguín', 'holguin']:
                    return 'Holguín'
                elif loc in ['camagüey', 'camaguey']:
                    return 'Camagüey'
                elif loc in ['villa clara', 'santa clara']:
                    return 'Villa Clara'
                elif loc in ['matanzas']:
                    return 'Matanzas'
                elif loc in ['cienfuegos']:
                    return 'Cienfuegos'
                elif loc in ['ciego de ávila', 'ciego de avila']:
                    return 'Ciego de Ávila'
                elif loc in ['sancti spíritus', 'sancti spiritus']:
                    return 'Sancti Spíritus'
                elif loc in ['las tunas']:
                    return 'Las Tunas'
                elif loc in ['granma', 'bayamo']:
                    return 'Granma'
                elif loc in ['guantánamo', 'guantanamo']:
                    return 'Guantánamo'
                elif loc in ['pinar del río', 'pinar del rio', 'pinar']:
                    return 'Pinar del Río'
                elif loc in ['artemisa']:
                    return 'Artemisa'
                elif loc in ['mayabeque']:
                    return 'Mayabeque'
                elif loc in ['isla de la juventud']:
                    return 'Isla de la Juventud'
                else:
                    return loc.title()
        return None

    def extract_whatsapp(self, post: Dict) -> Optional[str]:
        if post.get('textReferences'):
            for ref in post['textReferences']:
                url = ref.get('external_url', '')
                if 'wa.me' in url.lower() or 'Wa.me' in url:
                    return url
        link = post.get('link', '')
        if 'wa.me' in link.lower():
            return link
        return None

    def is_pure_part(self, text: str) -> bool:
        text_lower = text.lower()
        # Must contain part keywords
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
                         'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
                         'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
                         'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
                         'cargador para', 'cargador de', 'cargador ',
                         'batería ', 'bateria ', 'batería de', 'bateria de',
                         'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
                         'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
                         'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
                         'cargador para', 'cargador de', 'cargador ',
                         'batería ', 'bateria ', 'batería de', 'bateria de',
                         'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
                         'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
                         'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
                         'cargador para', 'cargador de', 'cargador ',
                         'batería ', 'bateria ', 'batería de', 'bateria de',
                         'extensor de rango', 'aro ', 'llanta bici', 'cadena bici', 'piñon bici',
                         'cambio', 'desviador', 'freno bici', 'manillar', 'sillin', 'pedal',
                         'biela', 'cuadro', 'horquilla', 'amortiguador', 'suspensión',
                         'cargador para', 'cargador de', 'cargador ',
                         'batería ', 'bateria ', 'batería de', 'bateria de',
                         'extensor de rango']
        text_lower = text.lower()
        for kw in ['repuesto', 'pieza', 'accesorio', 'cargador', 'bateria', 'batería',
                     'motor', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno',
                     'cadena', 'piñon', 'corona', 'llanta', 'neumático', 'filtro',
                     'aceite', 'bujía', 'bobina', 'carburador', 'cargador',
                     'batería', 'bateria', 'controlador', 'motor eléctrico',
                     'extensor de rango']:
            if kw in text_lower:
                return True
        return False

    def classify_part(self, text: str) -> str:
        text_lower = text.lower()
        
        # Check for specific vehicle type in title
        if any(kw in text_lower for kw in ['bicicleta eléctrica', 'bici eléctrica', 'ebike', 'e-bike', 'e bike']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in text_lower for kw in ['moto eléctrica', 'motorina eléctrica', 'bicimoto eléctrica', 'scooter eléctrico']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in text_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard', 'monociclo']):
            return 'Repuesto Patinete'
        elif any(kw in text_lower for kw in ['bicicleta ', 'bicicletas ', 'bici ', 'mtb', 'mountain bike', 'huffy', 'vivamax', 'spiderman', 'equilibrio', 'aro 26', 'aro 29', 'aro 27', 'aro 24', 'aro 20']):
            return 'Repuesto Bicicleta'
        elif any(kw in text_lower for kw in ['moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas', 'motoneta', 'motonetas', 'scooter', 'scooters', 'ciclomotor', 'bicimoto', 'bicimotos', 'bici moto', 'bici-moto']):
            return 'Repuesto Moto'
        
        # Check for specific part keywords
        if any(kw in text_lower for kw in ['motor ', 'cilindro', 'pistón', 'carburador', 'bujía', 'freno moto', 'cadena moto', 'piñon moto', 'corona moto']):
            return 'Repuesto Moto'
        elif any(kw in text_lower for kw in ['aro ', 'llanta bici', 'cadena bici', 'piñon bici', 'cambio bici', 'desviador', 'freno bici', 'manillar bici', 'sillin bici', 'pedal bici']):
            return 'Repuesto Bicicleta'
        elif any(kw in text_lower for kw in ['batería moto', 'bateria moto', 'cargador moto', 'controlador moto', 'motor eléctrico moto', 'bateria moto']):
            return 'Repuesto Moto Eléctrica'
        elif any(kw in text_lower for kw in ['batería bici', 'bateria bici', 'cargador bici', 'controlador bici', 'motor eléctrico bici']):
            return 'Repuesto Bicicleta Eléctrica'
        elif any(kw in text_lower for kw in ['patinete', 'patineta', 'scooter eléctrico', 'hoverboard', 'monociclo']):
            return 'Repuesto Patinete'
        
        return 'Repuesto Generico'

    def process_post(self, post: Dict) -> Optional[Dict]:
        text = self.extract_text_content(post)
        if not text or len(text.strip()) < 5:
            return None
        
        # Check if it's a part
        if not self.is_pure_part(text):
            return None
        
        vehicle_type = self.classify_part(text)
        if vehicle_type == 'Otro':
            return None
        
        # Extract price
        price_info = self.extract_price_and_currency(text)
        
        # Extract location
        location = self.extract_location(text)
        
        # Extract WhatsApp
        whatsapp = self.extract_whatsapp(post)
        
        # Get images
        images = []
        if post.get('attachments'):
            for att in post['attachments']:
                if isinstance(att, dict):
                    if att.get('media', {}).get('image', {}).get('uri'):
                        images.append(att['media']['image']['uri'])
                    elif isinstance(att.get('thumbnail'), dict) and att['thumbnail'].get('uri'):
                        images.append(att['thumbnail']['uri'])
        
        # Shared post images
        if post.get('sharedPost', {}).get('attachments'):
            for att in post['sharedPost']['attachments']:
                if isinstance(att, dict):
                    if att.get('media', {}).get('image', {}).get('uri'):
                        images.append(att['media']['image']['uri'])
                    elif isinstance(att.get('thumbnail'), dict) and att['thumbnail'].get('uri'):
                        images.append(att['thumbnail']['uri'])
        
        # Price conversion
        price_usd = None
        if price_info['price'] is not None:
            if price_info['currency'] == 'USD':
                price_usd = price_info['price']
            elif price_info['currency'] == 'CUP':
                price_usd = round(price_info['price'] / 2400, 2)
            elif price_info['currency'] == 'ZELLE':
                price_usd = price_info['price']
        
        # Build record
        user = post.get('user', {})
        record = {
            'source': 'facebook',
            'source_id': 'facebook_repuestos',
            'source_url': post.get('url', ''),
            'facebook_url': post.get('facebookUrl', ''),
            'post_id': post.get('id', ''),
            'legacy_id': post.get('legacyId', ''),
            'feedback_id': post.get('feedbackId', ''),
            'scraped_at': post.get('time', datetime.now().isoformat()),
            'processed_at': datetime.now().isoformat(),
            'group_title': post.get('groupTitle', ''),
            'author': {
                'id': post.get('user', {}).get('id', ''),
                'name': post.get('user', {}).get('name', ''),
                'profile_pic': post.get('user', {}).get('profilePic', '')
            },
            'text': text[:5000],
            'title': post.get('title', ''),
            'price_original': price_info['price'],
            'currency_original': price_info['currency'],
            'price_usd': price_usd,
            'location': location,
            'brand': None,
            'vehicle_type': self.classify_part(text),
            'whatsapp': whatsapp,
            'images': images[:10],
            'images_count': len(images),
            'engagement': {
                'likes': post.get('likesCount', 0),
                'shares': post.get('sharesCount', 0),
                'comments': post.get('commentsCount', 0)
            },
            'is_shared_post': bool(post.get('sharedPost')),
            'shared_post_text': post.get('sharedPost', {}).get('text', '')[:1000] if post.get('sharedPost') else ''
        }
        return record

    def run(self) -> Dict:
        print(f"Starting Facebook Repuestos processing...")
        raw_posts = self.load_raw_data()
        
        processed = []
        stats = {'total_raw': len(raw_posts), 'processed': 0, 'skipped': 0}
        
        for post in raw_posts:
            record = self.process_post(post)
            if record:
                processed.append(record)
                stats['processed'] += 1
            else:
                stats['skipped'] += 1
        
        print(f"Processing complete: {stats['processed']} repuestos processed, {stats['skipped']} skipped")
        
        output_file = self.curated_dir / f"facebook_repuestos_curated_{datetime.now().strftime('%Y%m%d')}.json"
        output = {
            'source_id': 'facebook_repuestos',
            'source_name': 'Facebook Groups',
            'source_type': 'social_media',
            'scraped_at': datetime.now().isoformat(),
            'processed_at': datetime.now().isoformat(),
            'stats': stats,
            'items': processed
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(processed)} repuestos to {output_file}")
        return output


if __name__ == "__main__":
    processor = FacebookRepuestosProcessor()
    processor.run()