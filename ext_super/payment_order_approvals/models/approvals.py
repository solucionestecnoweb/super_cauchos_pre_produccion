from odoo import api, fields, models


class ApprovalsCategoryPaymentExtend(models.Model):
    _inherit = 'approval.category'

    has_payment_order = fields.Selection(string='Payment Order', selection=[('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], default='no')

class ApprovalsRequestPaymentExtend(models.Model):
    _inherit = 'approval.request'

    payment_order_id = fields.Many2one(comodel_name='purchase.pay.order', string='Payment Order')
    has_payment_order = fields.Selection(related="category_id.has_payment_order")
