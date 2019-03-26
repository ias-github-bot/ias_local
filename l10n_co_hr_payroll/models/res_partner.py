from odoo import models, fields


class ResPartnerAcreedores(models.Model):
    _inherit = 'res.partner'

    acreedor = fields.Boolean(string="Is a creditor?")
    is_active = fields.Boolean(string="Active creditor?")
    code = fields.Char(string='Code')
    percentage_social_contribution = fields.Float(
        string="Percentage social contribution")
    top_social_contribution = fields.Float(string="top social contribution")
