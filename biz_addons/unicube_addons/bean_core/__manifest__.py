{

    'name': 'Bean Core',
    'category': 'UniCube/Hidden',
    'author': "The Bean Family",
    "license": "LGPL-3",
    "sequence": 200,
    'website': "https://thebeanfamily.org",
    'version': '17.0.0.1',
    'description': """
Bean Core Web Client.
===========================

This module modifies the web addon to provide the design and responsiveness.
        """,
    'depends': ['web', 'base_setup', 'mail','portal','digest'],
    'auto_install': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_data.xml',
        'data/debrand/mail_templates_email_layouts.xml',
        'data/debrand/mail_template_data.xml',
        'reports/bizzi_view.xml',
        'views/res_config.xml',
        'views/telegram_channel_view.xml',
        'views/webclient_templates.xml',
        'views/debrand/auth_signup_templates_email.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss', 'bean_core/static/src/**/*.variables.scss'),
            (
                'before', 'web/static/src/scss/primary_variables.scss',
                'bean_core/static/src/scss/primary_variables.scss'),
            'bean_core/static/src/scss/bean_variables.scss'
        ],
        'web._assets_secondary_variables': [
            ('before', 'web/static/src/scss/secondary_variables.scss',
             'bean_core/static/src/scss/secondary_variables.scss'),
        ],
        'web._assets_backend_helpers': [
            ('before', 'web/static/src/scss/bootstrap_overridden.scss',
             'bean_core/static/src/scss/bootstrap_overridden.scss'),
        ],
        'web.assets_frontend': [
            'bean_core/static/src/webclient/home_menu/home_menu_background.scss',  # used by login page
            'bean_core/static/src/webclient/navbar/navbar.scss',
        ],
        'web.assets_backend': [
            'bean_core/static/src/webclient/**/*.scss',
            'bean_core/static/src/views/**/*.scss',

            'bean_core/static/src/core/**/*',
            'bean_core/static/src/webclient/**/*.js',
            'bean_core/static/src/webclient/**/*.xml',
            'bean_core/static/src/views/**/*.js',
            'bean_core/static/src/views/**/*.xml',

            # Add refresher
            'bean_core/static/src/web_refesher/**/*.scss',
            'bean_core/static/src/web_refesher/**/*.xml',
            'bean_core/static/src/web_refesher/**/*.js',

            # Don't include dark mode files in light mode
            ('remove', 'bean_core/static/src/**/*.dark.scss'),
        ],
        'web.assets_web': [
            ('replace', 'web/static/src/main.js', 'bean_core/static/src/main.js'),
        ],
        # ========= Dark Mode =========
        "web.dark_mode_variables": [
            # web._assets_primary_variables
            ('before', 'bean_core/static/src/scss/primary_variables.scss',
             'bean_core/static/src/scss/primary_variables.dark.scss'),
            ('before', 'bean_core/static/src/**/*.variables.scss', 'bean_core/static/src/**/*.variables.dark.scss'),
            # web._assets_secondary_variables
            ('before', 'bean_core/static/src/scss/secondary_variables.scss',
             'bean_core/static/src/scss/secondary_variables.dark.scss'),
        ],
        "web.assets_web_dark": [
            ('include', 'web.dark_mode_variables'),
            # web._assets_backend_helpers
            ('before', 'bean_core/static/src/scss/bootstrap_overridden.scss',
             'bean_core/static/src/scss/bootstrap_overridden.dark.scss'),
            ('after', 'web/static/lib/bootstrap/scss/_functions.scss',
             'bean_core/static/src/scss/bs_functions_overridden.dark.scss'),
            # assets_backend
            'bean_core/static/src/**/*.dark.scss',
        ],
        'web.tests_assets': [
            'bean_core/static/tests/*.js',
        ],
        'web.qunit_suite_tests': [
            'bean_core/static/tests/views/**/*.js',
            'bean_core/static/tests/webclient/**/*.js',
            ('remove', 'bean_core/static/tests/webclient/action_manager_mobile_tests.js'),
        ],
        'web.qunit_mobile_suite_tests': [
            'bean_core/static/tests/views/disable_patch.js',
            'bean_core/static/tests/mobile/**/*.js',
            'bean_core/static/tests/webclient/action_manager_mobile_tests.js',
        ],
    },
}
