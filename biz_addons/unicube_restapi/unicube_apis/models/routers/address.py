

def get_country_state(env,country_id = 241):
    _data = env['res.country.state'].sudo().search([('country_id','=',country_id)])
    state_data = []
    for item in _data:
        state_data.append({
            'state_id': item.id,
            'state_name': item.name
        })
    return state_data


def get_country_district(env,state_id):
    _data = env['res.country.district'].sudo().search([('state_id','=',state_id)])
    district_data = []
    for item in _data:
        district_data.append({
            'district_id': item.id,
            'district_name': item.name
        })
    return district_data

def get_country_ward(env,district_id):
    _data = env['res.country.ward'].sudo().search([('district_id','=',district_id)])
    ward_data = []
    for item in _data:
        ward_data.append({
            'ward_id': item.id,
            'ward_name': item.name
        })
    return ward_data
