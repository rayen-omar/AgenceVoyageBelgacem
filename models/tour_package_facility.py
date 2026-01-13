# -*- coding: utf-8 -*-

from odoo import models, fields


class TourPackageFacility(models.Model):
    _name = 'tour.package.facility'
    _description = 'Service/Équipement du Forfait Touristique'
    _order = 'sequence, name'

    sequence = fields.Integer(string='Ordre', default=10, help="Ordre d'affichage", index=True)
    tour_package_id = fields.Many2one('tour.package', string='Forfait Touristique', required=True, ondelete='cascade')
    name = fields.Char(string='Service/Équipement', required=True, help="Nom du service ou équipement inclus dans le voyage")
    description = fields.Text(string='Description', help="Description détaillée du service ou équipement")
