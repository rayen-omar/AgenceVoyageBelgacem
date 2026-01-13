# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TravelPurchase(models.Model):
    _name = 'travel.purchase'
    _description = 'Achat Agence Voyage'
    _order = 'date_purchase desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', readonly=True, copy=False, default='New', tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Fournisseur', required=True, tracking=True, domain=[('supplier_rank', '>', 0)])
    vendor_email = fields.Char(related='vendor_id.email', string='Email', readonly=True, store=False)
    vendor_phone = fields.Char(related='vendor_id.phone', string='Téléphone', readonly=True, store=False)
    date_purchase = fields.Date(string='Date Achat', default=fields.Date.today, required=True, tracking=True)
    purchase_date = fields.Datetime(string='Date de Commande', default=fields.Datetime.now, tracking=True)
    responsible_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user, tracking=True)
    
    # Lignes d'achat
    purchase_line_ids = fields.One2many('travel.purchase.line', 'purchase_id', string='Lignes d\'Achat')
    
    # Montants
    amount_untaxed = fields.Float(string='Montant HT', compute='_compute_total_amount', store=True)
    discount_percentage = fields.Float(string='Remise (%)', default=0.0, tracking=True)
    tax_amount = fields.Float(string='Montant TVA', compute='_compute_total_amount', store=True)
    total_amount = fields.Float(string='Montant Total TTC', compute='_compute_total_amount', store=True, tracking=True)
    
    # Facture
    vendor_bill_id = fields.Many2one('account.move', string='Facture Fournisseur', readonly=True, copy=False)
    bill_status = fields.Selection([
        ('no', 'Pas de Facture'),
        ('draft', 'Brouillon'),
        ('posted', 'Validée')
    ], string='Statut Facture', compute='_compute_bill_status', store=True)
    
    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)
    
    # Informations supplémentaires
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Devise', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.purchase') or 'New'
        return super().create(vals)

    @api.depends('purchase_line_ids', 'purchase_line_ids.subtotal', 'discount_percentage')
    def _compute_total_amount(self):
        for record in self:
            subtotal = sum(record.purchase_line_ids.mapped('subtotal') or [0.0])
            discount = subtotal * (record.discount_percentage / 100.0) if record.discount_percentage > 0 else 0.0
            amount_untaxed = subtotal - discount
            # Calcul TVA (19% par défaut, peut être personnalisé)
            tax_rate = 0.19  # 19% TVA
            tax_amount = amount_untaxed * tax_rate
            total_amount = amount_untaxed + tax_amount
            
            record.amount_untaxed = amount_untaxed
            record.tax_amount = tax_amount
            record.total_amount = total_amount

    @api.depends('vendor_bill_id', 'vendor_bill_id.state')
    def _compute_bill_status(self):
        for record in self:
            if not record.vendor_bill_id:
                record.bill_status = 'no'
            elif record.vendor_bill_id.state == 'posted':
                record.bill_status = 'posted'
            elif record.vendor_bill_id.state == 'draft':
                record.bill_status = 'draft'
            else:
                record.bill_status = 'no'

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def _get_journal_and_account(self):
        """Récupère le journal et le compte pour les factures d'achat"""
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not journal:
            raise UserError(_('Aucun journal d\'achat trouvé. Veuillez le configurer.'))
        
        account = journal.default_account_id or self.env['account.account'].search([
            ('account_type', '=', 'expense'),
            ('company_id', '=', self.env.company.id),
            ('deprecated', '=', False)
        ], limit=1)
        if not account:
            raise UserError(_('Aucun compte de dépense trouvé. Veuillez le configurer.'))
        return journal, account

    def _prepare_bill_lines(self, account):
        """Prépare les lignes de facture fournisseur"""
        lines = []
        # Appliquer la remise sur chaque ligne proportionnellement
        total_before_discount = sum(self.purchase_line_ids.mapped('subtotal') or [0.0])
        discount_factor = (1 - self.discount_percentage / 100.0) if self.discount_percentage > 0 else 1.0
        
        for line in self.purchase_line_ids:
            # Prix unitaire après remise
            unit_price_after_discount = line.unit_price * discount_factor
            lines.append((0, 0, {
                'name': line.description or line.product_name,
                'quantity': line.quantity,
                'price_unit': unit_price_after_discount,
                'account_id': account.id,
                'tax_ids': [(6, 0, [])],  # Taxes peuvent être ajoutées ici
            }))
        return lines

    def action_create_vendor_bill(self):
        """Créer une facture fournisseur"""
        self.ensure_one()
        if self.state == 'draft':
            raise UserError(_('Veuillez confirmer l\'achat avant de créer une facture.'))
        
        if self.vendor_bill_id:
            if self.vendor_bill_id.state == 'draft':
                # Mettre à jour la facture existante
                journal, account = self._get_journal_and_account()
                bill_lines = self._prepare_bill_lines(account)
                self.vendor_bill_id.invoice_line_ids.unlink()
                self.vendor_bill_id.write({'invoice_line_ids': bill_lines})
                return self.action_view_vendor_bill()
            else:
                raise UserError(_('La facture est déjà validée. Impossible de la modifier.'))
        
        journal, account = self._get_journal_and_account()
        bill_lines = self._prepare_bill_lines(account)
        
        # Calculer le montant avec remise
        subtotal = self.amount_untaxed
        tax_amount = self.tax_amount
        
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor_id.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'invoice_origin': self.name,
            'ref': self.name,
            'invoice_line_ids': bill_lines,
        })
        
        self.vendor_bill_id = bill.id
        return self.action_view_vendor_bill()

    def action_view_vendor_bill(self):
        """Ouvrir la facture fournisseur"""
        self.ensure_one()
        if not self.vendor_bill_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture Fournisseur',
            'res_model': 'account.move',
            'res_id': self.vendor_bill_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class TravelPurchaseLine(models.Model):
    _name = 'travel.purchase.line'
    _description = 'Ligne d\'Achat'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    purchase_id = fields.Many2one('travel.purchase', required=True, ondelete='cascade')
    product_name = fields.Char(string='Produit/Service', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantité', default=1.0, required=True)
    unit_price = fields.Float(string='Prix Unitaire', required=True, digits=(16, 2))
    subtotal = fields.Float(string='Sous-total', compute='_compute_subtotal', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

