# -*- coding: utf-8 -*-
# Ingeniería, Aplicaciones y Software S.A.S

{
    'name': 'HR Holidays Localization Colombia',
    'version': '11.0.0.0.1',
    'category': 'Human Resources',
    'sequence': 10,
    'summary': 'Colombia - Human Resources',
    'author': 'IAS Ingenieria, Aplicaciones y Software, S.A.S',
    'website': 'http://www.ias.com.co',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
        'hr_payroll',
    ],
    'description': """HR Holidays Localization Colombia""",
    'data': [
        'views/hr_holidays_view.xml',
        'views/hr_payslip_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'workalendar',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
