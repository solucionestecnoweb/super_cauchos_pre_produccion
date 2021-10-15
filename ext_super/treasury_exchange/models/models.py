import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models, _
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning
import time

class Exchange(models.Model):
    _name ='account.exchange'

    name = fields.Char(string='Transaction', default='/')

    amount = fields.Monetary(string="Amount", currency_field='origin_currency_id')
    transaction = fields.Selection(selection=[("buy","Buy"),("sale","Sale")] ,string="Transaction", default='buy')
    final_currency_id = fields.Many2one ('res.currency', default= lambda self: self.env['res.currency'].search([('id', '=', 2)]))
    debit_id = fields.Many2one ('res.partner.bank',)
    rate = fields.Float(compute='_compute_rate' ,string="Rate")
    credit_id = fields.Many2one ('res.partner.bank',)
    final_amount = fields.Monetary(string="Final Amount", currency_field='final_currency_id')
    company_id = fields.Many2one ('res.company', default=lambda self: self.env.user.company_id.id)
    origin_currency_id = fields.Many2one ('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    request = fields.Date(string='Date of request', default=fields.Date.context_today)
    confirmation = fields.Datetime(string='Date of confirmation')
    reference = fields.Char ("Bank reference")
    state = fields.Selection(selection=[("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done"), ("cancel", "Cancel")], default="draft")

    @api.constrains('state')
    def _compute_name(self):
        if self.name == '/' and self.state == 'confirmed':
            self.name = self.env['ir.sequence'].next_by_code('account.exchange.seq')

    def _compute_rate(self):
        for item in self:
            rate_value = 1
            rate = item.env['res.currency.rate'].search([('name','=', item.request)], limit=1).sell_rate
            if rate:
                rate_value = rate
            item.rate = rate_value

    @api.onchange('request')
    def _onchange_rate(self):
        rate = self.env['res.currency.rate'].search([('name','=', self.request)], limit=1).sell_rate
        if not rate:
            return {'warning': {'message':'No existe una tasa para esta fecha'}}

    def calculate(self):
        if(self.origin_currency_id.name == 'USD' or self.origin_currency_id.name == 'EUR'):
            self.final_amount = self.amount * self.rate
        
        elif (self.origin_currency_id.name in ('Bs.', 'Bs', 'bs', 'bs.', 'BS', 'BS.')):
            self.final_amount = self.amount / self.rate
    
    def draft(self):
        self.state = "draft"
    
    def confirmed(self):
        self.state = "confirmed"

    def done(self):
        self.confirmation = fields.Datetime.now()
        self.state = "done"

    def cancel(self):
        self.state = "cancel"