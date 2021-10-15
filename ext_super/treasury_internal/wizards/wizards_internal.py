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

class Internal(models.TransientModel):
    _name ='internal.transfers'

    out_company_id = fields.Many2one('res.company', string='Compañía que envía')
    out_journal_id = fields.Many2one('account.journal')
    out_payment_type = fields.Selection([('outbound', 'Enviar Dinero'), ('inbound', 'Recibir Dinero'), ('transfer', 'Transferencia Interna')], default='outbound', string='Tipo de Pago')
    out_payment_method_id = fields.Many2one('account.payment.method', string='Método de Pago')
    out_destination_account_id  = fields.Many2one('account.account')

    in_company_id = fields.Many2one('res.company', string='Recieving Company')
    in_journal_id = fields.Many2one('account.journal')
    in_payment_type = fields.Selection([('outbound', 'Enviar Dinero'), ('inbound', 'Recibir Dinero'), ('transfer', 'Transferencia Interna')], default='inbound', string='Tipo de Pago')
    in_payment_method_id = fields.Many2one('account.payment.method', string='Método de Pago')
    in_destination_account_id  = fields.Many2one('account.account')

    amount = fields.Monetary(string='Monto')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    out_payment_date = fields.Date(string='Fecha de Envío', default=fields.Date.context_today)
    in_payment_date = fields.Date(string='Fecha de Recibo')
    communication = fields.Char(string='Memo')
    payment_concept = fields.Char(string='Concepto de Pago')

    partner_type = fields.Selection([('customer', 'Cliente'), ('supplier', 'Proveedor')], default='supplier')

    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=50)

    def validate(self):
        out_values = {
            'partner_type': self.partner_type,
            'payment_type': self.out_payment_type,
            'company_id': self.out_company_id.id,
            'partner_id': self.in_company_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.out_payment_date,
            'communication': self.communication,
            'journal_id': self.out_journal_id.id,
            'payment_method_id': self.out_payment_method_id.id,
#            'destination_account_id': self.out_destination_account_id.id,
        }

        out_payment = self.env['account.payment'].create(out_values)

        in_values = {
            'partner_type': self.partner_type,
            'payment_type': self.in_payment_type,
            'company_id': self.in_company_id.id,
            'partner_id': self.out_company_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.in_payment_date,
            'communication': self.communication,
            'journal_id': self.in_journal_id.id,
            'payment_method_id': self.in_payment_method_id.id,
            'seller_id': self.out_company_id.id,
            'payment_concept': self.payment_concept,
#            'destination_account_id': self.in_destination_account_id.id,
        }
        in_payment = self.env['account.payment'].create(in_values)

        out_payment.partner_id = self.in_company_id.partner_id.id
#        out_payment.destination_account_id = self.out_destination_account_id.id
#        in_payment.destination_account_id = self.in_destination_account_id.id

        out_payment.post()
        in_payment.post()

        action = self.env.ref('account.action_account_payments').read()[0]
        action['domain'] = [('id', 'in', [out_payment.id, in_payment.id])]
        action['context'] = {}
        return action

