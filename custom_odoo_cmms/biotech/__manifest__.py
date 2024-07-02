# -*- coding: utf-8 -*-

{
    'name': 'Biotech',
    'version': '1.0',
    'sequence': 100,
    'category': 'Manufacturing/Biotech',
    'description': """
        Track equipments and biotech requests""",
    'depends': ['mail'],
    'summary': 'Track equipment and manage biotech requests',
    'website': 'https://www.odoo.com/app/biotech',
    'data': [
        'security/biotech.xml',
        'security/ir.model.access.csv',
        'data/biotech_data.xml',
        'data/mail_alias_data.xml',
        'data/mail_activity_type_data.xml',
        'data/mail_message_subtype_data.xml',
        'views/biotech_views.xml',
        'views/mail_activity_views.xml',
        'data/biotech_cron.xml',



    ],
    #'demo': ['data/biotech_demo.xml'],
    'installable': True,
    'application': True,
    
}
