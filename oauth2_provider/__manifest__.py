# -*- coding: utf-8 -*-

{
    'name': 'OAuth2 Provider',
    'version': '1.0',
    'category': 'Technical',
    'summary': 'OAuth2 Provider Server',
    'description': """
OAuth2 Provider
===============

This module implements the oauthlib python library for Odoo and fully support the
OAuth2 standard.

    """,
    'author': 'Damien Bouvy',
    'website': 'http://www.bouvyd.be',
    'depends': [
        'base',
    ],
    'data': [
        'views/oauth_client_views.xml',
        'views/oauth_token_views.xml',
        'views/res_config_views.xml',
        'views/menuitems.xml',
    ],
    'installable': True,
    'application': False,
}
