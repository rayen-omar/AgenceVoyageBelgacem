# -*- coding: utf-8 -*-

from . import models


def post_init_hook(cr, registry):
    """
    Hook appelé après l'installation du module pour créer les droits d'accès
    et la vue pour travel.reservation.facility
    """
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Vérifier si le modèle travel.reservation.facility existe
    try:
        if 'travel.reservation.facility' in env:
            model = env['ir.model'].search([('model', '=', 'travel.reservation.facility')], limit=1)
            if model:
                # Création des droits d'accès pour les utilisateurs
                existing_user = env['ir.model.access'].search([
                    ('name', '=', 'travel.reservation.facility.user'),
                    ('model_id', '=', model.id)
                ], limit=1)
                if not existing_user:
                    env['ir.model.access'].create({
                        'name': 'travel.reservation.facility.user',
                        'model_id': model.id,
                        'group_id': env.ref('base.group_user').id,
                        'perm_read': True,
                        'perm_write': True,
                        'perm_create': True,
                        'perm_unlink': True,
                    })
                
                # Création des droits d'accès pour les administrateurs
                existing_manager = env['ir.model.access'].search([
                    ('name', '=', 'travel.reservation.facility.manager'),
                    ('model_id', '=', model.id)
                ], limit=1)
                if not existing_manager:
                    env['ir.model.access'].create({
                        'name': 'travel.reservation.facility.manager',
                        'model_id': model.id,
                        'group_id': env.ref('base.group_system').id,
                        'perm_read': True,
                        'perm_write': True,
                        'perm_create': True,
                        'perm_unlink': True,
                    })
                
                # Création de la vue héritée pour les équipements
                existing_view = env['ir.ui.view'].search([
                    ('name', '=', 'travel.reservation.form.facility')
                ], limit=1)
                if not existing_view:
                    view_arch = """<?xml version="1.0"?>
                    <xpath expr="//notebook" position="inside">
                        <page string="Équipements" icon="fa-star">
                            <field name="facility_ids" nolabel="1" optional="hide">
                                <tree editable="bottom" create="1" delete="1" default_order="sequence,name">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name" string="Service/Équipement" required="1"/>
                                    <field name="description" string="Description"/>
                                    <field name="from_package" string="Du Forfait" readonly="1"/>
                                </tree>
                                <form string="Équipement" create="1" edit="1" delete="1">
                                    <sheet>
                                        <group>
                                            <group string="Informations">
                                                <field name="name" string="Service/Équipement" required="1" 
                                                       placeholder="Ex: Petit-déjeuner inclus, WiFi gratuit, Piscine..."/>
                                                <field name="from_package" string="Du Forfait" readonly="1"/>
                                            </group>
                                        </group>
                                        <group>
                                            <group string="Description">
                                                <field name="description" string="Description détaillée" 
                                                       placeholder="Description détaillée du service ou équipement..."/>
                                            </group>
                                        </group>
                                    </sheet>
                                </form>
                            </field>
                        </page>
                    </xpath>"""
                    
                    parent_view = env.ref('AgenceVoaygeBelgacem.view_reservation_form', raise_if_not_found=False)
                    if parent_view:
                        env['ir.ui.view'].create({
                            'name': 'travel.reservation.form.facility',
                            'model': 'travel.reservation',
                            'inherit_id': parent_view.id,
                            'arch': view_arch,
                            'type': 'form',
                        })
    except Exception as e:
        # En cas d'erreur, on continue sans bloquer l'installation
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning('Erreur lors de la création des droits/vues pour travel.reservation.facility: %s', str(e))

