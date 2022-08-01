# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
import os
from openerp import tools, netsvc

import logging
_logger = logging.getLogger(__name__)


# class AccountTransport(models.Model):
#     _name = 'account.transport'
#     _description = "Letter Porte"
#     _order = 'date_transport desc, id desc'

#     def _default_uom(self):
#         weight_uom_id = self.env.ref('product.product_uom_kgm', raise_if_not_found=False)
#         if not weight_uom_id:
#             uom_categ_id = self.env.ref('product.product_uom_categ_kgm').id
#             weight_uom_id = self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)
#         return weight_uom_id

#     name = fields.Char(string='N° Letter Porte', required=True, copy=False,
#         readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True)
#     date_transport = fields.Datetime(string='Letter Porte Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
#     date_confirm = fields.Date('Confirmation Date', readonly=True, select=True, help="Date on which sales order is confirmed.", copy=False)
#     user_id = fields.Many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange')
#     partner_id = fields.Many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always')
#     partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.")
#     journal_id = fields.Many2one('account.journal', string='Diario', required=True, domain=[('type', 'in', ('transport'))])    

#     transport_inter = fields.Selection([('0','No'),('1', 'Si')], string='Transport Internacional', index=True, readonly=True, default='0',
#         copy=False)
#     type_transport = fields.Many2one('transport.sat', string='Type Transport')
#     type_shipping = fields.Selection([('in','Entrada'),('out', 'Salida')], string='Tipo de envio', index=True, readonly=True, default='out',
#         copy=False)
#     carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False)
#     weight = fields.Float(string='Weight net')
#     weight_uom_id = fields.Many2one('product.uom', string='Unit of Measure', required=True, readonly="1", help="Unit of measurement for Weight", default=_default_uom)


#     lines_ids = fields.One2many('account.transport.line', 'transport_id', 'Transport Lines',
#         readonly=True, states={'draft': [('readonly', False)]}, copy=True)
#     rfcprovcertif = fields.Char('RfcProvCertif', size=64, copy=False)
#     no_certificado = fields.Char('No. Certificate', size=64, copy=False, 
#         help='Number of serie of certificate used for the invoice')
#     certificado = fields.Text('Certificate', size=64, copy=False, help='Certificate used in the invoice')
#     sello = fields.Text('Stamp', size=512, copy=False, help='Digital Stamp')#
#     cadena_original = fields.Text('String Original', size=512, copy=False, 
#         help='Data stream with the information contained in the electronic invoice')
#     cfdi_xml=fields.Binary('XML TIMBRADO')
#     cfdi_fecha_timbrado = fields.Datetime('CFD-I Date Stamping', copy=False,
#         help='Date when is stamped the electronic invoice')
#     cfdi_fecha_cancel = fields.Datetime('CFD-I Date Cancel', copy=False)
#     cfdi_folio_fiscal = fields.Char('CFD-I Folio Fiscal', size=64, copy=False,
#         help='Folio used in the electronic invoice')
#     cfdi_sello = fields.Text('CFD-I Stamp', copy=False, help='Sign assigned by the SAT')
#     cfdi_cadena_original = fields.Text('CFD-I Original String', copy=False,
#         help='Original String used in the electronic invoice')
#     cfdi_no_certificado=fields.Char('CFD-I Certificado', size=32,
#         help='Serial Number of the Certificate')
#     date_transport_tz=fields.Datetime(string='Date Invoiced with TZ')

#     state = fields.Selection([
#             ('draft','Draft'),
#             ('open','Open'),
#             ('done', 'Done'),
#             ('cancel','Cancelled'),
#         ], string='Status', index=True, readonly=True, default='draft',
#         track_visibility='onchange', copy=False,
#         help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
#              " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
#              " * The 'Cancelled' status is used when user cancel invoice.")

#     @api.model
#     def create(self, vals):
#         if vals.get('name', '/') == '/':
#             vals['name'] = self.env['ir.sequence'].get('account.transport')
#         return super(AccountTransport, self).create(vals)


class AccountTransportLine(models.Model):
    _name = 'account.transport.line'
    _description = 'Account Transport Line'

    @api.onchange('product_id')
    def on_change_product_id(self):
        if self.product_id:
            self.product_code_sat_id=self.product_id.product_tmpl_id.code_product_sat and self.product_id.product_tmpl_id.code_product_sat.id or \
                self.product_id.code_product_sat.id
            self.product_uom_sat_id=self.product_id.product_tmpl_id.product_unit_sat and self.product_id.product_tmpl_id.product_unit_sat.id or \
                self.product_id.product_unit_sat.id
            self.weight_kg=self.product_id.weight


    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    sale_line_id = fields.Many2one("sale.order.line", string="Sale line")
    picking_line_id = fields.Many2one("stock.move", string="Picking line")
    invoice_line_id = fields.Many2one("account.invoice.line", string="Invoice line")
    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Name")
    product_code_sat_id = fields.Many2one("key.product.sat", string="Product Code SAT")
    product_uom_sat_id = fields.Many2one("key.unit.sat", string="Product Unit SAT")
    uom_id = fields.Many2one("product.uom", string="Unit of Measure")
    quantity = fields.Float(string="Quantity", digits= dp.get_precision('Product Unit of Measure'))
    price_subtotal = fields.Float(string='Valor Mercancia', digits= dp.get_precision('Account'))
    product_stcc_id = fields.Many2one("product.stcc.sat", string="Clave STCC")
    weight_kg = fields.Float(string='Weight Kg', digits_compute=dp.get_precision('Stock Weight'))
    unit_weight_id = fields.Many2one("unit.weight.sat", string="Clave Unidad")
    material_danger_id = fields.Many2one("material.danger.sat", string="Material peligroso")


