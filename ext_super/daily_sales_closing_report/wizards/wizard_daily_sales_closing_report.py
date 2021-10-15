from datetime import datetime, timedelta
from operator import mod
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import json
import csv
import xlwt

_logger = logging.getLogger(__name__)

class DailySales(models.Model):
    _name = 'daily.sales'

    name = fields.Date(string='Invoice Date')
    invoice_num = fields.Char(string='Invoice Number')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    currency_rate = fields.Float(string='Rate')
    total_bs = fields.Float(string='Total Bs. Operation')
    total_usd = fields.Float(string='Total $ Operation')
    payment_condition_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Condition')
    amount = fields.Float(string='Amount')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency')

class DailySalesReport(models.Model):
    _name = 'daily.sales.report'

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_now = fields.Datetime(string='Date Now', default=lambda *a:datetime.now())

    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=50)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)

    # *******************  FORMATOS ****************************

    def float_format(self,valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def print_report(self):
        self.env['daily.sales'].search([]).unlink()
        self.get_invoice()
        return {
            'type': 'ir.actions.report',
            'report_name': 'daily_sales_closing_report.daily_sales_closing_report',
            'report_type':"qweb-pdf"
            }

    def get_methods(self):
        xfind = self.env['account.payment.method'].search([
                ('sales_report', '=', True),
            ])
        return xfind

    def get_invoice(self):
        xfind = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('type', '=', 'out_invoice'),
            ('invoice_payment_state', '=', 'paid'),
        ])
        
        for item in xfind:
            # Tasa y montos en bs/$
            rate = 0.00
            if item.currency_id.id == 3:
                rates = item.env['res.currency.rate'].search([
                    ('name', '=', item.invoice_date)
                ], limit=1).sell_rate
                if rates > 0:
                    rate = rates
                else:
                    rate = 1
            else:
                if item.os_currency_rate > 0:
                    rate = item.os_currency_rate
                else:
                    rate = 1

            if item.currency_id.id == 3:
                total_bs = item.amount_total
                total_usd = round(item.amount_total / rate, 2)
            else:
                total_bs =round (item.amount_total * item.os_currency_rate, 2)
                total_usd = item.amount_total

            # Metodos de pago admitidos
            methods = []
            for line in self.get_methods():
                methods.append(line.id)

            if item.invoice_payments_widget:
                parse_dict = json.loads(item.invoice_payments_widget)
                if parse_dict:
                    for pay in parse_dict.get('content'):
                        varx = pay['account_payment_id']
            if varx:
                payment_condition = self.env['account.payment'].search([
                    ('id', '=', varx)
                ]).payment_method_id.id
            else:
                payment_condition = varx
                
            #Valores finales para crear
            values = {
                'name': item.invoice_date,
                'invoice_num': item.invoice_number_cli,
                'partner_id': item.partner_id.id,
                'currency_rate': rate,
                'total_bs': total_bs,
                'total_usd': total_usd,
                'payment_condition_id': payment_condition,
                'amount': item.amount_total,
                'currency_id': item.currency_id.id,
            }
            self.env['daily.sales'].create(values)

    def get_lines(self):
        xfind = self.env['daily.sales'].search([])
        return xfind

    def show_daily_sales(self):
        self.env['daily.sales'].search([]).unlink()
        self.get_invoice()
        self.ensure_one()
        res = self.env.ref('daily_sales_closing_report.daily_sales_action').read()[0]
        return res

    # *******************  REPORTE EN EXCEL ****************************

    def generate_xls_report(self):
        self.env['daily.sales'].search([]).unlink()
        self.get_invoice()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet(_('Daily Sales Closing Report'))
        fp = BytesIO()

        header_tittle_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170; align: horiz center, vert centre;")
        header_content_style = xlwt.easyxf("font: name Helvetica size 16 px, bold 1, height 170; align: horiz center, vert centre; pattern:pattern solid, fore_colour silver_ega;")
        lines_style_center = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: bottom thin; align: horiz center, vert centre;")
        lines_style_right = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: bottom thin; align: horiz right, vert centre;")
        
        row = 0
        col = 0
        ws1.row(row).height = 500
        ws1.write_merge(row,row, 3, 5, _("Daily Sales Closing Report"), header_tittle_style)
        xdate = self.date_now.strftime('%d/%m/%Y %I:%M:%S %p')
        xdate = datetime.strptime(xdate,'%d/%m/%Y %I:%M:%S %p') - timedelta(hours=4)
        ws1.write_merge(row,row, 6, 8, xdate.strftime('%d/%m/%Y %I:%M:%S %p'), header_tittle_style)
        row += 2

        #CABECERA DE LA TABLA 
        ws1.write(row,col+0, _("Date"),header_content_style)
        ws1.col(col+0).width = int((len('xx/xx/xxxx')+2)*256)
        ws1.write(row,col+1, _("Invoice Num"),header_content_style)
        ws1.col(col+1).width = int((len('Invoice Num')+5)*256)
        ws1.write(row,col+2, _("Customer"),header_content_style)
        ws1.col(col+2).width = int((len('Customer')+40)*256)
        ws1.write(row,col+3, _("Rate"),header_content_style)
        ws1.col(col+3).width = int(len('xxx.xxx.xxx,xx')*256)
        ws1.write(row,col+4,_("Total Bs. Operation"),header_content_style)
        ws1.col(col+4).width = int((len('xxx.xxx.xxx.xxx,xx')+2)*256)
        ws1.write(row,col+5, _("Total $ Operation"),header_content_style)
        ws1.col(col+5).width = int((len('xxx.xxx.xxx.xxx,xx')+2)*256)
        col_auto = 5
        for item in self.get_methods():
            col_auto += 1
            ws1.write(row,col_auto, item.name,header_content_style)

        #Totales
        total_bs = 0
        total_usd = 0
        #####
        total_final_bs = 0

        for item in self.get_lines():
            row += 1
            # Date
            if item.name:
                ws1.write(row,col+0, item.name.strftime('%d/%m/%Y'),lines_style_center)
            else:
                ws1.write(row,col+0, '',lines_style_center)
            # Invoice Number
            if item.invoice_num:
                ws1.write(row,col+1, item.invoice_num,lines_style_center)
            else:
                ws1.write(row,col+1, '',lines_style_center)
            # Customer
            if item.partner_id.name:
                ws1.write(row,col+2, item.partner_id.name,lines_style_center)
            else:
                ws1.write(row,col+2, item.name,lines_style_center)
            # Rate
            if item.currency_rate:
                ws1.write(row,col+3, self.float_format(item.currency_rate),lines_style_right)
            else:
                ws1.write(row,col+3, '',lines_style_right)
            # Total Bs. Operation
            if item.total_bs:
                ws1.write(row,col+4, self.float_format(item.total_bs),lines_style_right)
            else:
                ws1.write(row,col+4, '',lines_style_right)
            # Total $ Operation
            if item.total_usd:
                ws1.write(row,col+5, self.float_format(item.total_usd),lines_style_right)
            else :
                ws1.write(row,col+5,'',lines_style_right)

            col_auto = 5
            for line in self.get_methods():
                col_auto += 1
                if item.payment_condition_id.id == line.id:
                    ws1.write(row,col_auto, self.float_format(item.amount),lines_style_right)
                    ws1.col(col_auto).width = int(len('xxx.xxx.xxx,xx')*256)
                else:
                    ws1.write(row,col_auto, self.float_format(0.00),lines_style_right)
                    ws1.col(col_auto).width = int(len('xxx.xxx.xxx,xx')*256)
            
            total_bs += item.total_bs
            total_usd += item.total_usd
                
        row += 1
        ws1.write(row,col+4, total_bs,lines_style_right)
        ws1.write(row,col+5, total_usd,lines_style_right)
        col_auto = 5
        for line in self.get_methods():
            total_amount = 0
            col_auto += 1
            for item in self.get_lines():
                if item.payment_condition_id.id == line.id:
                    total_amount += item.amount
            ws1.write(row,col_auto, total_amount,lines_style_right)

        row += 2
        ws1.write(row,col+3, '',lines_style_center)
        ws1.write(row,col+4, _('$ Amount'),lines_style_center)
        ws1.write(row,col+5, _('Bs. Amount'),lines_style_center)
        for line in self.get_methods():
            total_bs = 0
            total_usd = 0
            for item in self.get_lines():
                if item.payment_condition_id.id == line.id:
                    total_bs += item.total_bs
                    total_usd += item.total_usd
                    total_final_bs += item.total_bs
            row += 1
            ws1.write(row,col+3, line.name,lines_style_center)
            ws1.write(row,col+4, self.float_format(total_usd),lines_style_right)
            ws1.write(row,col+5, self.float_format(total_bs),lines_style_right)
        row += 1
        ws1.write_merge(row,row,col+3,col+4, _('Total Bs.'),lines_style_center)
        ws1.write(row,col+5, self.float_format(total_final_bs),lines_style_right)

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        self.write({'state': 'get', 'report': out, 'name': _('Daily Sales Closing Report ')+ fecha +'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'daily.sales.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }