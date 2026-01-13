# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TravelReservation(models.Model):
    _name = 'travel.reservation'
    _description = 'Réservation de Voyage'
    _order = 'date_reservation desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', readonly=True, copy=False, default='New', tracking=True)
    # ==================== Informations Client ====================
    client_id = fields.Many2one('client.voyage', string='Client', required=True, tracking=True)
    client_email = fields.Char(related='client_id.email', string='Email', readonly=True)
    client_phone = fields.Char(related='client_id.telephone', string='Téléphone', readonly=True)
    responsible_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user, tracking=True)
    
    # ==================== Informations Forfait ====================
    tour_package_id = fields.Many2one('tour.package', string='Forfait', required=True, tracking=True)
    package_type = fields.Selection(related='tour_package_id.package_type', string='Type de Forfait', readonly=True)
    price_per_person = fields.Float(related='tour_package_id.price_per_person', string='Prix/Personne', readonly=True)
    
    # ==================== Dates ====================
    date_reservation = fields.Date(string='Date Réservation', default=fields.Date.today, required=True)
    booking_date = fields.Datetime(string='Date de Réservation', default=fields.Datetime.now, tracking=True)
    date_depart = fields.Date(string='Date Départ', required=True, tracking=True)
    date_retour = fields.Date(string='Date Retour', tracking=True)
    
    # ==================== Voyageurs ====================
    number_of_travelers = fields.Integer(string='Nombre de Personnes', default=1, tracking=True)
    any_child = fields.Boolean(string='Avec Enfants?', default=False)
    number_of_children = fields.Integer(string='Nombre d\'Enfants', default=0)
    cost_per_child = fields.Float(string='Coût/Enfant', default=0.0)
    
    # ==================== Services ====================
    transport_ids = fields.One2many('travel.reservation.transport', 'reservation_id', string='Transport')
    flight_ids = fields.One2many('travel.reservation.flight', 'reservation_id', string='Vols')
    facility_ids = fields.One2many('travel.reservation.facility', 'reservation_id', string='Équipements')
    terms_conditions = fields.Html(string='Termes et Conditions')
    
    # ==================== Montants ====================
    amount_untaxed = fields.Float(string='Montant HT', compute='_compute_total_amount', store=True)
    discount_percentage = fields.Float(string='Remise (%)', default=0.0)
    discount_method = fields.Selection([
        ('percent', 'Pourcentage'),
        ('fixed', 'Prix Fixe')
    ], string='Méthode Remise', default='percent')
    total_amount = fields.Float(string='Montant Total', compute='_compute_total_amount', store=True, tracking=True)
    
    # ==================== Facturation ====================
    invoice_id = fields.Many2one('account.move', string='Facture', readonly=True, copy=False)
    invoice_status = fields.Selection([
        ('no', 'Pas de Facture'),
        ('draft', 'Brouillon'),
        ('posted', 'Validée')
    ], string='Statut Facture', compute='_compute_invoice_status', store=True)
    
    # ==================== Statut ====================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)
    
    # ==================== Informations Société ====================
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Devise', readonly=True)

    @api.model
    def create(self, vals):
        """Crée une nouvelle réservation avec numéro de séquence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.reservation') or 'New'
        return super().create(vals)

    @api.onchange('tour_package_id')
    def _onchange_tour_package_id(self):
        """Ajoute automatiquement les équipements du forfait sélectionné"""
        if self.tour_package_id and self.tour_package_id.facility_ids:
            # Récupère les IDs des équipements déjà présents pour éviter les doublons
            existing_facility_names = {fac.name for fac in self.facility_ids if fac.name}
            
            # Ajoute les équipements du forfait qui ne sont pas déjà présents
            for package_facility in self.tour_package_id.facility_ids:
                if package_facility.name not in existing_facility_names:
                    self.facility_ids = [(0, 0, {
                        'name': package_facility.name,
                        'description': package_facility.description,
                        'from_package': True,
                    })]

    @api.depends('number_of_travelers', 'price_per_person', 'number_of_children', 
                 'cost_per_child', 'transport_ids', 'flight_ids', 'discount_percentage')
    def _compute_total_amount(self):
        """Calcule le montant total de la réservation"""
        for record in self:
            # Calcul du montant de base (adultes)
            base = (record.number_of_travelers or 0) * (record.price_per_person or 0.0)
            
            # Calcul du montant pour les enfants
            child = (record.number_of_children or 0) * (record.cost_per_child or 0.0) if record.any_child else 0.0
            
            # Calcul du montant des transports
            transport = sum(record.transport_ids.mapped('cost') or [0.0])
            
            # Calcul du montant des vols
            flight = sum(record.flight_ids.mapped('price') or [0.0])
            
            # Sous-total avant remise
            subtotal = base + child + transport + flight
            record.amount_untaxed = subtotal
            
            # Application de la remise
            discount_amount = subtotal * (record.discount_percentage / 100.0) if record.discount_percentage > 0 else 0.0
            record.total_amount = subtotal - discount_amount

    @api.depends('invoice_id', 'invoice_id.state')
    def _compute_invoice_status(self):
        """Calcule le statut de la facture associée"""
        for record in self:
            if not record.invoice_id:
                record.invoice_status = 'no'
            elif record.invoice_id.state == 'posted':
                record.invoice_status = 'posted'
            elif record.invoice_id.state == 'draft':
                record.invoice_status = 'draft'
            else:
                record.invoice_status = 'no'

    # ==================== Actions de workflow ====================
    
    def action_confirm(self):
        """Confirme la réservation"""
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Marque la réservation comme terminée"""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Annule la réservation"""
        self.write({'state': 'cancelled'})

    def action_draft(self):
        """Remet la réservation en brouillon"""
        self.write({'state': 'draft'})

    # ==================== Méthodes privées pour la facturation ====================
    
    def _get_or_create_partner(self):
        """Récupère ou crée un partenaire à partir du client"""
        partner = self.env['res.partner'].search([('name', '=', self.client_id.name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.client_id.name,
                'email': self.client_id.email or False,
                'phone': self.client_id.telephone or False,
                'street': self.client_id.adresse or False,
                'customer_rank': 1,
            })
        return partner

    def _get_journal_and_account(self):
        """Récupère le journal et le compte pour la facturation"""
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not journal:
            raise UserError(_('Aucun journal de vente trouvé. Veuillez le configurer.'))
        
        account = journal.default_account_id or self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', self.env.company.id),
            ('deprecated', '=', False)
        ], limit=1)
        if not account:
            raise UserError(_('Aucun compte de revenus trouvé. Veuillez le configurer.'))
        
        return journal, account

    def _prepare_invoice_lines(self, account):
        """Prépare les lignes de facture à partir de la réservation"""
        lines = []
        
        # Ligne pour les adultes
        if self.number_of_travelers > 0:
            lines.append((0, 0, {
                'name': f"{self.tour_package_id.name} (Adultes)",
                'quantity': self.number_of_travelers,
                'price_unit': self.price_per_person,
                'account_id': account.id,
            }))
        
        # Ligne pour les enfants
        if self.any_child and self.number_of_children > 0:
            lines.append((0, 0, {
                'name': "Charges Enfants",
                'quantity': self.number_of_children,
                'price_unit': self.cost_per_child,
                'account_id': account.id,
            }))
        
        # Lignes pour les transports
        category_map = {
            'hotel': 'Hôtel',
            'car': 'Voiture',
            'bus': 'Bus',
            'train': 'Train',
            'other': 'Autre'
        }
        for transport in self.transport_ids:
            category_label = category_map.get(transport.category, transport.category or 'Autre')
            desc = f" - {transport.description}" if transport.description else ""
            lines.append((0, 0, {
                'name': f"Transport: {category_label}{desc}",
                'quantity': 1,
                'price_unit': transport.cost or 0.0,
                'account_id': account.id,
            }))
        
        # Lignes pour les vols
        for flight in self.flight_ids:
            parts = [f"Vol: {flight.person_name or 'N/A'}"]
            if flight.source_location or flight.destination_location:
                parts.append(f"{flight.source_location or ''} → {flight.destination_location or ''}")
            if flight.pnr_no:
                parts.append(f"(PNR: {flight.pnr_no})")
            lines.append((0, 0, {
                'name': " - ".join(parts),
                'quantity': 1,
                'price_unit': flight.price or 0.0,
                'account_id': account.id,
            }))
        
        # Application de la remise si applicable
        if self.discount_percentage > 0:
            for line in lines:
                line[2]['discount'] = self.discount_percentage
        
        return lines

    # ==================== Actions publiques ====================
    
    def action_create_invoice(self):
        """Crée une facture à partir de la réservation"""
        self.ensure_one()
        
        if self.state == 'draft':
            raise UserError(_('Veuillez confirmer la réservation avant de créer une facture.'))
        
        partner = self._get_or_create_partner()
        journal, account = self._get_journal_and_account()
        invoice_lines = self._prepare_invoice_lines(account)
        
        # Si une facture existe déjà
        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                self.invoice_id.invoice_line_ids.unlink()
                self.invoice_id.write({'invoice_line_ids': invoice_lines})
                return self.action_view_invoice()
            else:
                raise UserError(_('La facture est déjà validée. Impossible de la modifier.'))
        
        # Création de la nouvelle facture
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'invoice_origin': self.name,
            'ref': self.name,
            'invoice_line_ids': invoice_lines,
        })
        self.invoice_id = invoice.id
        return self.action_view_invoice()

    def action_view_invoice(self):
        """Ouvre la vue de la facture associée"""
        self.ensure_one()
        if not self.invoice_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }


class ReservationTransport(models.Model):
    """Modèle pour les transports associés à une réservation"""
    _name = 'travel.reservation.transport'
    _description = 'Transport de Réservation'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Ordre', default=10)
    reservation_id = fields.Many2one('travel.reservation', string='Réservation', required=True, ondelete='cascade')
    category = fields.Selection([
        ('hotel', 'Hôtel'),
        ('car', 'Voiture'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('other', 'Autre')
    ], string='Catégorie', default='other', required=True)
    description = fields.Char(string='Description')
    cost = fields.Float(string='Coût', default=0.0, digits=(16, 2))


class ReservationFlight(models.Model):
    """Modèle pour les vols associés à une réservation"""
    _name = 'travel.reservation.flight'
    _description = 'Vol de Réservation'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Ordre', default=10)
    reservation_id = fields.Many2one('travel.reservation', string='Réservation', required=True, ondelete='cascade')
    person_name = fields.Char(string='Nom Personne')
    pnr_no = fields.Char(string='N° PNR')
    takeoff_time = fields.Datetime(string='Heure Départ')
    landing_time = fields.Datetime(string='Heure Arrivée')
    source_location = fields.Char(string='Lieu Départ')
    destination_location = fields.Char(string='Lieu Arrivée')
    price = fields.Float(string='Prix', default=0.0, digits=(16, 2))


class ReservationFacility(models.Model):
    """Modèle pour les équipements associés à une réservation"""
    _name = 'travel.reservation.facility'
    _description = 'Équipement de Réservation'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Ordre', default=10)
    reservation_id = fields.Many2one('travel.reservation', string='Réservation', required=True, ondelete='cascade')
    name = fields.Char(string='Service/Équipement', required=True)
    description = fields.Text(string='Description')
    from_package = fields.Boolean(string='Du Forfait', default=False, readonly=True, 
                                  help='Indique si cet équipement provient du forfait sélectionné')


class ReservationLine(models.Model):
    """Modèle pour les lignes de réservation (voyageurs) - Non utilisé actuellement"""
    _name = 'travel.reservation.line'
    _description = 'Ligne de Réservation'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Ordre', default=10)
    reservation_id = fields.Many2one('travel.reservation', string='Réservation', required=True, ondelete='cascade')
    name = fields.Char(string='Nom Complet', required=True)
    date_naissance = fields.Date(string='Date de Naissance')
    age = fields.Integer(string='Âge', compute='_compute_age', store=False)
    passport_number = fields.Char(string='N° Passeport')
    passport_expiry = fields.Date(string='Expiration Passeport')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Téléphone')
    traveler_type = fields.Selection([
        ('adult', 'Adulte'),
        ('child', 'Enfant'),
        ('infant', 'Bébé')
    ], string='Type de Voyageur', default='adult')
    notes = fields.Text(string='Notes')
    
    @api.depends('date_naissance')
    def _compute_age(self):
        """Calcule l'âge à partir de la date de naissance"""
        today = fields.Date.today()
        for record in self:
            if record.date_naissance:
                record.age = (today - record.date_naissance).days // 365
            else:
                record.age = 0
