# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployeeAcumulated(models.Model):

    _name = "hr.employee.acumulated"
    _description = 'Acumulated accounts from payroll'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    wage = fields.Float('Wage', required=False)
    date = fields.Date('Date')
    year_name = fields.Char('Year')
    last_month = fields.Char('Last registry')
    rule_name = fields.Char('Rule name')
    rule_amount = fields.Float('Rule amount')
