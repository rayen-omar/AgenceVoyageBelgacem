# -*- coding: utf-8 -*-

from odoo import models, fields


class HotelVoyage(models.Model):
    _name = 'hotel.voyage'
    _description = 'Hotel'
    _order = 'name'

    name = fields.Char(string='Nom de l\'hotel', required=True)
    adresse = fields.Text(string='Adresse')
    ville = fields.Char(string='Ville')
    pays = fields.Char(string='Pays')
    telephone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    nombre_etoiles = fields.Selection([
        ('1', '1 étoile'),
        ('2', '2 étoiles'),
        ('3', '3 étoiles'),
        ('4', '4 étoiles'),
        ('5', '5 étoiles'),
    ], string='Nombre d\'étoiles')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True)
