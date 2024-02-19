# -*- encoding: utf-8 -*-
{
    'name': 'Odoo Login page background',
    'summary': 'The new configurable Odoo Web Login Screen',
    'version': '17.0.0.1',
    'category': 'website',
    'summary': """
    You can customised login page like add background image or color and change position of login form.
    """,
    'author': 'Livedigital Technologies Private Limited',
    'company': 'Livedigital Technologies Private Limited',
    'maintainer': 'Livedigital Technologies Private Limited',
    'website': 'https://ldtech.in',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'web', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'data/login_image.xml',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        # 'templates/assets.xml',
        'templates/left_login_template.xml',
        'templates/right_login_template.xml',
        'templates/middle_login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            "login_background/static/src/css/web_login_style.css"
        ]
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
