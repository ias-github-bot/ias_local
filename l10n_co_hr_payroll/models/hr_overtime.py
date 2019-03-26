import pytz
import math
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = "HR Overtime"
    _inherit = ['mail.thread']

    @api.one
    def _compute_total(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_date = datetime.strptime(self.from_date, DATETIME_FORMAT)
        to_date = datetime.strptime(self.to_date, DATETIME_FORMAT)
        timedelta = to_date - from_date
        diff_day = (float(timedelta.total_seconds()) / 86400) * 24
        self.total_time = diff_day

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

    @api.onchange('from_date', 'to_date', 'employee_id')
    def onchange_from_date(self):
        day_list = []
        hour_list_from = []
        hour_list_to = []
        self.type_id = False
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.from_date:
            contract_id = self.env[
                'hr.employee'].browse(self.employee_id.id).contract_id.id
            for con in self.env['hr.contract'].browse(contract_id):
                for con_day in con.resource_calendar_id.attendance_ids:
                    day_list.append(con_day.dayofweek)
                    hour_list_from.append(con_day.hour_from)
                    hour_list_to.append(con_day.hour_to)
            request_date = datetime.strptime(
                self.from_date, DATETIME_FORMAT).date()
            request_day = request_date.weekday()
            if str(request_day) in day_list:
                contract = self.employee_id.contract_id
                structure = contract.overtime_structure_id
                rules = structure.hr_ov_structure_rule_ids
                for data in rules:
                    if data.type_id.code == "WD":
                        self.type_id = data.type_id.id
                        if structure.control_overtime_val:
                            index_list = day_list.index(str(request_day))
                            out_from_work = hour_list_to[index_list+1]
                            from_date_hour = datetime.strptime(
                                self.from_date, DATETIME_FORMAT)
                            to_date_hour = datetime.strptime(
                                self.to_date, DATETIME_FORMAT)
                            hour1, minute1 = self.float_time_convert(
                                data.begin_after)
                            hour2, minute2 = self.float_time_convert(
                                data.ends_in)
                            begin_after = from_date_hour.replace(
                                hour=hour1, minute=minute1)
                            ends_in = to_date_hour.replace(
                                hour=hour2, minute=minute2)
                            if from_date_hour.strftime('%H') >= out_from_work \
                                and from_date_hour >= begin_after \
                                    and from_date_hour <= ends_in:
                                self.type_detail_id = data.type_detail_id.id
            else:
                contract = self.employee_id.contract_id
                structure = contract.overtime_structure_id
                rules = structure.hr_ov_structure_rule_ids
                for data in rules:
                    if data.type_id.code == "WE":
                        self.type_id = data.type_id.id
                        if structure.control_overtime_val:
                            index_list = day_list.index(str(request_day))
                            out_from_work = hour_list_to[index_list+1]
                            from_date_hour = datetime.strptime(
                                self.from_date, DATETIME_FORMAT)
                            to_date_hour = datetime.strptime(
                                self.to_date, DATETIME_FORMAT)
                            hour1, minute1 = self.float_time_convert(
                                data.begin_after)
                            hour2, minute2 = self.float_time_convert(
                                data.ends_in)
                            begin_after = from_date_hour.replace(
                                hour=hour1, minute=minute1)
                            ends_in = to_date_hour.replace(
                                hour=hour2, minute=minute2)
                            if from_date_hour.strftime('%H') >= out_from_work \
                                and from_date_hour >= begin_after \
                                    and from_date_hour <= ends_in:
                                self.type_detail_id = data.type_detail_id.id

    @api.onchange('from_date', 'to_date')
    def onchange_from_day(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.from_date and self.to_date:
            from_day = datetime.strptime(
                self.from_date, DATETIME_FORMAT).strftime('%d')
            to_day = datetime.strptime(
                self.to_date, DATETIME_FORMAT).strftime('%d')
            if to_day > from_day:
                raise Warning(_(
                    'You can only select one specific day'))

    @api.onchange('type_id')
    def onchange_type(self):
        details = []
        if self.type_id:
            for type_data in self.env[
                    'hr.ov.structure.rule.type.detail'].search(
                        [('overtime_structure_type_id',
                          '=', self.type_id.id)]):
                details.append(type_data.id)
        return {'domain': {'type_detail_id': [('id', 'in', details)]}}

    name = fields.Char(
        string="Name", readonly=True, track_visibility='onchange')
    employee_id = fields.Many2one(
        'hr.employee', string="Employee",
        required=True, track_visibility='onchange')
    reason = fields.Text(string="Overtime Reason", track_visibility='onchange')
    from_date = fields.Datetime(
        srting="From Date", required=True, track_visibility='onchange')
    to_date = fields.Datetime(
        srting="To Date", required=True, track_visibility='onchange')
    actual_leave_time = fields.Datetime(
        string="Actual Leave Time", readonly=True, track_visibility='onchange')
    total_time = fields.Float(
        string="Total Time (Hours)",
        compute='_compute_total', track_visibility='onchange')
    type_id = fields.Many2one(
        'hr.ov.structure.rule.type',
        string="Type", track_visibility='onchange')
    type_detail_id = fields.Many2one(
        'hr.ov.structure.rule.type.detail', string="Type detail",
        track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('approve', 'Approved')], string="Status",
        default="draft",  track_visibility='onchange')
    cost = fields.Float(
        string="Cost", track_visibility='onchange')

    @api.onchange('type_detail_id')
    def onchange_type_detail(self):
        if self.type_detail_id:
            self.cost = self.total_time * self.type_detail_id.percent * (
                self.employee_id.timesheet_cost / 100)

    @api.model
    def create(self, values):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        values['name'] = self.env['ir.sequence'].get('hr.ov.req') or ' '
        if values['to_date'] and values['from_date']:
            if values['to_date'] < values['from_date']:
                raise Warning(_(
                    'You can not select a lower end date than the start date'))
            from_date = datetime.strptime(
                values['from_date'], DATETIME_FORMAT).strftime('%d')
            to_date = datetime.strptime(
                values['to_date'], DATETIME_FORMAT).strftime('%d')
            if to_date > from_date:
                raise Warning(_('You can only select one specific day'))
        res = super(HrOvertime, self).create(values)
        return res

    @api.multi
    def action_sumbit(self):
        return self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})

    @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})


class HrOvertimeStructure(models.Model):
    _name = "hr.overtime.structure"
    _description = "Overtime Structure"
    _inherit = ['mail.thread']

    name = fields.Char(string="Structure Name", track_visibility='onchange')
    code = fields.Char(
        string="Code", required=True, track_visibility='onchange')
    department_ids = fields.Many2many(
        'hr.department', string="Department(s)", track_visibility='onchange')
    overtime_method = fields.Selection(
        [('ov_request', 'According to Request'),
         ('ov_attendance', 'According to Attendance')],
        string="Overtime Method", required=True,
        track_visibility='onchange', default="ov_request")
    hr_ov_structure_rule_ids = fields.One2many(
        'hr.ov.structure.rule', 'hr_overtime_structure_id',
        string="Overtime Structure Line", track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('apply', 'Applied')],
        string="Status", default="draft", track_visibility='onchange')
    overtime_required = fields.Boolean('Apply all employees')
    control_overtime_val = fields.Boolean('Control overtime validation')

    @api.model
    def create(self, values):
        values['name'] = values['name'] + "( " + values['code'] + " )"
        res = super(HrOvertimeStructure, self).create(values)
        return res

    @api.one
    def apply_ov_structure(self):
        dep_list = []
        emp_list = []
        for dep in self.department_ids:
            dep_list.append(dep.id)
        employee_ids = self.env[
            'hr.employee'].search([('department_id', 'in', dep_list)])
        for emp in employee_ids:
            emp_list.append(emp.id)
        contract_ids = self.env[
            'hr.contract'].search([('employee_id', 'in', emp_list)])
        for contract in contract_ids:
            contract.write({'overtime_structure_id': self.id})
        self.write({'state': 'apply'})


class HrOvStructureRuleType(models.Model):
    _name = "hr.ov.structure.rule.type"
    _description = "Overtime Structure Rule type"
    _inherit = ['mail.thread']

    code = fields.Char(
        string="Code", required=True, track_visibility='onchange')
    name = fields.Char(
        string="Type Name", required=True, track_visibility='onchange')


class HrOvStructureRuleTypeDetail(models.Model):
    _name = "hr.ov.structure.rule.type.detail"
    _description = "Overtime Structure Rule type detail"
    _inherit = ['mail.thread']

    code = fields.Char(
        string="Code", required=True, track_visibility='onchange')
    overtime_structure_type_id = fields.Many2one(
        'hr.ov.structure.rule.type', string="Overtime type", required=True)
    name = fields.Char(
        string="Type detail name", required=True, track_visibility='onchange')
    percent = fields.Float(
        string="Charge percent", required=True, track_visibility='onchange')

class HrOvStructureRule(models.Model):
    _name = "hr.ov.structure.rule"
    _description = "Overtime Structure Rule"
    _inherit = ['mail.thread']

    @api.onchange('type_id')
    def onchange_type(self):
        details = []
        if self.type_id:
            for type_data in self.env[
                    'hr.ov.structure.rule.type.detail'].search(
                        [('overtime_structure_type_id',
                          '=', self.type_id.id)]):
                details.append(type_data.id)
        return {'domain': {'type_detail_id': [('id', 'in', details)]}}

    @api.onchange('type_detail_id')
    def onchange_type_detail(self):
        if self.type_detail_id:
            self.rate = self.type_detail_id.percent

    type_id = fields.Many2one('hr.ov.structure.rule.type', string="Type")
    type_detail_id = fields.Many2one(
        'hr.ov.structure.rule.type.detail', string="Type detail")
    rate = fields.Float(
        string="Rate (%)", required=True, track_visibility='onchange')
    max_per_day = fields.Integer(string="Max. hour per day")
    begin_after = fields.Float(string="Begin After")
    ends_in = fields.Float(string="Ends in")
    hr_overtime_structure_id = fields.Many2one(
        'hr.overtime.structure',
        string="Overtime Structure Ref.", ondelete='cascade',
        track_visibility='onchange')
