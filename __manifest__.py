# -*- coding: utf-8 -*-
{
    'name': 'Agence Voyage Belgacem',
    'technical_name': 'AgenceVoyageBelgacem',
    'version': '16.0.1.0.0',
    'category': 'Travel',
    'summary': 'Module de gestion pour Agence Voyage Belgacem',
    'description': """
        Module personnalisé pour la gestion de l'agence de voyage Belgacem
        ==================================================================
        
        Fonctionnalités:
        * Gestion des destinations
        * Gestion des clients
        * Gestion des hébergements
        * Gestion des forfaits touristiques
    """,
    'author': 'Agence Voyage Belgacem',
    'website': 'https://www.agencevoyagebelgacem.com',
    'depends': ['base', 'mail'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/location_views.xml',
        'views/client_views.xml',
        'views/hotel_views.xml',
        'views/tour_package_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'AgenceVoaygeBelgacem/static/css/custom_styles.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
