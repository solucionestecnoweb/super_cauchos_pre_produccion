from odoo import api, fields, models


class ApprovalsCategorySaleExtend(models.Model):
    _inherit = 'approval.category'

    has_sale_order = fields.Selection(string='Sale Order', selection=[('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], default='no')

class ApprovalsRequestSaleExtend(models.Model):
    _inherit = 'approval.request'

    sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    has_sale_order = fields.Selection(related="category_id.has_sale_order")
