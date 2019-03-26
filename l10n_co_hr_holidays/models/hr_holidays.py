# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLeave(models.Model):
    _inherit = "hr.holidays"

    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")
    holiday_status_type = fields.Selection([
        ('GD', "General disease"),
        ('PD', "Professional disease"),
    ], string="Types of Disease")
    payed = fields.Boolean("Already payed")
