#!/usr/bin/env python3
"""
Utilidades de moneda - Normalización y conversión de precios
"""

import re
from typing import Optional, Dict

# Tasas de conversión a USD (actualizar periódicamente)
EXCHANGE_RATES = {
    'USD': 1.0,
    'US$': 1.0,
    '$': 1.0,
    'CUP': 1/2400.0,      # Peso cubano ~ 2400 CUP = 1 USD
    'CUP$': 1/2400.0,
    'MN': 1/2400.0,       # Moneda Nacional
    'ZELLE': 1.0,         # Zelle es USD
    'EUR': 1.08,          # Euro aprox
    '€': 1.08,
    'MLC': 1.0,           # Moneda Libremente Convertible = USD
}

# Patrones de detección de moneda en texto
CURRENCY_PATTERNS = {
    'USD': [
        r'\$\s*([\d,]+\.?\d*)',
        r'USD\s*([\d,]+\.?\d*)',
        r'US\$\s*([\d,]+\.?\d*)',
        r'(\d+)\s*usd',
        r'(\d+)\s*us\$',
    ],
    'CUP': [
        r'(\d+)\s*cup',
        r'(\d+)\s*c\.u\.p\.',
        r'c\.u\.p\.\s*(\d+)',
        r'cup\s*(\d+)',
        r'peso',
        r'mn\s*(\d+)',
        r'moneda\s+nacional',
    ],
    'ZELLE': [
        r'zelle',
        r'zelle\s*(\d+)',
    ],
    'EUR': [
        r'eur\s*([\d,]+\.?\d*)',
        r'€\s*([\d,]+\.?\d*)',
        r'(\d+)\s*eur',
    ],
    'MLC': [
        r'mlc\s*([\d,]+\.?\d*)',
        r'moneda\s+libremente\s+convertible',
    ],
}

# Alias de moneda para normalización
CURRENCY_ALIASES = {
    'usd': 'USD',
    'us$': 'USD',
    '$': 'USD',
    'usd': 'USD',
    'cup': 'CUP',
    'c.u.p.': 'CUP',
    'c.u.p': 'CUP',
    'mn': 'CUP',
    'moneda nacional': 'CUP',
    'peso': 'CUP',
    'zelle': 'ZELLE',
    'eur': 'EUR',
    '€': 'EUR',
    'mlc': 'MLC',
    'moneda libremente convertible': 'MLC',
}


def normalize_currency(currency_str: str) -> str:
    """
    Normaliza el string de moneda a formato estándar.
    
    Args:
        currency_str: String de moneda (ej: 'USD', 'cup', 'Zelle')
        
    Returns:
        Moneda normalizada en mayúsculas (ej: 'USD', 'CUP', 'ZELLE')
    """
    if not currency_str:
        return 'USD'
    
    normalized = currency_str.strip().lower()
    return CURRENCY_ALIASES.get(normalized, currency_str.upper())


def convert_to_usd(price: float, currency: str) -> Optional[float]:
    """
    Convierte un precio a USD usando la tasa de cambio.
    
    Args:
        price: Precio original
        currency: Moneda original
        
    Returns:
        Precio en USD redondeado a 2 decimales
    """
    if price is None:
        return None
    
    normalized = normalize_currency(currency)
    rate = EXCHANGE_RATES.get(normalized, 1.0)
    return round(price * rate, 2)


def extract_price_and_currency(text: str) -> Dict:
    """
    Extrae precio y moneda de un texto.
    
    Args:
        text: Texto donde buscar precio
        
    Returns:
        Dict con 'price' (float) y 'currency' (str) o None si no encuentra
    """
    text_lower = text.lower()
    
    for currency, patterns in CURRENCY_PATTERNS.items():
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
                            # Validaciones de sanidad
                            if currency == 'CUP' and price > 100000:
                                continue
                            if currency == 'USD' and price > 50000:
                                continue
                            if currency == 'CUP' and price < 100:
                                continue
                            if currency == 'USD' and price < 10:
                                continue
                            return {'price': price, 'currency': currency}
                    except (ValueError, IndexError):
                        continue
    
    return {'price': None, 'currency': None}


def convert_to_usd(price: float, currency: str) -> Optional[float]:
    """
    Convierte un precio a USD.
    
    Args:
        price: Precio original
        currency: Moneda original
        
    Returns:
        Precio en USD o None si no se puede convertir
    """
    if price is None:
        return None
    
    normalized = normalize_currency(currency)
    rate = EXCHANGE_RATES.get(normalized, 1.0)
    return round(price * rate, 2)


def format_price_usd(price_usd: float) -> str:
    """
    Formatea un precio en USD para mostrar.
    """
    if price_usd is None:
        return "N/A"
    if price_usd >= 1000:
        return f"${price_usd:,.2f}"
    return f"${price_usd:.2f}"


def parse_price_string(price_str: str) -> Optional[float]:
    """
    Parsea un string de precio a float.
    
    Args:
        price_str: String como "1,500.00" o "1500" o "1,500"
        
    Returns:
        Float o None si no se puede parsear
    """
    if not price_str:
        return None
    
    # Limpiar string
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None