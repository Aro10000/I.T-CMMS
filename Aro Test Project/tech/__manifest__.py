# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tech',
    'version': '1.1',
    'sequence': 165,
    'depends': ['base', 'mail'],
    'summary': "Schedule employees' meetings",
    'description': """
This is a full-featured tech system.
========================================

It supports:
------------
    - Tech of events
    - Recurring events

If you need to manage your meetings, you should install the CRM module.
    """,
    'category': 'Productivity/Tech',
    'demo': [
        'data/tech_demo.xml'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tech_security.xml',
        'data/tech_cron.xml',
        'data/mail_template_data.xml',
        'data/tech_data.xml',
        'data/mail_activity_type_data.xml',
        'data/mail_message_subtype_data.xml',
        'views/mail_activity_views.xml',
        'views/tech_templates.xml',
        'views/tech_views.xml',
        'views/res_partner_views.xml',
        'wizard/tech_provider_config.xml'
    ],
    'installable': True,
    'application': True,
    'assets': {
        'mail.assets_messaging': [
            'tech/static/src/models/*.js',
        ],
        'web.assets_backend': [
            'tech/static/src/scss/tech.scss',
            'tech/static/src/js/base_tech.js',
            'tech/static/src/js/services/tech_notification_service.js',
            'tech/static/src/views/**/*',
            'tech/static/src/components/*/*.xml',
        ],
        'web.qunit_suite_tests': [
            'tech/static/tests/**/*',
        ],
        'web.assets_tests': [
            'tech/static/tests/tours/tech_tour.js',
        ],
    },
    'license': 'LGPL-3',
}
