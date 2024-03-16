# -*- coding: utf-8 -*-
{
    'name': "UniCube's VietQR Payment Method for website with callback supported by TIMO (A digital bank)",

    'summary': "UniCube's VietQR Payment Method for website with callback supported by TIMO (A digital bank)",

    'description': """
        - This addon will change the classic bank transfer module to UniCube's VietQR Payment Method for website.  
        - More than that, the module will create an IPN gateway to listen the callback from TIMO which provide the payment
        status for completing the order's payment
    """,

    'author': "UniCube",
    "license": 'OPL-1',
    'category': 'UniCube/Localization',
    "sequence": 200,
    'version': '17.0.0.2',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,
    'price': 50.00,
    'currency': 'USD',

    "images": ["static/description/image.gif"],

    # any module necessary for this one to work correctly
    'depends': ['unicubevn_bank', 'unicubevn_ipn', 'payment_custom', 'website_sale'],

    'data': [
        'views/payment_custom_templates.xml',
        'views/payment_confirm_page.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',  # Depends on `payment_method_wire_transfer`.
        'data/res_config_settings.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'unicubevn_payment/static/src/**/*',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
