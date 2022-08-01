# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.addons import decimal_precision as dp
import os
from openerp import tools
try:
    import xlrd
except ImportError:
    raise Warning("Warning",'Install xlrd in server-->sudo apt-get install python-xlrd ')
try:
    import xlwt
except ImportError:
    raise Warning("Warning",'Install xlrd in server')

import logging
_logger = logging.getLogger(__name__)


class TransportSat(models.Model):
    _name = 'transport.sat'
    _description = 'Transport Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for transport in self:
            name = transport.code + ' ' + transport.name
            result.append((transport.id, name))
        return result

    @api.model
    def import_transport_xlsx(self):
        transport_sat_obj = self.env['transport.sat']
        rows = transport_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_transport_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                transport_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Transport', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Transport')
    description = fields.Text(string='Description', translate=True,
        help='Description of the transport that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the transport that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class StationSat(models.Model):
    _name = 'station.sat'
    _description = 'Station Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for station in self:
            name = station.code + ' ' + station.name
            result.append((station.id, name))
        return result

    @api.model
    def import_station_xlsx(self):
        station_sat_obj = self.env['station.sat']
        rows = station_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_station_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'transport_code': sh.row(rx)[2].value,
                }
                station_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Station', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Station')
    transport_code = fields.Char(string='Transport Code')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Station that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Station that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class SeasonsSat(models.Model):
    _name = 'seasons.sat'
    _description = 'Seasons Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for seasons in self:
            name = seasons.code + ' ' + seasons.name
            result.append((seasons.id, name))
        return result

    @api.model
    def import_seasons_xlsx(self):
        seasons_sat_obj = self.env['seasons.sat']
        rows = seasons_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data', 'l10n_mx_seasons_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'transport_code': str(sh.row(rx)[0].value).replace(".0",""),
                    'code': str(sh.row(rx)[1].value).replace(".0",""),
                    'name': sh.row(rx)[2].value,
                    'nationalidad': sh.row(rx)[3].value,
                    'designador_iata': sh.row(rx)[4].value,
                    'railway_line': sh.row(rx)[5].value
                }
                seasons_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Seasons', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Seasons')
    transport_code = fields.Char(string='Transport Code')
    nationalidad = fields.Char(string='Nationalidad', help='Nationalidad for Seasons') 
    designador_iata = fields.Char(string='Designador IATA')
    railway_line = fields.Char(string='Railway line') 
    description = fields.Text(string='Description', translate=True,
        help='Description of the Seasons that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Seasons that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class UnitWeightSat(models.Model):
    _name = 'unit.weight.sat'
    _description = 'Unit Weigh Sat'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for weight in self:
            name = weight.code + ' ' + weight.name
            result.append((weight.id, name))
        return result

    @api.model
    def import_unit_weight_xlsx(self):
        unit_weight_sat_obj = self.env['unit.weight.sat']
        rows = unit_weight_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_unit_weight_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'description': sh.row(rx)[2].value,
                    'notes': sh.row(rx)[3].value,
                    'symbol': sh.row(rx)[6].value,
                    'flag': sh.row(rx)[7].value
                }
                unit_weight_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Unit Weigh', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Unit Weigh')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Unit Weight that will be shown in the invoices')
    symbol = fields.Char(string='Symbol')
    flag = fields.Char(string='Flag')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Unit Weight that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class MaterialDangerSat(models.Model):
    _name = 'material.danger.sat'
    _description = 'Material Danger Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for material in self:
            name = material.code + ' ' + material.name
            result.append((material.id, name))
        return result

    @api.model
    def import_material_danger_xlsx(self):
        material_danger_sat_obj = self.env['material.danger.sat']
        rows = material_danger_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_material_danger_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'class_division': sh.row(rx)[2].value,
                    'secondary_danger': sh.row(rx)[3].value,
                    'group_emb_env_onu': sh.row(rx)[4].value,
                    'disp_spec': sh.row(rx)[5].value,
                    'qty_limit_exc_01': sh.row(rx)[6].value,
                    'qty_limit_exc_02': sh.row(rx)[7].value,
                    'inst_emb_env': sh.row(rx)[8].value,
                    'disp_spec_emb_env': sh.row(rx)[9].value,
                    'inst_transp': sh.row(rx)[10].value,
                    'disp_spec_transp': sh.row(rx)[11].value,
                }
                material_danger_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Material Danger', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Material Danger')
    class_division = fields.Char(string='Clase o Division')
    secondary_danger = fields.Char(string='Peligro secundario')
    group_emb_env_onu = fields.Char(string='Grupo de emb/env ONU')
    disp_spec = fields.Char(string='Disp. espec.')
    qty_limit_exc_01 = fields.Char(string='Cantidades limitadas y exceptuadas 01')
    qty_limit_exc_02 = fields.Char(string='Cantidades limitadas y exceptuadas 02')
    inst_emb_env = fields.Char(string='Inst. de emb/env')
    disp_spec_emb_env = fields.Char(string='Disp. espec. de emb/env')
    inst_transp = fields.Char(string='Inst. de transp.')
    disp_spec_transp = fields.Char(string='Disp. espec. de transp.')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Material Danger that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Material Danger that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class PackagingTypeSat(models.Model):
    _name = 'packaging.type.sat'
    _description = 'Packaging Type Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for packaging in self:
            name = packaging.code + ' ' + packaging.name
            result.append((packaging.id, name))
        return result

    @api.model
    def import_packaging_type_xlsx(self):
        packaging_type_sat_obj = self.env['packaging.type.sat']
        rows = packaging_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_packaging_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                packaging_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Packaging Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Packaging Type')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Packaging Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Packaging Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class PermitStcSat(models.Model):
    _name = 'permit.stc.sat'
    _description = 'Permit STC Sat'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for permit in self:
            name = permit.code + ' ' + permit.name
            result.append((permit.id, name))
        return result

    @api.model
    def import_permit_stc_xlsx(self):
        permit_stc_sat_obj = self.env['permit.stc.sat']
        rows = permit_stc_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_permit_stc_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'transport_code': sh.row(rx)[2].value,
                }
                permit_stc_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Permit STC', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Permit STC')
    transport_code = fields.Char(string='Transport Code')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Permit STC that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Permit STC that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ConfigAutotransportSat(models.Model):
    _name = 'config.autotransport.sat'
    _description = 'Config Autotransport Sat'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for autotransport in self:
            name = autotransport.code + ' ' + autotransport.name
            result.append((autotransport.id, name))
        return result

    @api.model
    def import_config_autotransport_xlsx(self):
        config_autotransport_sat_obj = self.env['config.autotransport.sat']
        rows = config_autotransport_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_config_autotransport_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'axles_number': sh.row(rx)[2].value,
                    'tires_number': sh.row(rx)[3].value,
                }
                config_autotransport_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Config Autotransport', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Config Autotransport')
    axles_number = fields.Char(string='Numero de ejes')
    tires_number = fields.Char(string='Numero de llantas')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Config Autotransport that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Config Autotransport that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class TrailerTypeSat(models.Model):
    _name = 'trailer.type.sat'
    _description = 'Trailer Type Sat'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for trailer in self:
            name = trailer.code + ' ' + trailer.name
            result.append((trailer.id, name))
        return result

    @api.model
    def import_trailer_type_xlsx(self):
        trailer_type_sat_obj = self.env['trailer.type.sat']
        rows = trailer_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_trailer_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                trailer_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Trailer Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Trailer Type')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Trailer Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Trailer Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ConfigMaritimeSat(models.Model):
    _name = 'config.maritime.sat'
    _description = 'Config Maritime Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for maritime in self:
            name = maritime.code + ' ' + maritime.name
            result.append((maritime.id, name))
        return result

    @api.model
    def import_config_maritime_xlsx(self):
        config_maritime_sat_obj = self.env['config.maritime.sat']
        rows = config_maritime_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_config_maritime_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                config_maritime_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Config Maritime', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Config Maritime')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Config Maritime that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Config Maritime that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class LoadTypeSat(models.Model):
    _name = 'load.type.sat'
    _description = 'Load Type Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for load in self:
            name = load.code + ' ' + load.name
            result.append((load.id, name))
        return result

    @api.model
    def import_load_type_xlsx(self):
        load_type_sat_obj = self.env['load.type.sat']
        rows = load_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_load_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                load_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Load Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Load Type')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Load Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Load Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ContainerMaritimeSat(models.Model):
    _name = 'container.maritime.sat'
    _description = 'Container Maritime Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for maritime in self:
            name = maritime.code + ' ' + maritime.name
            result.append((maritime.id, name))
        return result

    @api.model
    def import_container_maritime_xlsx(self):
        container_maritime_sat_obj = self.env['container.maritime.sat']
        rows = container_maritime_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_container_maritime_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                container_maritime_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Container Maritime', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Container Maritime')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Container Maritime that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Container Maritime that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class PermitMaritimeSat(models.Model):
    _name = 'permit.maritime.sat'
    _description = 'Permit Maritime Sat'

    @api.model
    def import_permit_maritime_xlsx(self):
        permit_maritime_sat_obj = self.env['permit.maritime.sat']
        rows = permit_maritime_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_permit_maritime_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                }
                permit_maritime_sat_obj.create(lines_inv)
        return True

    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Permit Maritime')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Permit Maritime that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Permit Maritime that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class CodeAerotransportSat(models.Model):
    _name = 'code.aerotransport.sat'
    _description = 'Code Aerotransport Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for aerotransport in self:
            name = aerotransport.code + ' ' + aerotransport.name
            result.append((aerotransport.id, name))
        return result

    @api.model
    def import_code_aerotransport_xlsx(self):
        code_aerotransport_sat_obj = self.env['code.aerotransport.sat']
        rows = code_aerotransport_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_code_aerotransport_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'nationalidad': sh.row(rx)[1].value,
                    'name': sh.row(rx)[2].value,
                    'designador_oaci': sh.row(rx)[3].value,
                }
                code_aerotransport_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Code Aerotransport', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Code Aerotransport')
    nationalidad = fields.Char(string='Nationalidad', help='Nationalidad for Seasons') 
    designador_oaci = fields.Char(string='Designador OACI')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Code Aerotransport that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Code Aerotransport that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ProductStccSat(models.Model):
    _name = 'product.stcc.sat'
    _description = 'Product STCC Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for product_stcc in self:
            name = product_stcc.code + ' ' + product_stcc.name
            result.append((product_stcc.id, name))
        return result

    @api.model
    def import_product_stcc_xlsx(self):
        product_stcc_sat_obj = self.env['product.stcc.sat']
        rows = product_stcc_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_product_stcc_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                product_stcc_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Product STCC', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Product STCC')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Product STCC that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Product STCC that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ServiceTypeSat(models.Model):
    _name = 'service.type.sat'
    _description = 'Service Type Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for service in self:
            name = service.code + ' ' + service.name
            result.append((service.id, name))
        return result

    @api.model
    def import_service_type_xlsx(self):
        service_type_sat_obj = self.env['service.type.sat']
        rows = service_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_service_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                }
                service_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Service Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Service Type')
    description = fields.Text(string='Description', translate=True,
        help='Description of the Service Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Service Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class RightsWaySat(models.Model):
    _name = 'rights.way.sat'
    _description = 'Rights Way Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for way in self:
            name = way.code + ' ' + way.name
            result.append((way.id, name))
        return result

    @api.model
    def import_rights_way_xlsx(self):
        rights_way_sat_obj = self.env['rights.way.sat']
        rows = rights_way_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_rights_way_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'among': sh.row(rx)[2].value,
                    'until': sh.row(rx)[3].value,
                    'give_receive': sh.row(rx)[4].value,
                    'concessionaire': sh.row(rx)[5].value,
                }
                rights_way_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Rights Way', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Rights Way')
    among = fields.Char(string='Entre', translate=True)
    until = fields.Char(string='Hasta', translate=True)
    give_receive = fields.Char(string='Otorga/Recibe', translate=True)
    concessionaire = fields.Char(string='Concesionario', translate=True)
    description = fields.Text(string='Description', translate=True,
        help='Description of the Rights Way that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Rights Way that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class CarTypeSat(models.Model):
    _name = 'car.type.sat'
    _description = 'Car Type Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for car in self:
            name = car.code + ' ' + car.name
            result.append((car.id, name))
        return result

    @api.model
    def import_car_type_xlsx(self):
        car_type_sat_obj = self.env['car.type.sat']
        rows = car_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_car_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'description': sh.row(rx)[2].value,
                }
                car_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Car Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Car Type')  
    description = fields.Text(string='Description', translate=True,
        help='Description of the Car Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Car Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)


class ContainerTypeSat(models.Model):
    _name = 'container.type.sat'
    _description = 'Container Type Sat'

    #@api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for container in self:
            name = container.code + ' ' + container.name
            result.append((container.id, name))
        return result

    @api.model
    def import_container_type_xlsx(self):
        container_type_sat_obj = self.env['container.type.sat']
        rows = container_type_sat_obj.search_count([])
        if rows <= 0:
            FILE = False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data')
                ):
                    FILE = my_path and os.path.join(my_path, 'l10n_mx_transport_cfdi', 'data','l10n_mx_container_type_sat_data.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_id = False
            for rx in range(sh.nrows):
                lines_inv = {
                    'code': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'description': sh.row(rx)[2].value,
                }
                container_type_sat_obj.create(lines_inv)
        return True

    name = fields.Char(string='Name', required=True,
        help='Container Type', translate=True)
    code = fields.Char(string='Code', size=64, required=True,
        help='Specify the Code for Container Type')  
    description = fields.Text(string='Description', translate=True,
        help='Description of the Container Type that will be shown in the invoices')
    notes = fields.Text(string='Notes', translate=True,
        help='Notes of the Container Type that will be shown in the invoices')
    active = fields.Boolean('Active', default=True)

