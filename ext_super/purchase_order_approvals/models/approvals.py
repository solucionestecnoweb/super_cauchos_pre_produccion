from odoo import api, fields, models


class ApprovalsCategoryPurchaseExtend(models.Model):
    _inherit = 'approval.category'

    has_purchase_order = fields.Selection(string='Purchase Order', selection=[('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], default='no')

class ApprovalsRequestPurchaseExtend(models.Model):
    _inherit = 'approval.request'

    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Order')
    has_purchase_order = fields.Selection(related="category_id.has_purchase_order")
