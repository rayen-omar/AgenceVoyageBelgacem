# Module Agence Voyage Belgacem

Module personnalisé pour la gestion de l'agence de voyage Belgacem.

## Installation

1. Assurez-vous que le module est dans le dossier `addons` d'Odoo
2. Mettez à jour la liste des applications dans Odoo
3. Installez le module "Agence Voyage Belgacem"

## Structure du module

```
AgenceVoyageBelgacem/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── location_voyage.py          # Destinations
│   ├── client_voyage.py             # Clients
│   ├── hotel_voyage.py              # Hébergements
│   ├── tour_package.py              # Forfaits Touristiques
│   ├── tour_package_itinerary.py    # Jours des forfaits
│   └── tour_package_facility.py     # Équipements des forfaits
├── views/
│   ├── menu_views.xml               # Menu principal
│   ├── location_views.xml           # Vues pour les destinations
│   ├── client_views.xml             # Vues pour les clients
│   ├── hotel_views.xml              # Vues pour les hébergements
│   └── tour_package_views.xml       # Vues pour les forfaits
├── security/
│   └── ir.model.access.csv          # Droits d'accès
├── data/
│   └── ir_sequence_data.xml         # Séquence pour les forfaits
├── static/
│   └── css/
│       └── custom_styles.css        # Styles personnalisés
└── README.md
```

## Fonctionnalités

### Destinations
- Gestion des lieux de voyage (villes, monuments, aéroports, etc.)
- Informations : nom, description, pays, ville, adresse, coordonnées GPS
- Types de lieux : Aéroport, Gare, Hôtel, Monument, Plage, Restaurant, Autre

### Clients
- Gestion des clients avec informations essentielles
- Informations : nom, email, téléphone, adresse

### Hébergements
- Gestion des hébergements disponibles
- Informations : nom, adresse, ville, pays, téléphone, email, nombre d'étoiles, description

### Forfaits Touristiques
- Gestion des forfaits touristiques
- Informations : nom, référence (TP/00001), type de forfait (Flexi/Group), type de voyage (Domestic/International)
- Durée : Total Days, Total Nights
- Prix : Price/Person
- Saison : Summer, Winter, Spring, Autumn, All Season
- Jours : Gestion détaillée de chaque jour avec destination, hébergement, nuit, lieux visités
- Équipements : Liste des équipements inclus dans le forfait

## Auteur

Agence Voyage Belgacem

## Licence

LGPL-3
