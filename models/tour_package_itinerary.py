# -*- coding: utf-8 -*-

from odoo import models, fields


class TourPackageItinerary(models.Model):
    _name = 'tour.package.itinerary'
    _description = 'Jour du Forfait Touristique'
    _order = 'sequence, name'

    sequence = fields.Integer(string='Ordre', default=10, help="Ordre d'affichage des jours", index=True)
    tour_package_id = fields.Many2one('tour.package', string='Forfait Touristique', required=True, ondelete='cascade')
    name = fields.Char(string='Jour', required=True, help='Titre du jour (ex: Jour 1 - Arrivée)')
    location_id = fields.Many2one('location.voyage', string='Destination', help='Destination principale de ce jour')
    hotel_id = fields.Many2one('hotel.voyage', string='Hôtel', help='Hôtel pour cette nuit')
    night = fields.Integer(string='Nombre de Nuits', default=0, help='Nombre de nuits passées à cet hôtel')
    places_covered = fields.Text(string='Lieux Visités', help='Liste des lieux et attractions visités ce jour')
