# -*- coding: utf-8 -*-

from odoo import models, fields


class LocationVoyage(models.Model):
    _name = 'location.voyage'
    _description = 'Destination'
    _order = 'name'

    name = fields.Char(string='Nom du lieu', required=True)
    description = fields.Text(string='Description')
    pays = fields.Char(string='Pays', required=True)
    ville = fields.Char(string='Ville', required=True)
    adresse = fields.Text(string='Adresse complète')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
