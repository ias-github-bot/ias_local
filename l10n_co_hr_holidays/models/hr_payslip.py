# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from datetime import time as datetime_time
from odoo import models, fields, api, _
from workalendar.america import Colombia


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_diseases_type(self):
        # Diseases
        self.general_disease = False
        self.professional_disease = False
        diseases_ids = self.env['hr.holidays'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'validate'),
             ('date_from', '<=', self.date_to),
             ('date_to', '>=', self.date_from),
             ('holiday_status_type', 'in', ['GD', 'PD']),
             ('payed', '=', False)])
        for data in diseases_ids:
            if data.holiday_status_type:
                if data.holiday_status_type == 'GD':
                    self.general_disease = True
                if data.holiday_status_type == 'PD':
                    self.professional_disease = True

    general_disease = fields.Boolean(
        "General disease", compute='_compute_diseases_type', store=True)
    professional_disease = fields.Boolean(
        "Professional disease", compute='_compute_diseases_type', store=True)

    @api.model
    def action_payslip_done(self):
        result = super(HrPayslip, self).action_payslip_done()
        holidays_obj = self.env['hr.holidays']
        holidays_ids = holidays_obj.search(
            [('employee_id', '=', self.employee_id.id),
             ('payed', '=', False),
             ('date_from', '<=', self.date_to),
             ('date_to', '>=', self.date_from),
             ('holiday_status_type', 'in', ['GD', 'PD'])])
        for data in holidays_ids:
            if data:
                if self.date_from <= data.date_from:
                    if self.date_to >= data.date_to:
                        data.write({'payed': True})
        return result

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be
            applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(
                lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(
                fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_to), datetime_time.max)

            # compute leave days
            leaves = {}
            day_leave_intervals = contract.employee_id.iter_leaves(
                day_from, day_to, calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    if holiday.holiday_status_type == 'GD' and not holiday.payed:
                        name = 'GenDisease'
                    elif holiday.holiday_status_type == 'PD' and not holiday.payed:
                        name = 'ProDisease'
                    else:
                        name = holiday.holiday_status_id.name
                    current_leave_struct = leaves.setdefault(
                        holiday.holiday_status_id, {
                            'name': name,
                            'sequence': 5,
                            'code': name,
                            'number_of_days': 0.0,
                            'number_of_hours': 0.0,
                            'contract_id': contract.id,
                        })
                    cal = Colombia()
                    dias = [a[0] for a in cal.holidays(year=interval[0].year) if (a[0] >= interval[0].date() and a[0] <= interval[1].date())] # noqa
                    second = len(dias) * 3600
                    # leave_time = (interval[1] - interval[0]).seconds / 3600
                    leave_time = ((interval[1] - interval[0]).seconds) - timedelta(seconds=second)
                    leave_time =  leave_time/ 3600
                    current_leave_struct['number_of_hours'] += leave_time
                    work_hours = contract.employee_id.get_day_work_hours_count(
                        interval[0].date(),
                        calendar=contract.resource_calendar_id)
                    if work_hours:
                        current_leave_struct[
                            'number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(
                day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res
