from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class PriceList(models.TransientModel):
    _name = "stock.wizard.price.list"

    date_now = fields.Datetime(string='Date Now', default=lambda *a:datetime.now())

    category_id = fields.Many2many(comodel_name='product.category', string='Category')
    pricelist_id = fields.Many2many(comodel_name='product.pricelist', string='Product Pricelist')
    warehouse_id = fields.Many2many(comodel_name='stock.location', string='Deposito')
    show_qty = fields.Boolean(string='¿Mostrar cantidad en el reporte?')

    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.company.id)

    def print_inventario(self):
        return {'type': 'ir.actions.report','report_name': 'product_list_prices_multi_currency.prices_list_report','report_type':"qweb-pdf"}

    def _get_products(self, category):
        categ = []
        temp = []
        for item in category:
            if item.parent_id:
                temp.append(item.id)
            else:
                xfind = self.env['product.category'].search([('parent_id', '=', item.id)])
                if xfind:
                    for line in xfind:
                        temp.append(line.id)
                else:
                    temp.append(item.id)
        temp = set(temp)
        for item in temp:
            categ.append(item)
        
        xfind = self.env['product.product'].search([
            ('type', '=', 'product'),
            ('categ_id', 'in', categ),
            ('qty_available', '>', 0)
        ])

        xfind = set(xfind)
        result = []

        for item in xfind:
            cantidad = self.get_qty(item)
            if cantidad > 0:
                result += item         

        return result

    def get_categ(self, category):
        categ = []
        temp = []
        for item in category:
            if item.parent_id:
                temp.append(item.id)
            else:
                xfind = self.env['product.category'].search([('parent_id', '=', item.id)])
                if xfind:
                    for line in xfind:
                        temp.append(line.id)
                else:
                    temp.append(item.id)
        temp = set(temp)
        for item in temp:
            categ.append(item)
        
        xfind = self.env['product.category'].search([('id', 'in', categ)])
        
        return xfind

    def get_qty(self, producto):
        if self.warehouse_id:
            stock_q = self.env['stock.quant'].search([
                ('product_id', '=', producto.id),
                ('location_id', 'in', self.warehouse_id.ids),
                ('quantity', '>', 0),
               # ('company_id', 'in', self.env.company.ids)
            ])
        else:
            stock_q = self.env['stock.quant'].search([
                ('product_id', '=', producto.id),
                ('quantity', '>', 0),
            #    ('company_id', '=', self.env.company.ids)
            ])
        cantidad = 0
        for item in stock_q:
            cantidad += item.quantity - item.reserved_quantity

        return cantidad

    def get_iva(self, producto, monto):
        result = 0
        if producto.taxes_id:
            if producto.taxes_id[0].amount > 0:
                result = (producto.taxes_id[0].amount * monto) / 100

        return result

    def _get_prices(self):
        prices = []
        for item in self.pricelist_id:
            prices.append(item.id)
        xfind = self.env['product.pricelist'].search([
            ('id', 'in', prices)
        ])
        return xfind

    def _get_rate(self):
        xfind = self.env['res.currency.rate'].search([
            ('name', '<=', fields.date.today()),
            ('company_id', '=', self.env.user.company_id.id)
        ], limit=1).sell_rate
        return xfind