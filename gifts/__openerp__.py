# -*- encoding: utf-8 -*-

{
    'name': 'Gifts',
    'version': '1.0',
    'author': 'Damien Bouvy',
    'category': 'Gifts',
    'website': 'https://www.damienbouvy.be',
    'summary': 'Gift Lists management',
    'depends': ['web', 'mail', 'website'],
    'description': """
Gift Lists management
==============================================
Yo man!
""",
    "data": [
        "data/gift_data.xml",
        "views/gift_gift_views.xml",
        "views/gift_gift_templates.xml",
        "data/ir.model.access.csv",
        "data/gift_security.xml",
        "report/gift_followup_report.xml",
        "report/gift_followup_templates.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
