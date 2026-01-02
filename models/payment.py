# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TravelPayment(models.Model):
    _name = 'travel.payment'
    _description = 'Paiement de Voyage'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', readonly=True, copy=False, default='New', tracking=True)
    
    reservation_id = fields.Many2one('travel.reservation', string='Réservation', required=True, tracking=True)
    partner_id = fields.Many2one('client.voyage', string='Client', related='reservation_id.client_id', store=True, readonly=True)
    
    date = fields.Date(string='Date de Paiement', default=fields.Date.today, required=True, tracking=True)
    amount = fields.Float(string='Montant', required=True, tracking=True)
    
    payment_method = fields.Selection([
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement Bancaire'),
        ('credit_card', 'Carte de Crédit'),
        ('mobile_money', 'Mobile Money'),
    ], string='Mode de Paiement', required=True, default='cash', tracking=True)
    
    reference = fields.Char(string='Référence Paiement', help='N° de chèque, référence de virement, etc.')
    
    journal_id = fields.Many2one('account.journal', string='Journal', 
                                 domain=[('type', 'in', ['cash', 'bank'])],
                                 help='Journal comptable pour ce paiement')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Validé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True, required=True)
    
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Devise', readonly=True)
    move_id = fields.Many2one('account.move', string='Écriture Comptable', readonly=True, copy=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.payment') or 'New'
        return super(TravelPayment, self).create(vals)
    
    def action_post(self):
        """Valider le paiement"""
        for record in self:
            if record.amount <= 0:
                raise UserError(_("Le montant du paiement doit être supérieur à zéro."))
            record.write({'state': 'posted'})
        return True
    
    def action_cancel(self):
        """Annuler le paiement"""
        self.write({'state': 'cancelled'})
        return True
    
    def action_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft'})
        return True
    
    def action_print_receipt(self):
        """Imprimer le reçu de paiement"""
        self.ensure_one()
        return self.env.ref('AgenceVoaygeBelgacem.action_report_payment_receipt').report_action(self)
