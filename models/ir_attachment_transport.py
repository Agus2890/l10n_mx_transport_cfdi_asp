# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp import tools
from openerp import netsvc
from jinja2 import Environment, FileSystemLoader
import time
import tempfile
import base64
import codecs
from unidecode import unidecode
import os
from openerp import SUPERUSER_ID
from openerp.exceptions import except_orm, Warning, RedirectWarning
from xml.dom.minidom import parse
import logging
_logger = logging.getLogger(__name__)

from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

class IrAttachmentTransport(models.Model):
    _name = 'ir.attachment.transport'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Attachment Transport"

    #@api.model
    def _get_type(self):
        return []

    def get_driver_fc_sign(self):
        return {}

    def get_driver_fc_cancel(self):
        return {}

    name=fields.Char(string='Name', size=128, required=True, readonly=True)
    uuid=fields.Char(string='UUID', size=128, readonly=True)
    invoice_id=fields.Many2one('account.invoice', 'Factura', readonly=True)
    # invoice_ids=fields.Many2many('account.invoice', string="Facturas", readonly=True)
    # voucher_id=fields.Many2one('account.voucher', 'Voucher', readonly=True)
    # payment_ids=fields.Many2many('account.move.line',string="Lineas de Pago",readonly=True)
    company_id=fields.Many2one('res.company', string='Company', readonly=True)
    file_input=fields.Many2one('ir.attachment', 'File input',
            readonly=True, help='File input')
    type=fields.Selection('_get_type',string='Type')
    state=fields.Selection([
             ('draft', 'Draft'),
             ('confirmed', 'Confirmed'),
             ('signed', 'Signed'),
             ('printable', 'Printable Format Generated'),
             ('sent_customer', 'Sent Customer'),
             ('done', 'Done'),
             ('cancel', 'Cancelled'), ],
             'State', readonly=True, required=True,default="draft", help='State of attachments')
    file_xml_sign=fields.Many2one('ir.attachment', 'File XML Sign',
            readonly=True, help='File XML signed')
    file_pdf=fields.Many2one('ir.attachment', 'File PDF', readonly=True,
            help='Report PDF generated for the electronic Invoice')
    last_date=fields.Datetime(
            'Last Modified', readonly=True)
    description=fields.Text(string='Description')
    msj=fields.Text('Last Message', readonly=True,
            track_visibility='onchange',
            help='Message generated to upload XML to sign')

    # def action_confirm(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     invoice_obj = self.pool.get('account.invoice')
    #     msj = ''
    #     index_xml = ''
    #     attach = self.browse(cr, uid, ids[0])
    #     invoice = attach.invoice_id
    #     type = attach.type
    #     save_attach = None
    #     if 'cfdi' in type:
    #         fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
    #             '_V3_2.xml' or ''
    #         fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
    #             cr, uid, [invoice.id], context=context)
    #         attach = self.pool.get('ir.attachment').create(cr, uid, {
    #             'name': fname_invoice,
    #             'datas': base64.encodestring(xml_data),
    #             'datas_fname': fname_invoice,
    #             'res_model': 'account.invoice',
    #             'res_id': invoice.id,
    #         }, context=None)
    #         msj = _("Attached Successfully XML CFDI 3.2\n")
    #         save_attach = True
    #     else:
    #         raise orm.except_orm(
    #             _("Type Electronic Invoice Unknow!"),
    #             _("The Type Electronic Invoice:" + (type or ''))
    #         )
    #     if save_attach:
    #         self.write(
    #             cr, uid, ids,
    #             {'file_input': attach or False,
    #              'state': 'confirmed',
    #              'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
    #              'msj': msj,
    #              'file_xml_sign_index': index_xml},
    #             context=context
    #         )
    #     return True

    @api.multi
    def get_dr_amount_currency(self):
        for pay in self:
            if pay.voucher_id.payment_rate_currency_id != self.company_id.currency_id.id:
                for line in pay.payment_ids:
                    line.dr_amount_currency = pay.voucher_id.payment_rate * line.amount_payment

    def _get_certificate_str(self, fname_cer_pem=""):
        """
        @param fname_cer_pem : Path and name the file .pem
        """
        fcer = open(fname_cer_pem, "r")
        lines = fcer.readlines()
        fcer.close()
        cer_str = ""
        loading = False
        for line in lines:
            if 'END CERTIFICATE' in line:
                loading = False
            if loading:
                cer_str += line
            if 'BEGIN CERTIFICATE' in line:
                loading = True
        return cer_str

    def _get_sello(self):
        context = self.env.context.copy()
        certificate_lib = self.env['facturae.certificate.library']
        fname_sign = certificate_lib.b64str_to_tempfile(base64.encodestring(
            ''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + \
            '__sign__')
        result = certificate_lib.with_context(context)._sign(fname=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_key=context['fname_key'],
            fname_out=fname_sign, encrypt="sha1", type_key='PEM',context=context)
        return result

    def _xml2cad_orig(self):
        context = self.env.context.copy()
        certificate_lib = self.env['facturae.certificate.library']
        fname_tmp = certificate_lib.b64str_to_tempfile(base64.encodestring(
            ''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + \
            '__cadorig__')
        cad_orig = certificate_lib._transform_xml(fname_xml=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_out=fname_tmp)
        return fname_tmp, cad_orig

    def _get_noCertificado(self, fname_cer, pem=True):
        certificate_lib = self.env['facturae.certificate.library']
        fname_serial = certificate_lib.b64str_to_tempfile(base64.encodestring(
            ''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + \
            '__serial__')
        result = certificate_lib._get_param_serial(
            fname_cer, fname_out=fname_serial, type='PEM')
        return result

    def binary2file(self,binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

    def _get_file_globals(self):
        context = self.env.context.copy()
        file_globals = {}
        if self:
            #payslip = self.browse(cr, uid, id, context=context)
            tz = pytz.timezone('America/Mexico_City')
            time_now=datetime.now(tz).strftime('%H:%M:%S')
            #time_now=datetime.now().strftime('%H:%M:%S')
            # Create a template and pass a context
            date_voucher = datetime.strptime(
                    self.voucher_id.payment_datetime,'%Y-%m-%d %H:%M:%S'
                ).strftime('%Y-%m-%dT%H:%M:%S')
            ###########################
            context.update({'date_work':datetime.strptime(
                self.voucher_id.payment_datetime,'%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%dT%H:%M:%S')})
            file_globals.update({'date_stamped':datetime.strptime(
                self.voucher_id.payment_datetime,'%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%dT%H:%M:%S'),'datetime':date_voucher})
            certificate_id = self.company_id.with_context(
                context)._get_current_certificate(
                [self.company_id.id])[self.company_id.id]
            certificate_id = certificate_id and self.env[
                'res.company.facturae.certificate'].browse(
                    [certificate_id])

            if certificate_id:
                if not certificate_id.certificate_file_pem:
                    pass
                fname_cer_pem = False
                try:
                    fname_cer_pem = self.binary2file(
                        certificate_id.certificate_file_pem, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer.pem')
                except:
                    raise Warning(
                        _('Error !'),
                        _('Not captured a CERTIFICATE file in format PEM, in '
                           'the company!')
                    )
                file_globals['fname_cer'] = fname_cer_pem

                fname_key_pem = False
                try:
                    fname_key_pem = self.binary2file(
                        certificate_id.certificate_key_file_pem, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key.pem')
                except:
                    raise Warning(
                        _('Error !'),
                        _('Not captured a KEY file in format PEM, in the company!')
                    )
                file_globals['fname_key'] = fname_key_pem

                fname_cer_no_pem = False
                try:
                    fname_cer_no_pem = self.binary2file(
                        certificate_id.certificate_file, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer')
                except:
                    pass
                file_globals['fname_cer_no_pem'] = fname_cer_no_pem
                fname_key_no_pem = False
                try:
                    fname_key_no_pem = self.binary2file(
                        certificate_id.certificate_key_file, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key')
                except:
                    pass
                file_globals['fname_key_no_pem'] = fname_key_no_pem

                file_globals['password'] = certificate_id.certificate_password

                if certificate_id.fname_xslt:
                    if (certificate_id.fname_xslt[0] == os.sep or \
                        certificate_id.fname_xslt[1] == ':'):
                        file_globals['fname_xslt'] = certificate_id.fname_xslt
                    else:
                        file_globals['fname_xslt'] = os.path.join(
                            tools.config["root_path"], certificate_id.fname_xslt)
                else:
                    all_paths = tools.config["addons_path"].split(",")
                    for my_path in all_paths:
                        if os.path.isdir(os.path.join(my_path,
                            'l10n_mx_facturae', 'SAT')):
                            file_globals['fname_xslt'] = my_path and os.path.join(
                                my_path, 'l10n_mx_facturae', 'SAT',
                                'cadenaoriginal_2_0_l.xslt') or ''
                            break
                if not file_globals.get('fname_xslt', False):
                    raise Warning(
                        _('Warning !'),
                        _('Not defined fname_xslt. !')
                    )

                if not os.path.isfile(file_globals.get('fname_xslt', ' ')):
                    raise Warning(
                        _('Warning !'),
                        _('No exist file [%s]. !') % (file_globals.get('fname_xslt', ' '))
                    )

                file_globals['serial_number'] = certificate_id.serial_number
            else:
                raise Warning(
                    _('Warning !'),
                    _('Check date of invoice and the validity of certificate'
                      ', & that the register of the certificate is active.')
                )

        voucher_datetime = self.voucher_id.payment_datetime
        #payslip = self.browse(cr, uid, ids, context=context)
        pac_type=True
        #type_inv = payslip.journal_id.type_cfdi or 'cfd22'
        if voucher_datetime < '2012-07-01':
            return file_globals
        elif pac_type:
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_facturae', 'SAT')
                ):
                    file_globals['fname_xslt'] = my_path and os.path.join(
                        my_path, 'l10n_mx_facturae', 'SAT',
                        'cadenaoriginal_3_3',
                        'cadenaoriginal_3_3.xslt') or ''
        return file_globals

    @api.multi
    def _get_signed_xml(self,xmldata):
        context = self.env.context.copy()
        fname = (self.company_id.partner_id.vat_split+'_P'+'.xml')
        file_globals=self._get_file_globals()
        #################################
        fname_cer_no_pem = file_globals['fname_cer']
        cerCSD = fname_cer_no_pem and base64.encodestring(
             open(fname_cer_no_pem, "r").read()) or ''
        fname_key_no_pem = file_globals['fname_key']
        keyCSD = fname_key_no_pem and base64.encodestring(
             open(fname_key_no_pem, "r").read()) or ''

        context.update(file_globals)
        comprobante = xmldata.getElementsByTagName("cfdi:Comprobante")[0]
        noCertificado = self._get_noCertificado(context['fname_cer'])
        comprobante.setAttribute("NoCertificado", noCertificado)

        pagos10= xmldata.getElementsByTagName('pago10:Pago')
        docrelacionado= xmldata.getElementsByTagName('pago10:DoctoRelacionado')

        for attr in pagos10:
            if not self.voucher_id.journal_id.currency:
               attr.removeAttribute('TipoCambioP')
            if not self.voucher_id.partner_bank_id.bank_bic:
                attr.removeAttribute('RfcEmisorCtaOrd')
            elif self.voucher_id.payment_type_id and self.voucher_id.payment_type_id.code not in\
            ['03','04']:
                attr.removeAttribute('RfcEmisorCtaOrd')
                payment_type=self.voucher_id.payment_type_id.code
                #raise Warning(" si paso ",str( payment_type ))
            #raise Warning(" no paso ",str( payment_type ))
            elif attr.removeAttribute('RfcEmisorCtaOrd') == 'XEXX010101000':
                attrDR.setAttribute('NomBancoOrdExt', self.voucher_id.partner_bank_id.bank_name)
        #    attr.removeAttribute('CtaOrdenante')
        #    attr.removeAttribute('RfcEmisorCtaBen')
        #    attr.removeAttribute('CtaBeneficiario')
        #    attr.removeAttribute('RfcEmisorCtaOrd')
        #    attr.removeAttribute('NomBancoOrdExt')

        for attrDR in docrelacionado:
            if self.invoice_id:
                if self.invoice_id.currency_id.name == attr.attributes['MonedaP'].value or self.invoice_id.company_id.currency_id.id == self.voucher_id.journal_id.currency.id:                    
                    attrDR.removeAttribute('TipoCambioDR')

            if not self.invoice_id:
                if attr.attributes['MonedaP'].value == attrDR.getAttribute('MonedaDR') and attrDR.getAttribute('TipoCambioDR'):
                    attrDR.removeAttribute('TipoCambioDR')

            # if attr.attributes['MonedaP'].value != attrDR.getAttribute('MonedaDR') and attr.attributes['MonedaP'].value == 'MXN':
            #     tipoCambioDR = float(attrDR.getAttribute('TipoCambioDR'))
            #     rate = round((1/tipoCambioDR),6)#se agrego / 
            #     impPagado = float(attrDR.getAttribute('ImpPagado'))
            #     impPagadoUSD = round((impPagado*tipoCambioDR),2)
            #     # raise Warning(_("impPagadoUSD %s")%(impPagadoUSD))
            #     impSaldoAnt = float(attrDR.getAttribute('ImpSaldoAnt'))
            #     impSaldoAntUSD = round((impSaldoAnt*tipoCambioDR),2)
            #     impSaldoInsolutoUSD = impSaldoAntUSD-impPagadoUSD
            #     attrDR.setAttribute('ImpSaldoInsoluto', str(impSaldoInsolutoUSD))
            #     attrDR.setAttribute('ImpPagado', str(impPagadoUSD))
            #     attrDR.setAttribute('ImpSaldoAnt', str(impSaldoAntUSD))
            #     attrDR.setAttribute('TipoCambioDR', str(rate))

            # #Se comenta el if anterior para reducir decimales aun falta validar el residuo en caso de ser un pago de multiples facturas
            if attr.attributes['MonedaP'].value != attrDR.getAttribute('MonedaDR') and attr.attributes['MonedaP'].value == 'MXN':
                tipoCambioDR = float(attrDR.getAttribute('TipoCambioDR'))
                rateDR = round((1/tipoCambioDR),4)# dedondeo de 6 a 4
                impPagado = float(attrDR.getAttribute('ImpPagado'))# se omite amount_payment y se toma dr_amount_currency tomando el atributo ImpPagado="{{item.dr_amount_currency}}"
                impPagado = round((1 / self.voucher_id.payment_rate * impPagado),2)
                drImpPagadoUSD = float(attrDR.getAttribute('ImpPagado'))
                impSaldoAnt = float(attrDR.getAttribute('ImpSaldoAnt'))# hay que validar como tomar para el atributo para multiples facturas --> ImpSaldoAnt="{{item.invoice_id.residual+item.amount_payment}}"
                impSaldoAntUSD = drImpPagadoUSD
                impSaldoInsolutoUSD = impSaldoAntUSD-drImpPagadoUSD
                rateP = round((self.voucher_id.payment_rate),6)
                attrDR.setAttribute('ImpSaldoInsoluto', str(impSaldoInsolutoUSD)) 
                attrDR.setAttribute('ImpPagado', str(drImpPagadoUSD))
                attrDR.setAttribute('ImpSaldoAnt', str(impSaldoAntUSD))
                attrDR.setAttribute('TipoCambioDR', str(rateP))# ya esta en el template

        for attr in docrelacionado:
            se=attr.attributes['Serie'].value
            if se=='False':
                attr.removeAttribute('Serie')
        #################################
        pagos_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
        '.xml', 'openerp_' + (pagos_number or '') + '__pagos_v1__')
        fname_txt = fname_xml + '.txt'
        with open(fname_xml,'w') as f:
            f.write(xmldata.toxml("utf-8"))
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + (
            pagos_number or '') + '__nomina_txt_md5__')
        os.close(fileno_sign)
        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })
        fname_txt, txt_str = self.with_context(context)._xml2cad_orig()
        context.update({'cadena_original':txt_str})
        if not txt_str:
            raise Warning(
                _('Error en Cadena original!'),
                _("Can't get the string original of the voucher.\n"
                  "Ckeck your configuration.")
            )
        sign_str = self.with_context(context)._get_sello()
        ##certificado
        cert_str = self._get_certificate_str(context['fname_cer'])
        cert_str = cert_str.replace(' ', '').replace('\n', '')

        nodeComprobante = xmldata.getElementsByTagName("cfdi:Comprobante")[0]
        nodeComprobante.setAttribute("Sello", sign_str)
        nodeComprobante.setAttribute("Certificado", cert_str)
        data = {
            'no_certificado': noCertificado,
            'certificado': cert_str,
            'sello': sign_str,
            'cadena_original': txt_str,
            'date_payment_tz':file_globals['datetime']
        }
        self.voucher_id.write(data)

        xmldata = xmldata.toxml('UTF-8')
        return xmldata

    @api.multi
    def _get_cfdi_dict_data(self):
        move_lines = []
        for line in self.payment_ids:
            if line.credit:
                move_lines.append(line)
        #raise Warning("",str( move_lines ))
        # Crate an environment of jinja in the templates directory
        env = Environment(loader=FileSystemLoader(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../templates'
            )
        ))
        emitter = (self.company_id)
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        payment_datetime_convert = fields.Datetime.to_string(fields.Datetime.context_timestamp(self,
            fields.Datetime.from_string(self.voucher_id.payment_datetime)))[:25]
        time_now=datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        # date_voucher=datetime.strptime(time_now,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        date_voucher = datetime.strptime(
                self.voucher_id.date,'%Y-%m-%d'
            ).strftime('%Y-%m-%dT'+'12:00:00')
        # date_payment=datetime.strptime(self.voucher_id.payment_datetime,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        date_stamped = datetime.strptime(
            payment_datetime_convert,'%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%dT%H:%M:%S')
        #self.voucher_id.payment_datetime+'T'+'00:00:00'

        template = env.get_template('payment.xml')
        rate=self.voucher_id._get_currency_rate_mp()
        if not self.voucher_id.payment_type_id.code:
            raise Warning("Warning","Favor de Revisar que  el metodo de \
                Pago %s este bien configurado"%self.voucher_id.payment_type_id.name)
        xml_data = template.render(
            voucher=self.voucher_id,rate=rate,payment_ids=move_lines,
            emitter=emitter,date_stamped=date_stamped,date_voucher=date_voucher,pagos=move_lines
            )
        new_file = tempfile.NamedTemporaryFile(delete=False)
        with codecs.open(new_file.name, 'w', encoding='utf-8') as f:
           #raise Warning("",str(xml_data.encode('ascii', 'ignore').decode('ascii').replace('&', '&amp;')   ))
           unicode = unidecode(xml_data.encode('ascii', 'ignore').decode('ascii').replace('&', '&amp;') )
       	   f.write(unicode)
        xml = parse(new_file.name)
        xmldata=self._get_signed_xml(xml)
        #file_globals=self._get_file_globals()
        #file_globals=self._get_file_globals()
        return xmldata

    @api.multi        
    def action_sign_payment(self):
        # folios=self.company_id.check_folios_active()
        # if folios<=0:
        #     raise Warning("Aviso",str( "Timbres insuficietes numero de folios  es de %s" )%(folios))
        attach = ''
        index_xml = ''
        msj = ''
        attachment_obj = self.env['ir.attachment']
        voucher = self.voucher_id
        type = self.type
        if self.voucher_id:
            complemento = sum(x.amount_payment for x in self.voucher_id.line_cr_ids) 
            # if complemento != self.voucher_id.amount: 
            #     raise Warning(_("Favor de verificar la sumatoria del complemento %s,\n ya que no corresponde al monto a pagar %s")%(complemento,self.voucher_id.amount))
        if type:
            type__fc = self.get_driver_fc_sign()
            if type in type__fc.keys():
                # fname_payment = 'P'+self.company_id.partner_id.vat_split+'_'+str(self.voucher_id.cfdi_folio_fiscal)+'.xml'
                fname_payment = voucher.company_id.partner_id.vat_split + '_' + self.name + '.xml' 
                xml_data = self._get_cfdi_dict_data()
                fdata = base64.encodestring(xml_data)
                #raise Warning("",str(type__fc[type]()))
                res = type__fc[type](fdata)
                msj = tools.ustr(res.get('msg', False))
                index_xml = res.get('cfdi_xml', False)
                xml_file = res.get('cfdi_xml', False).encode('UTF-8')
                xml_file = ('%s')%(res.get('cfdi_xml', False))
                data_attach = {
                    'name': fname_payment,
                    'datas': base64.encodestring(xml_file),
                    'datas_fname': fname_payment,
                    'description': 'Factura-E XML CFD-I SIGN',
                    'res_model': 'account.voucher',
                    'res_id':self.voucher_id.id,
                }
                # Write cfdi in models
                voucher.move_id.sudo().write({'cfdi_folio_fiscal': self.voucher_id.cfdi_folio_fiscal})
                for line in voucher.move_id.line_id:
                    if not line.cfdi_folio_fiscal:
                        line.sudo().write({'cfdi_folio_fiscal': self.voucher_id.cfdi_folio_fiscal})
                self.write({'uuid': self.voucher_id.cfdi_folio_fiscal})
                # Context, because use a variable type of our code but we
                # dont need it.                
                attach = attachment_obj.create(data_attach)
            else:
                raise Warning(
                    _('Error'),
                    _("Unknow driver for %s" % attach.type)
                )
        vals={'file_xml_sign': attach.id or False,
            'state': 'signed',
            'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'msj': msj
            }
        _logger.info("write==============================: %s " % (vals))
        self.write(vals)
        # TODO: Remove the need to commit database if not exception
        self.action_printable()
        #self.action_send_customer(cr, uid, ids, context=context)
        #cr.commit()
        self.env.cr.commit()
        return True

    def signal_printable(self, cr, uid, ids, context=None):
        """
        If attachment workflow hangs we need to send a signal to continue
        """
        return self.action_printable(cr, uid, ids, context)

    def action_printable(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        aids = ''
        msj = ''
        index_pdf = ''
        attachment_obj = self.pool.get('ir.attachment')
        voucher = self.browse(cr, uid, ids)[0].voucher_id
        voucher_obj = self.pool.get('account.voucher')
        (fileno, fname) = tempfile.mkstemp(
            '.pdf', 'openerp_' + str(voucher.id or '') + '__facturae__'
        )
        os.close(fileno)
        voucher_obj.create_report(
            cr, uid, [voucher.id],
            'account.voucher.webkit', fname
        )
        attachment_ids = attachment_obj.search(cr, uid, [
           ('res_model', '=', 'account.voucher'),
           ('res_id', '=', voucher.id),
           ('datas_fname', '=','PAGO_'+(voucher.company_id.partner_id.vat_split) + '.pdf.pdf')]
        )
        for attach in self.browse(cr, uid, attachment_ids, context=context):
           aids = attach.id
           attachment_obj.write(
               cr, uid, [attach.id],
               # {'name': 'PAGO_'+voucher.company_id.partner_id.vat_split+'.pdf'},
               {'name': voucher.company_id.partner_id.vat_split + '_' + voucher.number + '.pdf'},
               context=context
           )
        if aids:
          msj = _("Attached Successfully PDF\n")
        else:
           # raise Warning(
           #     _('Warning'),str(attachment_ids)
           # )
           raise Warning(
               _('"Warning","Not Attached PDF\n"')
           )
        self.write(
            cr, uid, ids,
            {'file_pdf': aids or False,
             'state': 'printable',
             'msj': msj,
             'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
             'file_pdf_index': index_pdf},
            context=context
        )
        # TODO: Remove the need to commit database if not exception
        cr.commit()
        return True

    def signal_send_customer(self, cr, uid, ids, context=None):
        """
        If attachment workflow hangs we need to send a signal to continue
        """
        return self.action_send_customer(cr, uid, ids, context)

    def action_send_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attachments = []
        sent = ''
        sent_to = ''
        # Grab voucher
        voucher = self.browse(cr, uid, ids)[0].voucher_id

        # Grab attachments
        adjuntos = self.pool.get('ir.attachment').search(
            cr, uid,
            [('res_model', '=', 'account.voucher'),
             ('res_id', '=', voucher.id)]
        )
        for attach in self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
            attachments.append(attach.id)

        # Send mail
        obj_ir_mail_server = self.pool.get('ir.mail_server')
        mail_server_id = obj_ir_mail_server.search(
            cr, uid, [('name', '=', 'FacturaE')], context=None
        )
        if mail_server_id:
            _logger.debug('Testing SMTP servers')
            for smtp_server in obj_ir_mail_server.browse(
                cr, uid, mail_server_id, context=context
            ):
                try:
                    #raise orm.except_orm("",str( smtp_server.smtp_user ))
                    obj_ir_mail_server.connect(
                        smtp_server.smtp_host, smtp_server.smtp_port,
                        user=smtp_server.smtp_user,
                        password=smtp_server.smtp_pass,
                        encryption=smtp_server.smtp_encryption,
                        smtp_debug=smtp_server.smtp_debug)
                except Exception, e:
                    raise orm.except_orm(
                        _("Connection test failed!"),
                        _("Configure outgoing mail server named FacturaE: %s")
                        % tools.ustr(e)
                    )

            # Server tested, create mail content
            _logger.debug('Start processing mail template')
            template_pool = self.pool.get('email.template')
            template_id = self.get_tmpl_email_id(cr, uid, ids, context=context)
            values = template_pool.generate_email(
                cr, uid, template_id, voucher.id, context=context
            )
            assert values.get('email_from'), 'email_from is missing or empty after template rendering, send_mail() cannot proceed'
            # Get recipients
            recipients = values['partner_ids']
            #raise orm.except_orm("Email de envío", str(voucher.partner_id.email))
            # Create mail
            mail_mail = self.pool.get('mail.mail')
            msg_id = mail_mail.create(cr, uid, values, context=context)
            # Process attachments
            mail_mail.write(
                cr, uid, msg_id,
                {'attachment_ids': [(6, 0, attachments)],
                 'recipient_ids': [(6, 0, recipients)]},
                context=context
            )
            # Send mail
            mail_mail.send(
                cr, uid, [msg_id],
                context=context
            )
            #template_pool.send_mail(cr,uid,template_id,voucher.id,force_send=True,context=context)
            # Check mail
            if voucher.partner_id.email:
                sent = _("Sent Successfully\n")
                sent_to = voucher.partner_id.email
            else:
                raise orm.except_orm(
                    _('Warning'),
                    _('Your customer does not have email.'
                        '\nConfigure the mail of your "Customer"')
                )    
        else:
            raise orm.except_orm(
                _('Warning'),
                _('Not Found outgoing mail server name of "FacturaE".'
                  '\nConfigure the outgoing mail server named "FacturaE"')
            )
        self.write(cr, uid, ids, {'state': 'done', 'sent': sent, 'sent_to': sent_to}, context=context)
        # TODO: Remove the need to commit database if not exception
        cr.commit()
        return True

    @api.multi 
    def signal_cancel_payment(self):
        #raise Warning("hola",str(self))
        attachment_obj = self.env['ir.attachment']
        for attach in self:#.browse(cr, uid, ids, context=context):
            if attach.type:
                # raise Warning("signal_cancel_payment self.type",str(self.type))
                if attach.state not in ['cancel', 'draft', 'confirmed']:
                    type_fc = self.get_driver_fc_cancel()
                    # raise Warning("signal_cancel_payment type_fc",str(type_fc))#si entra
                    if attach.type in type_fc.keys():
                        # raise Warning("signal_cancel_payment cfdi_cancel",str(type_fc.keys()))#si entra
                        cfdi_cancel = type_fc[attach.type]()#([attach.id])
                        # raise Warning("signal_cancel_payment cfdi_cancel",str(cfdi_cancel))
                        if cfdi_cancel['status']:
                            # # Regenerate PDF file for include CANCEL legend
                            fname = attach.voucher_id.company_id.partner_id.vat_split + '_' + attach.voucher_id.number
                            # result = self._get_voucher_report()
                            # raise Warning("Valors",str(result))
                            attach_ids = attachment_obj.search(
                                [('res_model', '=', 'account.voucher'),
                                 ('res_id', '=', attach.voucher_id.id),
                                 ('name', '=', fname + '.pdf')]
                            )
                            # attach_ids.write(
                            #     {'datas': result}
                            # )
                            # # Set ir_attachment to cancel
                            self.write({'state': 'cancel'})
                            # Set null invoice ir_attachment
                            attach_ids.write(
                                {'res_id': False}
                            )
                            if attach_ids:
                                attach_xml_ids = attachment_obj.search(
                                    [('res_model', '=', 'account.voucher'),
                                     ('res_id', '=', attach.voucher_id.id),
                                     ('name', '=', fname + '.xml')]
                                )
                                if attach_xml_ids:
                                    attach_xml_ids.write(
                                        {'res_id': False}
                                    )
                        # else: Comentado por que detiene el proceso de cancelacion
                        #     raise Warning(
                        #         _('Error'),
                        #         _("Couldn't cancel invoice")
                        #     )
                    else:
                        raise Warning(
                            _('Error'),
                            _("Unknow driver for %s" % self.type)
                        )
            else:
                raise Warning(
                    _("Type Electronic Invoice Unknow!"),
                    _("The Type Electronic Invoice:" + (self.type or ''))
                )
        return

    def get_tmpl_email_id(self, cr, uid, ids, context=None):
        email_pool = self.pool.get('email.template')
        email_ids = email_pool.search(
            cr, uid,
            [('model_id.model', '=', 'account.voucher')]
        )
        return email_ids and email_ids[0] or False

    def _get_voucher_report(self, cr, uid, id, context=None):
        """
        Helper function to create the PDF report file for invoices
        """
        report_name = "account.voucher.webkit"
        report_service = 'report.' + report_name
        service = netsvc.LocalService(report_service)
        (result, format) = service.create(
            cr, SUPERUSER_ID, [id],
            {'model': 'account.voucher'}, context=context
        )
        # raise Warning("Valors",str(service))
        result = base64.b64encode(result)
        return result


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attachments = self.pool.get('ir.attachment.transport').search(
            cr, SUPERUSER_ID,
            ['|', '|', ('file_input', 'in', ids),
             ('file_xml_sign', 'in', ids), ('file_pdf', 'in', ids)
             ]
        )
        if attachments:
            raise Warning(
                _('Warning!'),
                _('You can not remove an attachment of an payment')
            )
        return super(IrAttachment, self).unlink(cr, uid, ids, context=context)
