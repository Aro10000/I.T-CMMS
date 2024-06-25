# -*- coding: utf-8 -*-

{
    'name': 'I.T Help Desk',
    'version': '1.0',
    'sequence': 2,
    'category': 'Manufacturing/ICT',
    'description': """
        Track equipments and ict requests""",
    'depends': ['mail'],
    'summary': 'Track equipment and manage ict requests',
    'website': 'https://www.odoo.com/app/ict',
    'data': [
        'security/ict.xml',
        'security/ir.model.access.csv',
        'data/ict_data.xml',
        'data/mail_alias_data.xml',
        'data/mail_activity_type_data.xml',
        'data/mail_message_subtype_data.xml',
        'views/ict_views.xml',
        'views/mail_activity_views.xml',
        'data/ict_cron.xml',
    ],
    'demo': ['data/ict_demo.xml'],
    'installable': True,
    'application': True,
    
}
