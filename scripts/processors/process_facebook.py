#!/usr/bin/env python3
"""
Facebook Groups Data Processor
Processes scraped Facebook group posts for vehicle listings
Integrates with the motos_bicis_project standardized format
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

class FacebookDataProcessor:
    def __init__(self, project_root: str = "/home/reynaldomesab/Project/motos_bicis_project"):
        self.project_root = Path(project_root)
        self.raw_dir = self.project_root / "data" / "raw" / "facebook"
        self.curated_dir = self.project_root / "data" / "curated"
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_id = f"facebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now().isoformat()
        
        # Vehicle classification keywords (same as other processors)
        self.VEHICLE_INDICATORS = {
            'Moto Combustión': [
                'moto ', 'motos ', 'motocicleta', 'motorina', 'motorinas',
                'motoneta', 'motonetas', 'scooter', 'scooters',
                'ciclomotor', 'ciclomotores', 'bicimoto', 'bicimotos',
                'bici moto', 'bici-moto', 'scuter', '𝛋𝐭𝐨', '𝛋𝐭𝐨𝐬',
                'yamaha', 'honda ', 'suzuki ', 'kawasaki', 'ktm ', 'ducati', 'harley',
                'bj ', 'keeway', 'znen', 'loncin', 'lifan', 'cg125', 'cg150', 'cg200',
                'xr150', 'xr250', 'crf', 'yzf', 'r15', 'r3', 'mt07', 'mt09', 'r1', 'r6',
                'cbr', 'cbf', 'cb125', 'cb190', 'cb300', 'cb500', 'cb650', 'cb1000',
                'hornet', 'shadow', 'vstrom', 'gsx', 'gsxr', 'hayabusa', 'bandit',
                'ninja', 'zx6r', 'zx10r', 'z900', 'z650', 'versys', 'vulcan',
                'duke', 'rc390', 'rc125', 'adv ', 'enduro', 'cross', 'motard', 'trail',
                'jin ', 'krathos', 'restrepa', 'mt ', 'halcón', 'halcon', 'vedca',
                'lifan', 'izuki', 'unison', 'topmaq', 'ava pantera', 'mountain',
                'kvitova', 'pla51', 'pla 51', 'mikazuki', 'caiman', 'mvp ',
                'jinpeng', 'qlife', 'onebot', 'shikra', 'avisp', 'predator',
                'challenger', 'voltus', 'eagle', 'pron', 'prontezza', 'corleone',
                'maf ', 'maf eagle', 'eagle', 'motico', 'matico', 'challenger',
                'prontezza', 'corleone', 'maf eagle', 'ava pantera'
            ],
            'Moto Eléctrica': [
                'moto eléctrica', 'moto electrica', 'motos eléctricas', 'motos electricas',
                'motorina eléctrica', 'motorina electrica', 'motorinas eléctricas',
                'bicimoto eléctrica', 'bicimoto electrica', 'bicimotos eléctricas',
                'bicimotos ', 'bicimotos', '𝐦𝐨𝐭𝐨 𝐞𝐥', '𝐦𝐨𝐭𝐨𝐬 𝐞𝐥',
                '𝐦𝐨𝐭𝐨 𝐞𝐥é', '𝐦𝐨𝐭𝐨𝐬 𝐞𝐥é', '𝐦𝐨𝐭𝐨𝐬 𝐞𝐥é𝐜𝐭𝐫𝐢𝐜𝐚',
                '𝐦𝐨𝐭𝐨 𝐞𝐥é𝐜𝐭𝐫𝐢𝐜𝐚', '𝐛𝐢𝐜𝐢𝐦𝐨𝐭𝐨', '𝐛𝐢𝐜𝐢𝐦𝐨𝐭𝐨𝐬',
                'bicimoto eléctrica', 'bicimoto electrica', 'bicimotos eléctricas'
            ],
            'Bicicleta Eléctrica': [
                'bicicleta eléctrica', 'bicicleta electrica', 'bicicletas eléctricas',
                'bici eléctrica', 'bici electrica', 'bicis eléctricas',
                'ebike', 'e-bike', 'e bike', 'bicicleta a bateria', 'bicicleta a pilas',
                'bicicleta con motor', 'bicicleta motorizada'
            ],
            'Bicicleta': [
                'bicicleta ', 'bicicletas ', 'bici ', 'bici de', 'bici para',
                'bicicleta de montaña', 'bicicleta montaña', 'mtb', 'mountain bike',
                'bicicleta de paseo', 'bicicleta paseo', 'bicicleta de ruta', 'bicicleta ruta',
                'bicicleta plegable', 'bici plegable', 'folding bike',
                'bicicleta infantil', 'bicicleta para niños', 'bicicleta para ninos',
                'bicicleta 12', 'bicicleta 14', 'bicicleta 16', 'bicicleta 18',
                'bicicleta 20', 'bicicleta 24', 'bicicleta 26', 'bicicleta 29',
                'aro 26', 'aro 27', 'aro 29', 'aro 24', 'aro 20',
                'huffy', 'vivamax', 'spiderman', 'equilibrio', 'balance bike',
                '𝐛𝐢𝐜𝐢𝐜𝐥𝐞𝐭𝐚', '𝐛𝐢𝐜𝐢𝐜𝐥𝐞𝐭𝐚𝐬', '𝐛𝐢𝐜𝐢',
                'huffy', 'vivamax', 'spiderman', 'equilibrio', 'balance bike'
            ],
            'Patinete Eléctrico': [
                'patinete', 'patinetes', 'patineta', 'scooter eléctrico', 'scooter electrico',
                'scooters eléctricos', 'hoverboard', 'monociclo', 'unicycle',
                '𝐩𝐚𝐭𝐢𝐧𝐞𝐭𝐚', '𝐩𝐚𝐭𝐢𝐧𝐞𝐭𝐚𝐬', '𝐬𝐜𝐨𝐨𝐭𝐞𝐫'
            ],
            'Mototrina': [
                'triciclo eléctrico', 'triciclo electrico', 'triciclos eléctricos',
                'triciclo de carga', 'triciclo carga', 'triciclo híbrido', 'triciclo hibrido',
                'triciclo 202', 'triciclo 2025', 'triciclo 2026',
                'mototrina', 'mototrin', 'mikazuki', 'caiman', 'vedca ',
                'mvp ', 'jinpeng', 'qlife', 'onebot', 'power ',
                'extensor de rango', 'refrigerado', 'mototrina', 'mototrin'
            ]
        }
        
        # Parts/accessories to exclude
        self.PART_INDICATORS = [
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
            'trailer', 'remolque', 'carreta', 'consola', 'caja 5ta', 'forro de',
            'kit de bases', 'vendo neumáticos', 'reproductor', 'cámara', 'android',
            'carplay', 'ojos del diablo', 'interesados', 'me ajusto',
            'arrancador portátil', 'oferta', 'se recogen', 'compresor',
            'enganche', 'bola de trailler', 'neumático', 'neumáticos', 'goma',
            'gomas', 'llanta', 'llantas', 'aceite', 'filtro', 'pistón', 'pistones',
            'cigueñal', 'escape', 'compresión', 'compresion', 'manifor',
            'arrancador', 'convertidor', 'cargador topmaq', 'extensor de rango',
            'bateria topmaq', 'batería topmaq', 'cargador 84v', 'compresor',
            'arrancador de bateria', 'power bank', 'bote 4 lt', 'juego de pistones',
            'tubo de escape', 'cigueñal', 'manifor curvo', 'clochet',
            'tubo de escape', 'compresion', 'manifor curvo', 'clochet',
            'tubo de escape', 'compresion', 'arrancador de bateria',
            'power bank', 'bote 4 lt', 'juego de pistones', 'tubo de escape',
            'cigueñal', 'manifor curvo', 'clochet', 'compresion', 'arrancador'
        ]
        
        # Currency patterns
        self.CURRENCY_PATTERNS = {
            'USD': [r'\$\s*([\d,]+\.?\d*)', r'USD\s*([\d,]+\.?\d*)', r'(\d+)\s*usd', r'(\d+)\s*us\$'],
            'CUP': [r'(\d+)\s*cup', r'(\d+)\s*c\.u\.p\.', r'c\.u\.p\.\s*(\d+)', r'cup\s*(\d+)', r'peso', r'mn\s*(\d+)', r'moneda nacional'],
            'ZELLE': [r'zelle', r'zelle\s*(\d+)'],
            'EUR': [r'eur\s*(\d+)', r'€\s*([\d,]+\.?\d*)', r'(\d+)\s*eur'],
        }

    def load_raw_data(self) -> List[Dict]:
        """Load the raw Facebook JSON data."""
        json_file = self.raw_dir / "facebook.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} raw Facebook posts")
        return data

    def extract_text_content(self, post: Dict) -> str:
        """Extract all text content from a post (main text + shared post + attachments OCR)."""
        texts = []
        
        # Main post text
        if post.get('text'):
            texts.append(str(post['text']))
        
        # Shared post text
        if post.get('sharedPost'):
            shared = post['sharedPost']
            if shared.get('text'):
                texts.append(str(shared['text']))
            # OCR text from attachments in shared post
            if shared.get('attachments'):
                for att in shared['attachments']:
                    if isinstance(att, dict):
                        if att.get('ocrText'):
                            texts.append(str(att['ocrText']))
                        if att.get('description'):
                            texts.append(str(att['description']))
        
        # Attachments OCR text
        if post.get('attachments'):
            for att in post['attachments']:
                if isinstance(att, dict):
                    if att.get('ocrText'):
                        texts.append(str(att['ocrText']))
                    if att.get('description'):
                        texts.append(str(att['description']))
        
        return ' '.join(texts)

    def extract_price_and_currency(self, text: str) -> Dict[str, Any]:
        """Extract price and currency from text."""
        text_lower = text.lower()
        
        # Try each currency pattern
        for currency, patterns in self.CURRENCY_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Get the first reasonable match
                    for match in matches:
                        try:
                            # Handle tuple matches from capture groups
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            price_str = re.sub(r'[^\d.,]', '', str(match))
                            price_str = price_str.replace(',', '')
                            if price_str:
                                price = float(price_str)
                                # Basic sanity check
                                if currency == 'CUP' and price > 100000:
                                    continue  # Likely not a price in CUP
                                if currency == 'USD' and price > 50000:
                                    continue  # Likely not a price in USD
                                if currency == 'CUP' and price < 100:
                                    continue
                                if currency == 'USD' and price < 10:
                                    continue
                                return {'price': price, 'currency': currency}
                        except (ValueError, IndexError):
                            continue
        
        return {'price': None, 'currency': None}

    def extract_location(self, text: str) -> Optional[str]:
        """Extract location from text (Cuban provinces/cities)."""
        locations = [
            'la habana', 'habana', 'centro habana', 'plaza', 'cerro', 'boyeros',
            'arroyo naranjo', 'cotorro', 'san miguel del padrón', 'guanabacoa',
            'habana del este', 'regla', 'guanabacoa', 'maranao', 'marianao',
            'santiago de cuba', 'santiago', 'holguín', 'holguin', 'camagüey',
            'camaguey', 'villa clara', 'santa clara', 'matanzas', 'cienfuegos',
            'ciego de ávila', 'ciego de avila', 'sancti spíritus', 'sancti spiritus',
            'las tunas', 'granma', 'bayamo', 'guantánamo', 'guantanamo',
            'pinar del río', 'pinar del rio', 'artemisa', 'mayabeque',
            'isla de la juventud', 'isla de la juventud', 'colón', 'colon',
            'cárdenas', 'cardenas', 'pinar', 'artemisa', 'guines', 'güines',
            'bauta', 'guanajay', 'bauta', 'san antonio', 'mariel', 'caimito',
            'san cristobal', 'candelaria', 'bahía honda', 'bahia honda',
            'guane', 'mantua', 'sandino', 'viñales', 'vinales', 'la palma',
            'los palacios', 'consolación del sur', 'consolacion del sur'
        ]
        
        text_lower = text.lower()
        for loc in locations:
            if loc in text_lower:
                # Normalize
                if loc in ['la habana', 'habana', 'centro habana', 'plaza', 'cerro', 'boyeros',
                           'arroyo naranjo', 'cotorro', 'san miguel del padrón', 'guanabacoa',
                           'habana del este', 'regla', 'marianao']:
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
        """Extract WhatsApp contact from post."""
        # Check textReferences
        if post.get('textReferences'):
            for ref in post['textReferences']:
                if ref.get('external_url', '').startswith('http://Wa.me/') or ref.get('external_url', '').startswith('https://Wa.me/'):
                    return ref['external_url']
                if ref.get('external_url', '').startswith('http://wa.me/') or ref.get('external_url', '').startswith('https://wa.me/'):
                    return ref['external_url']
        
        # Check link field
        link = post.get('link', '')
        if 'wa.me' in link.lower() or 'Wa.me' in link:
            return link
        
        # Search in text
        text = self.extract_text_content({})  # Will be filled by caller
        wa_match = re.search(r'(https?://)?(wa\.me|Wa\.me)/\d+', text)
        if wa_match:
            return wa_match.group(0)
        
        return None

    def is_pure_part(self, text: str) -> bool:
        """Check if text indicates a pure part/accessory sale."""
        text_lower = text.lower()
        for kw in self.PART_INDICATORS:
            if kw in text_lower:
                # Check if it's a vehicle with parts mentioned
                vehicle_first = any(text_lower.startswith(v.split()[0]) for v in [
                    'moto', 'motos', 'motorina', 'motorinas', 'motoneta', 'motonetas',
                    'scooter', 'bicimoto', 'bicimotos', 'bicimoto', 'bicimotos',
                    'bicicleta', 'bicicletas', 'bici', 'bicicletas', 'bici',
                    'patinete', 'patinetes', 'triciclo', 'triciclos', 'mototrina'
                ])
                if not vehicle_first:
                    return True
        return False

    def classify_vehicle(self, text: str) -> str:
        """Classify vehicle type from text."""
        text_lower = text.lower()
        
        # Check for parts first
        if self.is_pure_part(text_lower):
            return 'Parte/Accesorio'
        
        # Check each vehicle type
        for vtype, keywords in self.VEHICLE_INDICATORS.items():
            for kw in keywords:
                if kw in text_lower:
                    return vtype
        
        return 'Otro'

    def extract_brand(self, text: str) -> Optional[str]:
        """Extract brand from text."""
        brands = {
            'TOPMAQ': ['topmaq', 'topmaq'],
            'VEDCA': ['vedca', 'vedca'],
            'MOTICO': ['motico', 'matico', 'motico'],
            'Kvitova': ['kvitova', 'kvitova'],
            'Jin': ['jin ', 'jin'],
            'Krathos': ['krathos', 'krathos'],
            'Restrepa': ['restrepa', 'restrepa'],
            'Lifan': ['lifan', 'lifan'],
            'Halcón': ['halcón', 'halcon'],
            'Unison': ['unison', 'unison'],
            'Izuki': ['izuki', 'izuki'],
            'MAF': ['maf ', 'maf eagle', 'maf eagle'],
            'AVA': ['ava ', 'ava pantera'],
            'Huffy': ['huffy', 'huffy'],
            'Vivamax': ['vivamax', 'vivamax'],
            'Spiderman': ['spiderman', 'spider man'],
            'Yamaha': ['yamaha', 'yamaha'],
            'Honda': ['honda ', 'honda'],
            'Suzuki': ['suzuki ', 'suzuki'],
            'Kawasaki': ['kawasaki', 'kawasaki'],
            'KTM': ['ktm ', 'ktm'],
            'Ducati': ['ducati', 'ducati'],
            'Harley': ['harley', 'harley'],
            'Bajaj': ['bajaj', 'bajaj'],
            'Keeway': ['keeway', 'keeway'],
            'Znen': ['znen', 'znen'],
            'Loncin': ['loncin', 'loncin'],
            'Bajaj': ['bajaj', 'bajaj'],
            'Mikazuki': ['mikazuki', 'mikazuki'],
            'Caiman': ['caiman', 'caiman'],
            'MVP': ['mvp ', 'mvp'],
            'Jinpeng': ['jinpeng', 'jinpeng'],
            'QLife': ['qlife', 'qlife'],
            'OneBot': ['onebot', 'onebot'],
            'Shikra': ['shikra', 'shikra'],
            'Avisp': ['avisp', 'avispon'],
            'Predator': ['predator', 'predator'],
            'Challenger': ['challenger', 'challenger'],
            'Voltus': ['voltus', 'voltus'],
            'Eagle': ['eagle', 'eagle'],
            'Maf Eagle': ['maf eagle', 'maf eagle'],
            'Corleone': ['corleone', 'corleone'],
            'Prontezza': ['prontezza', 'prontezza'],
            'Corleone': ['corleone', 'corleone'],
        }
        
        text_lower = text.lower()
        for brand, keywords in brands.items():
            for kw in keywords:
                if kw in text_lower:
                    return brand
        return None

    def process_post(self, post: Dict) -> Optional[Dict]:
        """Process a single Facebook post into standardized format."""
        # Get all text content
        text = self.extract_text_content(post)
        
        if not text or len(text.strip()) < 5:
            return None
        
        # Check if it's a part/accessory
        if self.is_pure_part(text):
            return None
        
        # Classify vehicle
        vehicle_type = self.classify_vehicle(text)
        if vehicle_type in ['Parte/Accesorio', 'Otro']:
            return None
        
        # Extract price
        price_info = self.extract_price_and_currency(text)
        
        # Extract location
        location = self.extract_location(text)
        
        # Extract brand
        brand = self.extract_brand(text)
        
        # Extract WhatsApp
        whatsapp = self.extract_whatsapp(post)
        
        # Get author info
        user = post.get('user', {})
        
        # Get images - handle various attachment structures
        def extract_image_uris(attachments):
            uris = []
            for att in attachments:
                # Handle dict attachments
                if isinstance(att, dict):
                    # Try media.image.uri
                    if att.get('media', {}).get('image', {}).get('uri'):
                        uris.append(att['media']['image']['uri'])
                    # Try thumbnail.uri
                    elif isinstance(att.get('thumbnail'), dict) and att['thumbnail'].get('uri'):
                        uris.append(att['thumbnail']['uri'])
                    # Try direct uri
                    elif att.get('uri'):
                        uris.append(att['uri'])
                    # Try image.uri
                    elif isinstance(att.get('image'), dict) and att['image'].get('uri'):
                        uris.append(att['image']['uri'])
                    # Try src
                    elif att.get('src'):
                        uris.append(att['src'])
                # Handle string attachments (could be URI)
                elif isinstance(att, str) and (att.startswith('http') or att.startswith('https')):
                    uris.append(att)
            return uris
        
        images = []
        if post.get('attachments'):
            images.extend(extract_image_uris(post['attachments']))
        
        # Shared post images
        if post.get('sharedPost', {}).get('attachments'):
            images.extend(extract_image_uris(post['sharedPost']['attachments']))
        
        # Convert price to USD
        price_usd = None
        if price_info['price'] is not None:
            if price_info['currency'] == 'USD':
                price_usd = price_info['price']
            elif price_info['currency'] == 'CUP':
                price_usd = round(price_info['price'] / 2400, 2)
            elif price_info['currency'] == 'ZELLE':
                price_usd = price_info['price']
            elif price_info['currency'] == 'EUR':
                price_usd = round(price_info['price'] * 1.08, 2)
        
        # Build standardized record
        record = {
            'source': 'facebook',
            'source_id': f"facebook_{self.session_start[:10].replace('-', '')}",
            'source_url': post.get('url', ''),
            'facebook_url': post.get('facebookUrl', ''),
            'post_id': post.get('id', ''),
            'legacy_id': post.get('legacyId', ''),
            'feedback_id': post.get('feedbackId', ''),
            'scraped_at': post.get('time', self.session_start),
            'processed_at': datetime.now().isoformat(),
            'group_title': post.get('groupTitle', ''),
            'author': {
                'id': user.get('id', ''),
                'name': user.get('name', ''),
                'profile_pic': user.get('profilePic', '')
            },
            'text': text[:5000],  # Limit text length
            'title': post.get('title', ''),
            'price_original': price_info['price'],
            'currency_original': price_info['currency'],
            'price_usd': price_usd,
            'location': location,
            'brand': brand,
            'vehicle_type': self.classify_vehicle(text),
            'whatsapp': whatsapp,
            'images': images[:10],  # Limit images
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
        """Main processing pipeline."""
        print(f"Starting Facebook data processing: {self.source_id}")
        
        # Load raw data
        raw_posts = self.load_raw_data()
        
        # Process each post
        processed = []
        stats = {
            'total_raw': len(raw_posts),
            'processed': 0,
            'skipped_no_text': 0,
            'skipped_parts': 0,
            'skipped_other': 0,
            'by_vehicle_type': Counter(),
            'by_group': Counter(),
            'with_price': 0,
            'with_whatsapp': 0,
            'with_images': 0
        }
        
        for post in raw_posts:
            record = self.process_post(post)
            
            if record is None:
                text = self.extract_text_content(post)
                if not text or len(text.strip()) < 5:
                    stats['skipped_no_text'] += 1
                elif self.is_pure_part(self.extract_text_content(post)):
                    stats['skipped_parts'] += 1
                else:
                    stats['skipped_other'] += 1
                continue
            
            processed.append(record)
            stats['processed'] += 1
            stats['by_vehicle_type'][record['vehicle_type']] += 1
            stats['by_group'][record['group_title']] += 1
            
            if record['price_usd'] is not None:
                stats['with_price'] += 1
            if record['whatsapp']:
                stats['with_whatsapp'] += 1
            if record['images_count'] > 0:
                stats['with_images'] += 1
        
        print(f"Processing complete:")
        print(f"  Total raw: {stats['total_raw']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Skipped (no text): {stats['skipped_no_text']}")
        print(f"  Skipped (parts): {stats['skipped_parts']}")
        print(f"  Skipped (other): {stats['skipped_other']}")
        print(f"  By vehicle type: {dict(stats['by_vehicle_type'])}")
        print(f"  By group: {dict(stats['by_group'])}")
        print(f"  With price: {stats['with_price']}")
        print(f"  With WhatsApp: {stats['with_whatsapp']}")
        print(f"  With images: {stats['with_images']}")
        
        # Save processed data
        output_file = self.curated_dir / f"facebook_curated_{self.session_start[:10].replace('-', '')}.json"
        
        output = {
            'source_id': self.source_id,
            'source_name': 'Facebook Groups',
            'source_type': 'social_media',
            'scraped_at': self.session_start,
            'processed_at': datetime.now().isoformat(),
            'stats': {k: dict(v) if isinstance(v, Counter) else v for k, v in stats.items()},
            'items': processed
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved curated data to: {output_file}")
        print(f"Total vehicles: {len(processed)}")
        
        return output


if __name__ == "__main__":
    processor = FacebookDataProcessor()
    processor.run()