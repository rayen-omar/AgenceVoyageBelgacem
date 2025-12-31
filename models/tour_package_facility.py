# -*- coding: utf-8 -*-

from odoo import models, fields


class TourPackageFacility(models.Model):
    _name = 'tour.package.facility'
    _description = 'Équipement du Forfait Touristique'
    _order = 'name'

    tour_package_id = fields.Many2one('tour.package', string='Forfait Touristique', required=True, ondelete='cascade')
    name = fields.Char(string='Titre', required=True)
    description = fields.Text(string='Description')
