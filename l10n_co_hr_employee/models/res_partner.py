from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    eps = fields.Boolean(string="Is a Eps?")
    compensation_box = fields.Boolean(string="compensation box?")
    pension_severance_fund = fields.Boolean(
        string="Is pension and severance fund?")
    arl = fields.Boolean(string="Is a Arl?")
    eps_ids = fields.One2many('hr.employee', compute='_compute_eps_ids',
                              store=False)
    arl_ids = fields.One2many('hr.employee', compute='_compute_arl_ids',
                              store=False)
    pension_severance_fund_ids = fields.One2many(
        'hr.employee', compute='_compute_pension_severance_fund_ids',
                                                 store=False)
    compensation_box_ids = fields.One2many(
        'hr.employee', compute='_compute_compensation_box_ids', store=False)

    medical_exam_ids = fields.One2many('hr.medical.exam', 'res_partner_id',
                                       'Medical exam', readonly=True, )

    medical_exam = fields.Boolean(string="Make medical exams?")

    @api.one
    def _compute_eps_ids(self):
        self.eps_ids = self.env['hr.employee'].search([
            ('eps_id', '=', self.id)])

    @api.one
    def _compute_arl_ids(self):
        self.arl_ids = self.env['hr.employee'].search([
            ('arl_id', '=', self.id)])

    @api.one
    def _compute_pension_severance_fund_ids(self):
        self.pension_severance_fund_ids = self.env['hr.employee'].search([
            ('pension_severance_fund_id', '=', self.id)])

    @api.one
    def _compute_compensation_box_ids(self):
        self.compensation_box_ids = self.env['hr.employee'].search([
            ('compensation_box_id', '=', self.id)])
