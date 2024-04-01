
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
            # 'contact_address_complete': contact_info.get('contact_address_complete'),
            'type': 'contact',
            'active': contact_info.get('active'),
            'is_company': False
        })
        if result:
            return True
        return False
    
    except Exception as e:
        _logger(e)

def handle_get_contact(env, store_id, phone):
    contact_info = env['res.partner'].sudo().search([
        ('store_id','=',store_id),('phone','=',phone)
    ])
    if not contact_info:
        return {}
    return {
        'id': contact_info.id,
        'name': contact_info.name,
        'phone': contact_info.phone,
        'contact_address_complete': contact_info.contact_address_complete
    }


def handle_get_contact_by_store(env, store_id, pageIndex, pageSize):

    contact_info = env['res.partner'].sudo().search([('store_id','=',store_id)], offset=(pageIndex - 1) * pageSize, limit=pageSize)
    total = env['res.partner'].sudo().search_count([('store_id','=',store_id)])

    contact_data = []

    if not contact_info:
        return contact_data
    
    for item in contact_info:
        contact_data.append({
            'id': item.id,
            'name': item.name,
            'phone': item.phone,
            'street': item.street,
            'street2': item.street2,
            'city': item.city,
            'email': item.email,
            'contact_address_complete': item.contact_address_complete,
            'create_date': item.create_date.timestamp(),
            'store_id': item.store_id.id
        })

    return contact_data, total
