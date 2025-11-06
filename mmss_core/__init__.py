"""
MMSS Core System - Многоуровневая Мета-Семантическая Система
Активация всех пакетов фрактальной пересборки
"""

from .fractal_reassembly import FractalReassemblyEngine
from .temporal_navigator import TemporalNavigator
from .context_weaver import ContextWeaver
from .prompt_generator import MMSSPromptGenerator
from .domains import (
    DOMAINS_LIST,
    DOMAIN_D_F_OPTIMAL,
    DOMAIN_SUBDOMAINS,
    get_domain_d_f,
    get_subdomains,
    get_all_domains_with_subdomains
)

__all__ = [
    'FractalReassemblyEngine',
    'TemporalNavigator', 
    'ContextWeaver',
    'MMSSPromptGenerator',
    'DOMAINS_LIST',
    'DOMAIN_D_F_OPTIMAL',
    'DOMAIN_SUBDOMAINS',
    'get_domain_d_f',
    'get_subdomains',
    'get_all_domains_with_subdomains'
]

__version__ = "2.0.EC"
