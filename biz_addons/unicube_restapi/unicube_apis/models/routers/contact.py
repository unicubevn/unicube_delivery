
from .handlerespon import make_response
import logging

_logger = logging.getLogger(__name__)

def handle_create_conract(env, contact_info):
    try: 
        result = env['res.partner'].sudo().create({
            'name': contact_info.get('name'),
            'company_id': contact_info.get('company_id'),
            'country_id': contact_info.get('country_id'),
            'state_id': contact_info.get('state_id'),

            'phone': contact_info.get('phone'),
            'mobile': contact_info.get('mobile'),
            'district_id': contact_info.get('district_id'),
            'ward_id': contact_info.get('ward_id'),

            'street': contact_info.get('street'),
            'street2': contact_info.get('street2'),
            'city': contact_info.get('city'),
            
            'store_id': contact_info.get('store_id'),
            'account_type': contact_info.get('account_type'),
            'contact_address_complete': contact_info.get('contact_address_complete'),
            'type': 'contact',

        })
        if result:
            return True
        return False
    
    except Exception as e:
        _logger(e)
    