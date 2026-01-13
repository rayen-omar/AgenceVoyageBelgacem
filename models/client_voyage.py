# -*- coding: utf-8 -*-

from odoo import models, fields


class ClientVoyage(models.Model):
    _name = 'client.voyage'
    _description = 'Client'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    email = fields.Char(string='Email')
    telephone = fields.Char(string='Téléphone')
    adresse = fields.Text(string='Adresse')
