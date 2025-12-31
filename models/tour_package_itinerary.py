# -*- coding: utf-8 -*-

from odoo import models, fields


class TourPackageItinerary(models.Model):
    _name = 'tour.package.itinerary'
    _description = 'Jour du Forfait Touristique'
    _order = 'name'

    tour_package_id = fields.Many2one('tour.package', string='Forfait Touristique', required=True, ondelete='cascade')
    name = fields.Char(string='Days', required=True, help='Titre du jour')
    location_id = fields.Many2one('location.voyage', string='Location')
    hotel_id = fields.Many2one('hotel.voyage', string='Hotels')
    night = fields.Integer(string='Night', default=0)
    places_covered = fields.Text(string='Places Covered')
