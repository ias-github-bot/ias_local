# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingeniería, Aplicaciones y Software S.A.S
#    Copyright (C) 2003-2018 Tiny SPRL (<http://www.ias.com.co>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "HR Employee Colombia modifications",
    'version': '1.1',
    'category': 'HR',
    'sequence': 10,
    'summary': 'HR',
    'author': 'IAS Ingenieria, Aplicaciones y Software, S.A.S',
    'website': 'www.ias.com.co',
    'depends': [
        'base', 'hr', 'hr_contract', 'project', 'l10n_co_topology', 'survey'
    ],
    'external_dependencies': {
        'python': ['dateutil'],
    },    
    'description':
    """
        HR module modification

        - Add model to languages.
        - Add model to children and family.
        - Add field to show emergency contacts.
        - Add field to calculate age employee.
        - Add field to specify the employee work location.
        - Add field to specify the employee project.
        - Add model to specify the employee skills.
        - Add models to specify the employee experience.
        - Add fields to specify the employee seniority.
        - Add model to specify the employee departament transfer.
        - Add report to get and print the employee resume.
        - Add model to employee infractions.
        - Add model to employee trainings and orientations.
    """,
    'data': [
        'security/ir.model.access.csv',

        'data/ir_cron.xml',
        'data/mail_message_subtype.xml',
        'data/hr_departament.xml',
        'data/hr_contract_type.xml',
        "data/mail_template.xml",
        "data/ir_sequence.xml",
        'data/hr_infraction_category.xml',
        'data/hr_employee.xml',

        'wizards/views/hr_action.xml',

        'reports/layouts.xml',
        'reports/report_resume.xml',

        'views/hr_security.xml',
        'views/hr_language.xml',
        'views/hr_skill.xml',
        'views/hr_employee.xml',
        'views/hr_employee.xml',
        'views/hr_employee_children.xml',
        'views/project_project.xml',
        'views/hr_academic.xml',
        'views/hr_certification.xml',
        'views/hr_departament_transfer.xml',
        'views/hr_infractions.xml',
        "views/hr_orientation_checklist_line.xml",
        "views/hr_orientation_checklist.xml",
        "views/hr_orientation_checklist_request.xml",
        'views/hr_employee_training.xml',
        'views/res_partner.xml',
        'views/hr_type_of_contributor.xml',
        'views/hr_medical_exams.xml',
        'views/survey.xml',
        'views/hr_contract.xml',
        'views/res_company.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}