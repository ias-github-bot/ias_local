from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class HRSocialContribution(models.Model):
    _name = "hr.social.contribution"
    _inherit = ['mail.thread']

    acreedor_id = fields.Many2one(
        'res.partner', string="Creditor", required=True)
    date = fields.Date(
        string="Date", default=fields.Date.today(), readonly=True)
    state = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')], string="State",
        default='inactive', copy=False)
    social_contribution_ids = fields.One2many(
        'hr.social.contribution.line', 'social_contribution_id',
        string="Partners", index=True)

    @api.multi
    def action_activate(self):
        self.write({'state': 'active'})

    @api.multi
    def action_inactivate(self):
        return self.write({'state': 'inactive'})

    @api.model
    def create(self, vals):
        if vals.get('acreedor_id'):
            ids = self.env['hr.social.contribution'].search(
                [('state', '=', 'active'),
                 ('acreedor_id', '=', vals.get('acreedor_id'))])
            if ids:
                raise UserError(
                    _("Sorry, there is already a social contribution "
                      "on behalf of this active status"),)

        res = super(HRSocialContribution, self).create(vals)
        return res


class HRSocialContributionLine(models.Model):
    _name = "hr.social.contribution.line"

    employee_id = fields.Many2one('hr.employee', string="Employee")

    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)

    emp_salary = fields.Monetary(string="Monthly salary", related="employee_id.contract_id.wage", readonly=True)

    social_contribution_id = fields.Many2one('hr.social.contribution', string="Ref. Of the loan", ondelete='cascade')

    social_contribution = fields.Float(string="Total Social contribution",
                                       compute='_compute_social_contribution')

    @api.one
    def _compute_social_contribution(self):
        social_contribution = 0.00
        self.pay_biweekly = 0
        acreedor_id = self.social_contribution_id.acreedor_id

        if acreedor_id:
            percentage = acreedor_id.percentage_social_contribution
            top = acreedor_id.top_social_contribution
            if percentage:
                social_contribution = (self.emp_salary * percentage / 100)
        if social_contribution > top:
            social_contribution = top
        self.social_contribution = social_contribution
