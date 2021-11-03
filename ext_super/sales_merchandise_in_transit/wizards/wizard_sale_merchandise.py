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

class SaleMerchandiseTransit(models.TransientModel):
    _name = 'sale.merchandise.transit'

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_now = fields.Datetime(string='Date Now', default=lambda *a:datetime.now())
    
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=50)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)

    def print_pdf(self):
        return {'type': 'ir.actions.report','report_name': 'sales_merchandise_in_transit.sales_merchandise_in_transit','report_type':"qweb-pdf"}

    def get_merchandise(self):
        xfind = self.env['purchase.order.line'].search([
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ('draft', 'sent', 'purchase')),
            ('qty_received', '=', 0),
        ])
        return xfind

    def date_fix(self):
        new_date = self.date_now - timedelta(hours=4)
        return new_date