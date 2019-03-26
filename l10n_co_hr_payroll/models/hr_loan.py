# -*- coding: utf-8 -*-
import time
import calendar
from odoo import fields, models, api
from odoo.exceptions import except_orm
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Loan Request"

    @api.one
    def _compute_amount(self):
        total_paid_amount = 0.00
        for loan in self:
            for line in loan.loan_line_ids:
                if line.paid:
                    total_paid_amount += line.amortization
            balance_amount = loan.loan_amount - total_paid_amount
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid_amount

    @api.one
    def _get_old_loan(self):
        old_amount = 0.00
        for loan in self.search([('employee_id', '=', self.employee_id.id),
                                 ('state', '=', 'approve')]):
            if loan.id != self.id:
                old_amount += loan.balance_amount
            self.loan_old_amount = old_amount

    name = fields.Char(string="Correlative", default="/", readonly=True)

    date = fields.Date(string="Date", default=fields.Date.today())

    employee_id = fields.Many2one('hr.employee', string="Employee")

    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)

    acreedor_id = fields.Many2one('res.partner', string="Creditor")

    parent_id = fields.Many2one('hr.employee', related="employee_id.parent_id", string="Supervisor")

    department_id = fields.Many2one('hr.department', related="employee_id.department_id",
                                    readonly=True, string="Department")

    job_id = fields.Many2one('hr.job', related="employee_id.job_id",
                             readonly=True, string="Work position")

    emp_salary = fields.Monetary(string="Monthly salary", related="employee_id.contract_id.wage", readonly=True)

    loan_old_amount = fields.Float(string="Not payed", compute='_get_old_loan')

    emp_account_id = fields.Many2one('account.account', string="Employee Account", readonly=True)

    treasury_account_id = fields.Many2one('account.account', string="Destination account")

    journal_id = fields.Many2one('account.journal', string="Daily")

    loan_amount = fields.Float(string="Loan")

    loan_amount_charges = fields.Float(string="Loan with charges", store=True, compute='get_amount_charges')

    quotas_amount_manual = fields.Float(string="Quotas")

    others_loan_amount = fields.Float(string="Others amounts")

    total_amount = fields.Float(string="Total", readonly=True, compute='_compute_amount')

    balance_amount = fields.Float(string="Balance of the amount", compute='_compute_amount')

    total_paid_amount = fields.Float(string="Total Paid", compute='_compute_amount')

    no_month = fields.Integer(string="Month", default=1)

    payment_start_date = fields.Date(string="Initial date", default=fields.Date.today())

    loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Dues", index=True)

    move_id = fields.Many2one('account.move', string="Daily entry", readonly=True)

    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('refuse', 'Rejected')],
                             string="State", default='draft', track_visibility='onchange', copy=False)

    type_loan = fields.Selection([('order', 'Order'), ('loan', 'Loan'),('save', 'Saving funds')],
                                 string="Type", track_visibility='onchange')

    apply_interest = fields.Boolean(string="Apply interest")

    type_payments = fields.Selection([ ('biweekly', 'Biweekly'), ('monthly', 'Monthly')],
                                     string="Type payments", track_visibility='onchange', default="biweekly")

    interest = fields.Float(string="Percentage interest")

    ant_current_interest = fields.Float(string="Anticipated current interest", digits=(12, 3))

    debt_insurance_interest = fields.Float(string="Debt insurance", digits=(12, 3))

    calculate_quotas = fields.Selection([('french', 'Constant quota loan - French system'),
                                         ('german', 'Variable quota loan - German system'),
                                         ('manual', 'Manual')],
                                        string="Quotas calculation", track_visibility='onchange')

    @api.onchange('ant_current_interest',
                  'debt_insurance_interest',
                  'others_loan_amount')
    def get_amount_charges(self):
        total = 0.0
        amount1 = 0.0
        amount2 = 0.0
        amount3 = 0.0
        if self.debt_insurance_interest:
            amount1 = self.loan_amount * (self.debt_insurance_interest / 100)
        if self.ant_current_interest:
            amount2 = self.loan_amount * (self.ant_current_interest / 100)
        if self.others_loan_amount > 0:
            amount3 = self.others_loan_amount
        total = amount1 + amount2 + amount3 + self.loan_amount
        self.loan_amount_charges = total

    @api.onchange('type_loan')
    def get_company_id(self):
        if self.type_loan == 'loan':
            self.acreedor_id = self.env[
                'res.users'].browse([self._uid]).company_id.id
        else:
            self.acreedor_id = False

    @api.model
    def create(self, values):
        values['name'] = ''
        if values['type_loan'] == 'order':
            values['name'] = self.env[
                'ir.sequence'].next_by_code('hr.order.req')
        elif values['type_loan'] == 'loan':
            values['name'] = self.env[
                'ir.sequence'].next_by_code('hr.loan.req')
        elif values['type_loan'] == 'save':
            values['name'] = self.env[
                'ir.sequence'].next_by_code('hr.sf.req')
        else:
            values['name'] = self.env[
                'ir.sequence'].next_by_code('hr.sc.req')
        res = super(HrLoan, self).create(values)
        return res

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def onchange_employee_id(self, employee_id=False):
        old_amount = 0.00
        if employee_id:
            for loan in self.search([('employee_id', '=', employee_id),
                                     ('state', '=', 'approve')]):
                if loan.id != self.id:
                    old_amount += loan.balance_amount
            return {'value': {'loan_old_amount': old_amount}}

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})
        if not self.emp_account_id or not self.treasury_account_id or not \
                self.journal_id:
            raise except_orm('Warning',
                             "You must enter employee account & Treasury \
                             account and journal to approve ")
        if not self.loan_line_ids:
            raise except_orm(
                'Warning', 'You must compute Loan Request before Approved')

        can_close = False
        loan_obj = self.env['hr.loan']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for loan in self:
            company_currency = loan.employee_id.company_id.currency_id.id
            current_currency = self.env.user.company_id.currency_id.id
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            move = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'state': 'posted'
            }

            debit_account_id = loan.treasury_account_id.id
            credit_account_id = loan.emp_account_id.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                cred_l = (0, 0, {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(cred_l)
                credit_sum += cred_l[2]['credit'] - cred_l[2]['debit']
            move.update({'line_ids': line_ids})
            move_id = move_obj.create(move)
            return self.write({'move_id': move_id.id})
        return True

    @api.onchange('type_loan')
    def reset_calculate_quotas(self):
        if self.type_loan == 'save':
            self.calculate_quotas = None
        elif self.calculate_quotas == 'socialc':
            self.self.calculate_quotas = None
        else:
            return

    @api.multi
    def compute_loan_line_french(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        # Variables init
        amount_interest = 0
        amortization = 0
        outstanding_capital = 0
        for loan in self:
            totals_amount = 0
            if loan.loan_amount_charges > 0:
                totals_amount = loan.loan_amount_charges
            else:
                totals_amount = loan.loan_amount
            if self.interest <= 0:
                raise except_orm('Warning',
                                 "You must enter a interest")
            if loan.type_payments == 'biweekly':
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                # French method quota formula
                efec_interest = round((loan.interest/2) / 100.0, 6)
                calc1 = (1 + efec_interest) ** (loan.no_month * 2)
                calc2 = efec_interest * calc1
                calc3 = calc1 - 1
                for i in range(1, (loan.no_month * 2) + 1):
                    # French method quota
                    amount_per_time = totals_amount * (calc2 / calc3)
                    if counter == 1:
                        amount_interest = (totals_amount * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = totals_amount - amortization
                    else:
                        data = loan_line.search(
                            [('loan_id', '=', self.id),
                             ('period', '=', counter - 1)])[0]
                        data_capital = data.outstanding_capital
                        amount_interest = (data_capital * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = data_capital - amortization
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'interest_amount': amount_interest,
                        'amortization': amortization,
                        'outstanding_capital': outstanding_capital,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
            else:
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                # French method quota formula
                efec_interest = round(loan.interest / 100.0, 6)
                calc1 = (1 + efec_interest) ** (loan.no_month)
                calc2 = efec_interest * calc1
                calc3 = calc1 - 1
                for i in range(1, (loan.no_month) + 1):
                    # French method
                    amount_per_time = totals_amount * (calc2 / calc3)
                    if counter == 1:
                        amount_interest = (totals_amount * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = totals_amount - amortization
                    else:
                        data = loan_line.search(
                            [('loan_id', '=', self.id),
                             ('period', '=', counter - 1)])[0]
                        data_capital = data.outstanding_capital
                        amount_interest = (data_capital * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = data_capital - amortization
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'interest_amount': amount_interest,
                        'amortization': amortization,
                        'outstanding_capital': outstanding_capital,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
        return True

    @api.multi
    def compute_loan_line_german(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        # Variables init
        amount_interest = 0
        amortization = 0
        outstanding_capital = 0
        for loan in self:
            totals_amount = 0
            if loan.loan_amount_charges > 0:
                totals_amount = loan.loan_amount_charges
            else:
                totals_amount = loan.loan_amount
            if self.interest <= 0:
                raise except_orm('Warning',
                                 "You must enter a interest")
            if loan.type_payments == 'biweekly':
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                # German method quota
                efec_interest = ((1+(loan.interest/100))**(0.083333333))-1
                for i in range(1, (loan.no_month * 2) + 1):
                    # German method quota
                    amount_per_time = (totals_amount / loan.no_month) / 2
                    if counter == 1:
                        amount_interest = (totals_amount * efec_interest)/2
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = totals_amount - amortization
                    else:
                        data = loan_line.search(
                            [('loan_id', '=', self.id),
                             ('period', '=', counter - 1)])[0]
                        data_capital = data.outstanding_capital
                        amount_interest = (data_capital * efec_interest) / 2
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = data_capital - amortization
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time + amount_interest,
                        'employee_id': loan.employee_id.id,
                        'interest_amount': amount_interest,
                        'amortization': amount_per_time,
                        'outstanding_capital': outstanding_capital,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)

            else:
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                # German method quota
                efec_interest = ((1+(loan.interest/100))**(0.083333333))-1
                for i in range(1, (loan.no_month) + 1):
                    # German method
                    amount_per_time = (totals_amount / loan.no_month)
                    if counter == 1:
                        amount_interest = (totals_amount * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = totals_amount - amortization
                    else:
                        data = loan_line.search(
                            [('loan_id', '=', self.id),
                             ('period', '=', counter - 1)])[0]
                        data_capital = data.outstanding_capital
                        amount_interest = (data_capital * efec_interest)
                        amortization = amount_per_time - amount_interest
                        outstanding_capital = data_capital - amortization
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time + amount_interest,
                        'employee_id': loan.employee_id.id,
                        'interest_amount': amount_interest,
                        'amortization': amount_per_time,
                        'outstanding_capital': outstanding_capital,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
        return True

    @api.multi
    def compute_loan_line_manual(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        for loan in self:
            if loan.type_payments == 'biweekly':
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.quotas_amount_manual
                for i in range(1, (loan.no_month * 2) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
            else:
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.quotas_amount_manual
                for i in range(1, (loan.no_month) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
        return True

    @api.multi
    def compute_loan_line_savef(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        for loan in self:
            if loan.type_payments == 'biweekly':
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.loan_amount / loan.no_month
                for i in range(1, (loan.no_month * 2) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time / 2,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
            else:
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.loan_amount / loan.no_month
                for i in range(1, (loan.no_month) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
        return True

    @api.multi
    def compute_loan_line_socialc(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        for loan in self:
            if loan.type_payments == 'biweekly':
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.loan_amount / loan.no_month
                for i in range(1, (loan.no_month * 2) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time / 2,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
            else:
                date_start_str = datetime.strptime(loan.payment_start_date,
                                                   '%Y-%m-%d')
                counter = 1
                amount_per_time = loan.loan_amount / loan.no_month
                for i in range(1, (loan.no_month) + 1):
                    loan_line.create({
                        'period': counter,
                        'paid_date': date_start_str,
                        'month_name': date_start_str.strftime("%B"),
                        'paid_amount': amount_per_time,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id})
                    counter += 1
                    date_start_str = self.date_start_next(date_start_str,
                                                          loan.type_payments)
        return True

    @api.multi
    def button_reset_balance_total(self):
        total_paid_amount = 0.0
        for loan in self:
            for line in loan.loan_line_ids:
                if line.paid:
                    total_paid_amount += line.paid_amount
            balance_amount = loan.loan_amount - total_paid_amount
            self.write({'total_paid_amount': total_paid_amount,
                        'balance_amount': balance_amount})

    @api.multi
    def date_start_next(self, date_start_str, type_payments):
        if type_payments == 'biweekly':

            if date_start_str.day < 20:

                day_end = calendar.monthrange(date_start_str.year,
                                              date_start_str.month)

                return datetime(year=date_start_str.year,
                                month=date_start_str.month,
                                day=day_end[1])

            else:
                date_start_str = date_start_str + relativedelta(months=1)
                return datetime(year=date_start_str.year,
                                month=date_start_str.month,
                                day=15)
        else:
            date_start_str = date_start_str + relativedelta(months=1)
            day_end = calendar.monthrange(date_start_str.year,
                                          date_start_str.month)
            return datetime(year=date_start_str.year,
                            month=date_start_str.month,
                            day=day_end[1])


class HrLoanLine(models.Model):
    _name = "hr.loan.line"
    _description = "HR Loan Request Line"

    period = fields.Integer(string="Period")

    paid_date = fields.Date(string="Payment date")

    employee_id = fields.Many2one('hr.employee', string="Employee")

    paid_amount = fields.Float(string="Amount payable")

    interest_amount = fields.Float(string="Interest")

    amortization = fields.Float(string="Amortization")

    outstanding_capital = fields.Float(string="Outstanding capital")

    paid = fields.Boolean(string="Paid out")

    month_name = fields.Char(string="Month")

    notes = fields.Text(string="Notes")

    loan_id = fields.Many2one('hr.loan', string="Ref. Of the loan", ondelete='cascade')

    payroll_id = fields.Many2one('hr.payslip', string="Payroll Ref.")

    @api.one
    def action_paid_amount(self):
        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        amount = 0.0
        for line in self:
            if line.loan_id.state != 'approve':
                raise except_orm('Warning', "Loan Request must be approved")
            paid_date = line.paid_date
            if self.loan_id.type_loan in ['save', 'socialc']:
                amount = line.paid_amount
            else:
                amount = line.amortization
            loan_name = line.employee_id.name
            reference = line.loan_id.name
            journal_id = line.loan_id.journal_id.id
            move = {'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': paid_date,
                    'state': 'posted'}
            debit_account_id = line.loan_id.treasury_account_id.id
            credit_account_id = line.loan_id.emp_account_id.id
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': line.loan_id.id,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            if credit_account_id:
                cred_line = (0, 0, {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': line.loan_id.id
                })
                line_ids.append(cred_line)
                credit_sum += cred_line[2]['credit'] - cred_line[2]['debit']

            move.update({'line_ids': line_ids})
            move_obj.create(move)
            return self.write({'paid': True})
        return True
