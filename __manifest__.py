# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Carta Porte CFDI 3.3',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'website': 'http://mikrointeracciones.com.mx',
    'summary': 'Carta porte cfdi',
    'description' : """
    """,
    'depends': [
        'base',
        'account',
        'stock',
        'l10n_mx_catalogs',
        'l10n_mx_facturae',
        'base_address_extended',
    ],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        "security/ir.model.access.csv",
        'views/res_partner_view.xml',
        'views/transport_catalogs_view.xml',
        'views/account_move_view.xml',
        'report/report_template_cfdi.xml',
        'views/fleet_view.xml',
    ],
    'active': False,
    'installable': True,
}
