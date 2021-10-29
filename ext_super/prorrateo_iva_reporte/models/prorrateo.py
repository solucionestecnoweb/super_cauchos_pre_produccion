from operator import index
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import base64
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.float_utils import float_round

class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_prorrateo_iva = fields.Many2one('prorrateo.iva', string='Prorrateo compras')
    sale_prorrateo_iva = fields.Many2one('prorrateo.iva', string='Prorrateo Ventas')

class ResCompany(models.Model):
    _inherit = "res.company"

    account_journal_prorrateo   = fields.Many2one('account.journal', string='Diario para prorrateo')
    account_prorrateo_debe      = fields.Many2one('account.account', string='Cuenta Acreedora')
    account_prorrateo_haber     = fields.Many2one('account.account', string='Cuenta Adeudora')
    prorrateo_iva = fields.Boolean(string='Prorratear IVA')


class ProrrateoIva(models.Model):
    _name = "prorrateo.iva"

    name = fields.Char(string='Código', default='Borrador')
    desde = fields.Date(string='Desde')
    hasta = fields.Date(string='Hasta')

    deducible = fields.Float(string='% Deducible', )
    no_deducible = fields.Float(string='% No Deducible')
    total_deducible = fields.Float(string='Total Deducible', )
    total_no_deducible = fields.Float(string='Total No Deducible')

    state = fields.Selection(string='Estado', selection=[('draft', 'Borrador'), ('posted', 'Publicado')], default='draft')
    company_id = fields.Many2one('res.company','Compañía',default=lambda self: self.env.company.id)
    
    move_id = fields.Many2one('account.move','Asientos Contables')

    prorrateo_ids = fields.Many2many(comodel_name='data.prorrateo.iva', string='Datos Prorrateo')
    purchase_invoice_ids = fields.One2many('account.move', 'purchase_prorrateo_iva', string='Facturas de Compras')
    purchase_amount_untaxed_signed = fields.Float(string='Total Base Imponible')
    purchase_amount_tax = fields.Float(string='Total Impuesto')
    purchase_amount_total_signed = fields.Float(string='Total Factura')

    sale_invoice_ids = fields.One2many('account.move','sale_prorrateo_iva', 'Facturas de Ventas')
    sale_amount_untaxed_signed = fields.Float(string='Total Base Imponible')
    sale_amount_tax = fields.Float(string='Total Impuesto')
    sale_amount_total_signed = fields.Float(string='Total Factura')

    ventas_gravadas = fields.Float(string='Ventas Gravadas')
    ventas_totales  = fields.Float(string='Ventas Totales')

    data_prorrateo_id = fields.One2many('data.prorrateo.iva','prorrateo_id', string='Apuntes Contables')
    
    ### Nombre Código ###

    def search_invoice(self):
        gravados = ('general','reduced','additional')

        self.sale_amount_untaxed_signed = 0
        self.sale_amount_tax = 0
        self.sale_amount_total_signed = 0
        self.ventas_gravadas = 0
        self.ventas_totales= 0
        invoice_sale = self.env['account.move'].search([
            ('invoice_date','>=',str(self.desde)),
            ('invoice_date','<=',str(self.hasta)),
            ('state','in',('posted','cancel' )),
            ('type','in',('out_invoice','out_refund','out_receipt')),
            ('company_id','=',self.env.company.id)
            ])
        for item in invoice_sale:
            item.sale_prorrateo_iva = self.id
            self.sale_amount_untaxed_signed += item.amount_untaxed_signed
            self.sale_amount_tax += item.amount_tax_signed
            self.sale_amount_total_signed += item.amount_total_signed
            for line in item.invoice_line_ids:
                if self.company_id.currency_id.id == item.currency_id.id:
                        if line.tax_ids[0].aliquot in gravados:
                            self.ventas_gravadas += line.price_total
                            self.ventas_totales += line.price_total
                        else :
                            self.ventas_totales += line.price_total
        self.deducible = (self.ventas_gravadas / self.ventas_totales) * 100
        self.no_deducible = 100 - self.deducible
        self.purchase_amount_untaxed_signed = 0
        self.purchase_amount_tax = 0
        self.purchase_amount_total_signed = 0

        self.data_prorrateo_id.unlink()
        invoice_purchase = self.env['account.move'].search([
            ('invoice_date','>=',str(self.desde)),
            ('invoice_date','<=',str(self.hasta)),
            ('state','in',('posted','cancel' )),
            ('type','in',('in_invoice','in_refund','in_receipt')),
            ('company_id','=',self.env.company.id)
            ])
        for item in invoice_purchase:
            item.purchase_prorrateo_iva = self.id
            self.purchase_amount_untaxed_signed += item.amount_untaxed_signed
            self.purchase_amount_tax += item.amount_tax_signed
            self.purchase_amount_total_signed += item.amount_total_signed
            for line in item.invoice_line_ids:
                if line.account_id.prorreatable == True or line.account_id.group_id.prorreatable == True:
                    if line.tax_ids[0].aliquot in gravados:
                        credito = line.price_unit * (line.tax_ids[0].amount / 100)
                        deducible = credito * ( self.deducible / 100)
                        no_deducible = credito - deducible

                        self.total_deducible += deducible
                        self.total_no_deducible += no_deducible

                        self.env['data.prorrateo.iva'].create({
                            'cliente':line.partner_id.name,
                            'n_factura': item.invoice_number_pro,
                            'cuenta':line.account_id.name,
                            'prorrateo_id':self.id,
                            'credito_fiscal':credito,
                            'deducible':deducible,
                            'no_deducible':no_deducible
                        })
        
    @api.constrains('state')
    def constraint_name(self):
        if self.name == 'Borrador':
            self.name = self.env['ir.sequence'].next_by_code('prorrateo.iva.seq')

    ### Estados ###

    def post(self):
        self.state = 'posted'
        ref = "Prorrateo " + str(self.desde)  + ' ' + str(self.hasta),
        invoice_1 = self.env['account.move'].create({
            'type': 'entry',
            'ref': ref,
            'date': fields.Date.today(),
            'partner_id': self.company_id.partner_id.id,
            'currency_id': self.company_id.currency_id.id,
            'journal_id':self.company_id.account_journal_prorrateo.id,
            'line_ids': [(0, 0, {
                'name': ref,
                'account_id': self.company_id.account_prorrateo_debe.id,
                'debit': self.total_deducible,
                'credit':0,
            }),(0, 0, {
                'name': ref,
                'account_id': self.company_id.account_prorrateo_haber.id,
                'debit': 0,
                'credit':self.total_deducible,
            })],
        })
        self.move_id = invoice_1.id 
        self.move_id.action_post()
    
    def draft(self):
        self.move_id.button_draft()
        self.move_id.unlink()
        self.state = 'draft'

    ### Formatos ###

    def float_format(self,valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"


class DataProrrateoIVA(models.Model):
    _name = 'data.prorrateo.iva'

    cliente = fields.Char(string='Cliente')
    n_factura = fields.Char(string='Nro Factura')
    cuenta = fields.Char(string='Cuenta')
    credito_fiscal = fields.Float(string='Credito Fiscal')
    deducible = fields.Float(string='Deducible')
    no_deducible = fields.Float(string='No Deducible')
    tipo = fields.Selection(string='Tipo', selection=[('nd', 'nd'), ('pd', 'pd'), ('td', 'td')])
    prorrateo_id = fields.Many2one(comodel_name='prorrateo.iva', string='Prorrateo')
    