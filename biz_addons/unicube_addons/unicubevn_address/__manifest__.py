{
    'name': "Utilities: Vietnamese Address based on Circular No 124/2004/QĐ-TTg issued by Viet Nam Government (for backend sites only)",

    'summary': """
        This is the Vietnamese address module based on Circular No 124/2004/QĐ-TTg issued by Viet Nam Government (for backend sites only)
            """,

    'description': """
        This is the Vietnamese address module based on Circular No 124/2004/QĐ-TTg issued by Viet Nam Government (for backend sites only)
    """,

    'author': "UniCube",
    "license": "LGPL-3",
    'category': 'UniCube/Localization',
    'version': '17.0.0.1',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,
    "images": ["static/description/image.jpeg"],

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_district.xml',
        'views/res_ward.xml',
        'views/res_company_info.xml',
        'data/res.country.state.xml',
        'data/res.country.district.csv',
        'data/res.country.ward.csv',
        'menus/res_address_menu.xml',
    ],

}
