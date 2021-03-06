from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class Days(models.TransientModel):
    _name = "days.report"

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_now = fields.Datetime(string='Date Now', default=lambda *a:datetime.now())

    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=50)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    currency_bs_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    currency_usd_id = fields.Many2one('res.currency', default= lambda self: self.env['res.currency'].search([('id', '=', 2)]))

    def print_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': 'reports_days.days_report',
            'report_type':"qweb-pdf"
            }

    def get_lines(self):
        xfind = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to), ('invoice_payment_state', '=', 'paid')])
        return xfind

    def show_days(self):
        self.env['account.move'].search([])
        self.ensure_one()
        res = self.env.ref('reports_days.type_days_name_action').read()[0]
        return res

    # *******************  REPORTE EN EXCEL ****************************

    def generate_xls_report(self):

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet(_('Reporte de D??as Promedio'))
        fp = BytesIO()

        header_content_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170; align: horiz center;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170")
        sub_header_style_c = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz center")
        sub_header_style_r = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;")

        row = 0
        col = 0
        ws1.row(row).height = 500
        ws1.write_merge(row,row, 6, 7, _("Reporte de D??as Promedio"), header_content_style)
        xdate = self.date_now.strftime('%d/%m/%Y %I:%M:%S %p')
        xdate = datetime.strptime(xdate,'%d/%m/%Y %I:%M:%S %p') - timedelta(hours=4)
        xname = self.company_id.name
        xvat = self.company_id.vat
        ws1.write_merge(row,row, 0, 1, xname, header_content_style)
        ws1.write_merge(row,row, 2, 3, xvat, header_content_style)
        ws1.write_merge(row,row, 10, 11, xdate.strftime('%d/%m/%Y %I:%M:%S %p'), header_content_style)
        row += 2

        #CABECERA DE LA TABLA 
        ws1.col(col).width = 250
        ws1.write(row,col+0, _("Fecha de Vencimiento"),sub_header_style_c)
        ws1.col(col+0).width = int((len('xx/xx/xxxx')+10)*256)
        ws1.write(row,col+1, _("F Vence/H"),sub_header_style_c)
        ws1.col(col+1).width = int((len('xx/xx/xxxx')+10)*256)        
        ws1.write(row,col+2, _("Fecha de Pago"),sub_header_style_c)
        ws1.col(col+2).width = int((len('xx/xx/xxxx')+10)*256)
        ws1.write(row,col+3, _("D??as Prom"),sub_header_style_c)
        ws1.col(col+3).width = int((len('D??as Prom')+4)*256)
        ws1.write(row,col+4, _("D??as Prom/H"),sub_header_style_c)
        ws1.col(col+4).width = int((len('D??as Prom/H')+4)*256)
        ws1.write(row,col+5, _("D??as C"),sub_header_style_c)
        ws1.col(col+5).width = int((len('D??as C')+4)*256)
        ws1.write(row,col+6, _("Nro Pago"),sub_header_style_c)
        ws1.col(col+6).width = int((len('Nro Pago')+20)*256)
        ws1.write(row,col+7, _("Doc. Afect"),sub_header_style_c)
        ws1.col(col+7).width = int((len('Doc. Afect')+20)*256)
        ws1.write(row,col+8, _("Cliente"),sub_header_style_c)
        ws1.col(col+8).width = int((len('Cliente')+26)*256)
        ws1.write(row,col+9, _("Monto en Bs"),sub_header_style_c)
        ws1.col(col+9).width = int((len('Monto en Bs')+10)*256)
        ws1.write(row,col+10, _("Tasa"),sub_header_style_c)
        ws1.col(col+10).width = int((len('Tasa')+15)*256)
        ws1.write(row,col+11, _("Monto en $"),sub_header_style_c)
        ws1.col(col+11).width = int((len('Monto en $')+10)*256)

        center = xlwt.easyxf("align: horiz center")
        right = xlwt.easyxf("align: horiz right")

        #Totales
        total_days = 0
        total_slack_days = 0
        total_street_days = 0
        total_bs = 0
        total_usd = 0

        for item in self.get_lines():
            row += 1
            # Date of Expiration
            if item.invoice_date_due:
                ws1.write(row,col+0, item.invoice_date_due.strftime('%d/%m/%Y'),center)
            else:
                ws1.write(row,col+0, '',center)
            # Date of Expiration with Slack
            if item.date_due_slack:
                ws1.write(row,col+1, item.date_due_slack.strftime('%d/%m/%Y'),center)
            else:
                ws1.write(row,col+1, '',center)
            # Date of Payment
            if item.payment_date:
                ws1.write(row,col+2, item.payment_date.strftime('%d/%m/%Y'),center)
            else:
                ws1.write(row,col+2, '',center)
            # Average Days
            if item.days:
                ws1.write(row,col+3, item.days,center)
            else:
                ws1.write(row,col+3, '0',center)
            # Average Days with Slak
            if item.slack:
                ws1.write(row,col+4, item.slack,center)
            else:
                ws1.write(row,col+4, '0',center)
            # Street Days
            if item.street_days:
                ws1.write(row,col+5, item.street_days,center)
            else:
                ws1.write(row,col+5, '0',center)
            # Paymente Reference
            if item.invoice_payment_ref:
                ws1.write(row,col+6, item.invoice_payment_ref,center)
            else:
                ws1.write(row,col+6, '',center)
            # Bill
            if item.name:
                ws1.write(row,col+7, item.name,center)
            else:
                ws1.write(row,col+7, '',center)
            # Customer
            if item.invoice_partner_display_name:
                ws1.write(row,col+8, item.invoice_partner_display_name,center)
            else:
                ws1.write(row,col+8, '',center)
            # Amount in Bs
            if item.amount_total:
                ws1.write(row,col+9, item.amount_total,right)
            else:
                ws1.write(row,col+9, '',right)
            # Rate
            if item.rate:
                ws1.write(row,col+10, item.rate,right)
            else:
                ws1.write(row,col+10, '',right)
            # Amount in $
            if item.amount_currency:
                ws1.write(row,col+11, item.amount_currency,right)
            else:
                ws1.write(row,col+11, '',right)

            total_days += item.days
            total_slack_days += item.slack
            total_street_days += item.street_days
            total_bs += item.amount_total
            total_usd += item.amount_currency
                
        row += 1
        ws1.write_merge(row,row, 0, 2, ("Totales..."), sub_header_style_c)
        ws1.write(row,col+3, total_days,center)
        ws1.write(row,col+4, total_slack_days,center)
        ws1.write(row,col+5, total_street_days,center)
        ws1.write(row,col+9, total_bs,right)
        ws1.write(row,col+11, total_usd,right)

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        self.write({'state': 'get', 'report': out, 'name': _('Reporte de D??as Promedio ')+ fecha +'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'days.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }