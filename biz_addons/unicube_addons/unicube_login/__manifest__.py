# -*- encoding: utf-8 -*-
{
    'name': 'UniCube JSC Customize Login',
    'summary': 'Customize Web Login Screen',
    'version': '17.0.0.1',
    'category': 'website',
    'summary': """
    You can customised login page like add background image, menu component or color and change position of login form.
    """,
    'author': 'UniCube JSC',
    'company': 'UniCube JSC',
    'maintainer': 'UniCube JSC',
    'website': 'https://unicube.vn',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'web', 'auth_signup', 'bean_core'],
    'auto_install': ['bean_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/login.image.csv',
        'data/ir.config_parameter.csv',
        'data/login_image.xml',
        'data/res_config_settings.xml',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        # 'templates/assets.xml',
        'templates/left_login_template.xml',
        'templates/right_login_template.xml',
        'templates/middle_login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            "unicube_login/static/src/css/unicube_login_style.css"
        ]
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
