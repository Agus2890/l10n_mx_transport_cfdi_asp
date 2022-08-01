# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
import time
class fleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    remolque=fields.Boolean(string="Remolque  ?")
    cartapporte=fields.Boolean(string="En Carta Porte  ?")
    config_autotransport_id = fields.Many2one('config.autotransport.sat', string='Conf. Auto Transporte Federal', copy=False)
    trailer_type_id = fields.Many2one('trailer.type.sat', string='Tipo Remolque', copy=False)

    insurance_partner_id = fields.Many2one('res.partner', string='Compañía de seguros', copy=False)
    insurance_policy = fields.Char(string='Poliza se Seguro', copy=False)

    permit_stc_id = fields.Many2one('permit.stc.sat', string='Permiso STC', copy=False)
    permit_stc_number = fields.Char(string='Num. Permiso STC', copy=False)