"""
Model extraction utilities for DeLonghi products
Extracts standardized model codes from product names
"""

import re
from typing import Optional, List, Tuple


class ModelExtractor:
    """Extract and normalize DeLonghi model codes from product names"""
    
    # Common patterns for DeLonghi models
    PATTERNS = [
        # ECAM series: ECAM22.114.B, ECAM350.55.B, ECAM450.65.S
        r'ECAM\s*\d+\.?\d*\.?\d*\.?\w*',
        # EC series: EC685.R, EC9865M, EC 9865 M
        r'EC\s*\d+\.?\w*',
        # ESAM series: ESAM4500
        r'ESAM\s*\d+',
        # ECI series: ECI341.BK
        r'ECI\s*\d+\.?\w+',
        # EXAM series: EXAM440.55.B
        r'EXAM\s*\d+\.?\d*\.?\w*',
        # KG series (grinders): KG520.M, KG200
        r'KG\s*\d+\.?\w*',
        # KB series (kettles): KBD2001, KBI2001.R
        r'KB\w+\d+\.?\w*',
        # CT series (toasters): CTOV2103.AZ, CTI2103.R
        r'CT\w+\d+\.?\w*',
        # ICM series (coffee makers): ICM17210
        r'ICM\s*\d+',
        # DLSC series (accessories): DLSC002, DLSC310
        r'DLSC\s*\d+',
        # Melitta patterns
        r'Aroma\s*Zones\s*\d+X\d+/\d+\s*\w+',
        r'Aromaboy\s*\d+',
        r'Aromafresh\s*\w+',
        r'F\d+-\d+\w+',
        r'E\d+',
        r'F\d+',
    ]
    
    # Words to remove from product names
    NOISE_WORDS = [
        'delonghi', 'de longhi', 'dl', 'coffee', 'machine', 'maker',
        'espresso', 'cappuccino', 'automatic', 'manual', 'pump',
        'kettle', 'toaster', 'grinder', 'coffeegrinder', 'black',
        'white', 'silver', 'red', 'blue', 'gray', 'grey', 'metal',
        'titanium', 'dedica', 'duo', 'magnifica', 'eletta', 'explore',
        'primadonna', 'sta', 'l', 'ml', 'g', 'kg', 'шт', 'шт.',
        'filter', 'water', 'multiclean', 'set', 'softball', 'cleaning',
        'tabs', 'bruch', 'clean', 'tablets', 'liquid', 'descaling',
        'thermos', 'knock', 'box', 'pitcher', 'milk', 'temper',
        'ceramic', 'glass', 'capp', 'cappuccino', 'bicc', 'latte',
        'cold', 'brew', 'glasses', 'drink', 'small', 'great',
        'cups', 'amerikano', 'means', 'for', 'of', 'the', 'and',
    ]
    
    @classmethod
    def extract_model(cls, product_name: str) -> Optional[str]:
        """
        Extract model code from product name
        
        Args:
            product_name: Full product name
            
        Returns:
            Extracted and normalized model code, or None if not found
            
        Examples:
            >>> ModelExtractor.extract_model("DeLonghi ECAM22.114.B")
            'ECAM22.114.B'
            >>> ModelExtractor.extract_model("Delonghi EC 9865 M")
            'EC9865.M'
            >>> ModelExtractor.extract_model("Coffee Machine DeLonghi EC890.GR Dedica Duo")
            'EC890.GR'
        """
        if not product_name:
            return None
        
        # Convert to uppercase for pattern matching
        text = product_name.upper()
        
        # Try each pattern
        for pattern in cls.PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                model = match.group(0)
                return cls._normalize_model(model)
        
        return None
    
    @classmethod
    def _normalize_model(cls, model: str) -> str:
        """
        Normalize model code to standard format
        
        Args:
            model: Raw model code
            
        Returns:
            Normalized model code
        """
        # Remove extra spaces
        model = re.sub(r'\s+', '', model)
        
        # Convert to uppercase
        model = model.upper()
        
        # Special cases
        # EC 9865 M → EC9865.M
        model = re.sub(r'(EC)(\d+)([A-Z])$', r'\1\2.\3', model)
        
        # Remove "DL" prefix ONLY if NOT DLSC (accessories)
        if not model.startswith('DLSC'):
            model = re.sub(r'^DL\s*', '', model)
        
        return model
    
    @classmethod
    def extract_with_confidence(cls, product_name: str) -> Tuple[Optional[str], float]:
        """
        Extract model with confidence score
        
        Args:
            product_name: Full product name
            
        Returns:
            Tuple of (model, confidence) where confidence is 0.0-1.0
        """
        model = cls.extract_model(product_name)
        if not model:
            return None, 0.0
        
        # Calculate confidence based on various factors
        confidence = 0.5  # Base confidence
        
        # Higher confidence if model appears early in name
        text_upper = product_name.upper()
        model_pos = text_upper.find(model.replace('.', '').replace(' ', ''))
        if model_pos >= 0:
            # Earlier position = higher confidence
            position_factor = 1.0 - (model_pos / len(product_name))
            confidence += position_factor * 0.3
        
        # Higher confidence if DeLonghi brand is present
        if 'delonghi' in product_name.lower():
            confidence += 0.2
        
        # Cap at 1.0
        confidence = min(confidence, 1.0)
        
        return model, confidence
    
    @classmethod
    def normalize_for_matching(cls, model: str) -> str:
        """
        Aggressive normalization for matching - removes ALL special chars
        
        Args:
            model: Model code
            
        Returns:
            Normalized model (only letters and numbers)
            
        Examples:
            >>> ModelExtractor.normalize_for_matching("EC 9865 M")
            'EC9865M'
            >>> ModelExtractor.normalize_for_matching("ECAM 22.110.B")
            'ECAM22110B'
            >>> ModelExtractor.normalize_for_matching("DL EC885.BG")
            'EC885BG'
        """
        if not model:
            return ""
        
        # Check if DLSC (accessories) - preserve it
        is_dlsc = 'DLSC' in model.upper()
        
        # Remove ALL non-alphanumeric characters
        normalized = re.sub(r'[^A-Z0-9]', '', model.upper())
        
        # Remove DL prefix (except for DLSC)
        if not is_dlsc and normalized.startswith('DL'):
            normalized = normalized[2:]
        
        return normalized
    
    @classmethod
    def match_models(cls, model1: str, model2: str, strict: bool = True) -> bool:
        """
        Check if two models match (accounting for variations)
        
        Args:
            model1: First model code
            model2: Second model code
            strict: If True, require exact match. If False, allow color variants
            
        Returns:
            True if models match
            
        Examples:
            >>> ModelExtractor.match_models("EC9865.M", "EC9865M")
            True
            >>> ModelExtractor.match_models("EC 9865 M", "EC9865M")
            True
            >>> ModelExtractor.match_models("ECAM 22.110.B", "ECAM22110B")
            True
            >>> ModelExtractor.match_models("EC685.R", "EC685.W")
            False
            >>> ModelExtractor.match_models("EC685.R", "EC685", strict=False)
            True
        """
        if not model1 or not model2:
            return False
        
        # Aggressive normalization (remove all special chars)
        m1_norm = cls.normalize_for_matching(model1)
        m2_norm = cls.normalize_for_matching(model2)
        
        # Exact match after normalization
        if m1_norm == m2_norm:
            return True
        
        # If not strict, allow base model matching (ignore color suffix)
        if not strict:
            # Remove last 1-2 characters if they are letters (color codes)
            # EC685R → EC685, EC685BG → EC685
            m1_base = re.sub(r'[A-Z]{1,2}$', '', m1_norm)
            m2_base = re.sub(r'[A-Z]{1,2}$', '', m2_norm)
            
            if m1_base == m2_base and len(m1_base) >= 4:
                return True
        
        return False
    
    @classmethod
    def get_model_variants(cls, model: str) -> List[str]:
        """
        Get possible variants of a model code
        
        Args:
            model: Model code
            
        Returns:
            List of possible variant representations
        """
        variants = [model]
        
        # Add version without dots
        no_dots = model.replace('.', '')
        if no_dots != model:
            variants.append(no_dots)
        
        # Add version with spaces
        with_spaces = re.sub(r'(\d)([A-Z])', r'\1 \2', model)
        if with_spaces != model:
            variants.append(with_spaces)
        
        return list(set(variants))


# Convenience functions
def extract_model(product_name: str) -> Optional[str]:
    """Extract model from product name"""
    return ModelExtractor.extract_model(product_name)


def match_models(model1: str, model2: str) -> bool:
    """Check if two models match"""
    return ModelExtractor.match_models(model1, model2)

