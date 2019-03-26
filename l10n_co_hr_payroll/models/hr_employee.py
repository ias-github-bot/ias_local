# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    year_filter = fields.Selection(
        [(num, str(num))
         for num in reversed(range(1900, (datetime.now().year)+1))],
        'Year Filter', default=datetime.now().year)
    salary_hour = fields.Float(string="Salary Hour")
    total_basic = fields.Float(string="Total basic",
                               compute='_get_total_basic')
    total_gross = fields.Float(string="Total gross",
                               compute='_get_total_gross')
    total_eps = fields.Float(string="Total EPS",
                             compute='_get_total_eps')
    total_pension = fields.Float(string="Total pensión",
                                 compute='_get_total_pension')
    total_fsolidaridad = fields.Float(string="Total fondo solidaridad",
                                      compute='_get_total_fsoli')
    total_svida = fields.Float(string="Total seguro de vida",
                                      compute='_get_total_svida')
    total_atrans = fields.Float(string="Total ayuda transporte",
                                compute='_get_total_atrans')
    total_orders = fields.Float(string="Total orders",
                                compute='_get_total_orders')
    total_loans = fields.Float(string="Total loans",
                               compute='_get_total_loans')
    total_sfunds = fields.Float(string="Total save funds",
                                compute='_get_total_sfunds')
    total_all = fields.Float(string="Total",
                             compute='_get_total_all')

    prime = fields.Float(string="Prime")

    loan_ids = fields.One2many('hr.loan', 'employee_id', string="Loans")

    @api.one
    def _get_total_basic(self):
        total_basic = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Basico')])
            if acumulateds:
                for a in acumulateds:
                    total_basic += a.rule_amount
            self.total_basic = total_basic

    @api.one
    def _get_total_gross(self):
        total_gross = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Gross')])
            if acumulateds:
                for a in acumulateds:
                    total_gross += a.rule_amount
            self.total_gross = total_gross

    @api.one
    def _get_total_eps(self):
        total_eps = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'EPS')])
            if acumulateds:
                for a in acumulateds:
                    total_eps += a.rule_amount
            self.total_eps = (-1) * float(total_eps)

    @api.one
    def _get_total_pension(self):
        total_pension = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Pension')])
            if acumulateds:
                for a in acumulateds:
                    total_pension += a.rule_amount
            self.total_pension = (-1) * float(total_pension)

    @api.one
    def _get_total_fsoli(self):
        total_fsolidaridad = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Fondo de solidaridad')])
            if acumulateds:
                for a in acumulateds:
                    total_fsolidaridad += a.rule_amount
            self.total_fsolidaridad = (-1) * float(total_fsolidaridad)

    @api.one
    def _get_total_svida(self):
        total_svida = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Seguro de vida')])
            if acumulateds:
                for a in acumulateds:
                    total_svida += a.rule_amount
            self.total_svida = (-1) * float(total_svida)

    @api.one
    def _get_total_atrans(self):
        total_atrans = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Auxilio de transporte')])
            if acumulateds:
                for a in acumulateds:
                    total_atrans += a.rule_amount
            self.total_atrans = total_atrans

    @api.one
    def _get_total_orders(self):
        total_orders = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Total créditos')])
            if acumulateds:
                for a in acumulateds:
                    total_orders += a.rule_amount
            self.total_orders = (-1) * float(total_orders)

    @api.one
    def _get_total_loans(self):
        total_loans = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Total préstamos')])
            if acumulateds:
                for a in acumulateds:
                    total_loans += a.rule_amount
            self.total_loans = (-1) * float(total_loans)

    @api.one
    def _get_total_sfunds(self):
        total_sfunds = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'Total ahorros')])
            if acumulateds:
                for a in acumulateds:
                    total_sfunds += a.rule_amount
            self.total_sfunds = (-1) * float(total_sfunds)

    @api.one
    def _get_total_all(self):
        total_all = 0.0
        if self.year_filter:
            acumulateds = self.env['hr.employee.acumulated'].search(
                [('employee_id', '=', self.id),
                 ('year_name', '=', self.year_filter),
                 ('rule_name', '=', 'TOTAL')])
            if acumulateds:
                for a in acumulateds:
                    total_all += a.rule_amount
            self.total_all = total_all
