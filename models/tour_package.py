# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TourPackage(models.Model):
    _name = 'tour.package'
    _description = 'Forfait Touristique'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom du forfait', required=True, tracking=True)
    sequence = fields.Char(string='Référence', readonly=True, copy=False, default='New')
    package_type = fields.Selection([
        ('flexi', 'Flexi Package'),
        ('group', 'Group Package'),
    ], string='Type de forfait', default='flexi', required=True, tracking=True)

    location_ids = fields.Many2many(
        'location.voyage',
        string='Destinations',
        help='Destinations incluses dans ce forfait'
    )

    tour_type = fields.Selection([
        ('domestic', 'Domestic'),
        ('international', 'International'),
    ], string='Type de voyage', default='domestic', tracking=True)
    total_days = fields.Integer(string='Total Days', default=0, tracking=True)
    total_nights = fields.Integer(string='Total Nights', default=0, tracking=True)
    price_per_person = fields.Float(string='Price/Person', digits=(16, 2), tracking=True)
    season = fields.Selection([
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('autumn', 'Autumn'),
        ('all', 'All Season'),
    ], string='Season', default='summer', tracking=True)

    itinerary_ids = fields.One2many(
        'tour.package.itinerary',
        'tour_package_id',
        string='Jours'
    )

    facility_ids = fields.One2many(
        'tour.package.facility',
        'tour_package_id',
        string='Équipements'
    )

    active = fields.Boolean(string='Actif', default=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Devise', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('tour.package') or 'New'
        return super(TourPackage, self).create(vals)

    def action_book(self):
        """Action pour réserver le forfait"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Réserver',
            'res_model': 'tour.package',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
