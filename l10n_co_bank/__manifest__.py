# -*- coding: utf-8 -*-
# Ingeniería, Aplicaciones y Software S.A.S
# Copyright (C) 2003-2018 Tiny SPRL (<http://www.ias.com.co>).


{
    'name': 'Añade el tipo de cuenta del banco en el formulario',
    'version': '2.0',
    'author': 'IAS Ingenieria, Aplicaciones y Software, S.A.S',
    'website': 'http://www.ias.com.co',
    'license': 'AGPL-3',
    'category': 'Bank account modifications',
    'sequence': 10,
    'summary': 'Bank account modifications',
    'depends': ['base'],
    'description': """Añade el tipo de cuenta del banco en el formulario""",
    'data': [
        'views/res_partner_bank.xml',
        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
