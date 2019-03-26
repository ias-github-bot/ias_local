
from __future__ import division
from odoo import models, fields


class HrAttendanceReporting(models.TransientModel):
    _name = "hr.attendance.reporting"
    _description = "HR  Attendance Report Wizard"

    attandance_report_id = fields.Many2one('ir.actions.report', required=True, string="Report Name",
                                           domain=[('model', '=', 'hr.attendance')])

    employee_id = fields.Many2one('hr.employee', required=True, string="Employee")

    date_from = fields.Date(string="From", required=True)

    date_to = fields.Date(string="To", required=True, default=fields.date.today())

    def action_print(self):
        res = {}
        for wizard in self:
            report_name = wizard.attandance_report_id.report_name
            datas = {
                'ids': self.env['hr.attendance'].search([
                            ('employee_id.name', '=', wizard.employee_id.name),
                            ('check_in', '>=', wizard.date_from),
                            ('check_out', '<', wizard.date_to)], order="check_in"),
                'model': 'hr.attendance',
                'form': self.read()}
            res = {
                'type': 'ir.actions.report',
                'report_name': report_name,
                'data': datas,
                'context': self.env.context,
            }
        return res
