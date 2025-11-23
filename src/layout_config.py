"""Layout configuration for PDF generation."""

from typing import Dict, Any, List

# Image placement rules
# 'max_images': Maximum number of images to insert per document
# 'placement_strategy': 'auto' (distributed), 'end' (at the end), 'specific' (after specific headers)
# 'min_spacing': Minimum number of paragraphs between images

LAYOUT_CONFIG: Dict[str, Any] = {
    'chapter': {
        'max_images': 4,
        'placement_strategy': 'auto',
        'min_spacing': 3,
        'preferred_sections': [
            '## Игра Сцены',
            '## Вовлеченность',
            '## Упражнение'
        ],
        'avoid_sections': [
            '### Инструкции',
            '### Цель',
            '## Обзор'
        ],
    },
    'jam_plan': {
        'max_images': 3,
        'placement_strategy': 'auto',
        'min_spacing': 2,
        'preferred_sections': ['## Блок', '## Block', '### Шаг', '### Step'],
        'avoid_sections': ['# ', '## Кратко', '## Overview'],
    }
}

# Image pools (fallback if not provided dynamically)
IMAGE_POOLS: Dict[str, List[str]] = {
    'chapter': [
        'Screenshot 2025-11-23 at 22.33.09.png',
        'Screenshot 2025-11-23 at 22.34.18.png',
        'kristen_schaal_performance.jpg',
        'john_early_performance.jpg'
    ],
    'jam_plan': [
        'bigger_show.jpg',
        'asssscat_will_ferrell.jpg',
        'ego_nwodim_asssscat.jpg',
        'jon_gabrus_asssscat.jpg',
        'ucb_improv_training.jpg'
    ]
}
