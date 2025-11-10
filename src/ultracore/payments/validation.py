"""
BSB Validation & Account Verification
"""
from typing import Dict, Optional


class BSBValidator:
    """BSB (Bank State Branch) Validation"""
    
    def __init__(self):
        self.bsb_directory = {
            '063': {'institution': 'Commonwealth Bank', 'state': 'NSW'},
            '732': {'institution': 'Westpac', 'state': 'NSW'},
            '013': {'institution': 'ANZ', 'state': 'NSW'},
            '083': {'institution': 'NAB', 'state': 'NSW'}
        }
    
    async def validate_bsb(self, bsb: str) -> bool:
        """Validate BSB format and existence"""
        bsb_clean = bsb.replace('-', '')
        if len(bsb_clean) != 6 or not bsb_clean.isdigit():
            return False
        return bsb_clean[:3] in self.bsb_directory
    
    async def lookup_bsb(self, bsb: str) -> Optional[Dict]:
        """Lookup BSB details"""
        bsb_clean = bsb.replace('-', '')
        bsb_prefix = bsb_clean[:3]
        if bsb_prefix in self.bsb_directory:
            return {'bsb': bsb_clean, **self.bsb_directory[bsb_prefix]}
        return None
