# -*- coding: utf-8 -*-
import json
import logging
import sys
from odoo import http
from odoo.tools import config

if sys.version_info > (3,):
    import _pickle as cPickle

    unicode = str
else:
    import cPickle




try:
    from redis.client import Redis
    # import redis
    print("Redis package is installed")
except ImportError:
    print("Redis package is not installed")



_logger = logging.getLogger(__name__)

ADDRESS_CACHE_KEY = "unicubevn_addess"
SESSION_TIMEOUT = 60 * 60 * 24 * 30  # 30 days in seconds

# def check_python_package_installed( package_name):
#     try:
#         __import__(package_name)
#         _logger.info(f"Python {package_name} package is installed")
#         return True
#     except ImportError:
#         _logger.info(f"Python {package_name} package is not installed")
#         return False

class AddressController(http.Controller):

    def __init__(self):
        self.redis_client = None
        try:
            if (config.get('enable_redis') or config.get('enable_redis') == True):
                self.redis_client = Redis(host=config.get('redis_host'),
                                          port=int(config.get('redis_port')),
                                          db=int(config.get('redis_dbindex', 1)),
                                          password=config.get('redis_pass', None))
        except:
            pass
    @http.route(["/address_template/<int:country_id>"], type="json", auth='public', csrf=False)
    def address_template(self, country_id, **kw):
        _logger.info(f"state_id ----- {country_id}")
        """
            Check if the http.Stream.redis_client is existing and have address cache data, return address cache data
            Otherwise return calculated address data
        """
        _logger.info(self.redis_client)
        if self.redis_client:
            _logger.info("Run API with redis")

            address_cache = self.redis_client.get(ADDRESS_CACHE_KEY)
            if address_cache:
                return json.dumps(cPickle.loads(address_cache))
            else:
                response_data = self._generate_address_data(country_id)
                self.redis_client.setex(name=ADDRESS_CACHE_KEY, value=cPickle.dumps(response_data),
                                   time=SESSION_TIMEOUT)
                _logger.debug(f"{type(response_data)} - data:\n {response_data}")
                return json.dumps(response_data)
        else:
            _logger.info("Run API without redis")
            response_data = self._generate_address_data(country_id)
            _logger.debug(f"{type(response_data)} - data:\n {response_data}")
            return json.dumps(response_data)

    def _generate_address_data(self, country_id):
        _wards = http.request.env["res.country.ward"]
        _districts = http.request.env["res.country.district"]
        _states = http.request.env["res.country.state"]
        _country = http.request.env["res.country"]
        districts = _districts.sudo().search([('country_id', '=', country_id)])
        ward = _wards.sudo().search([('country_id', '=', country_id)])
        states = _states.sudo().search([('country_id', '=', country_id)])
        country = _country.sudo().search([])
        return dict(
            ward=[{"id": w.id, "value": w.name, "code": w.code, "district_id": w.district_id.id} for w in ward],
            district=[{"id": d.id, "value": d.name, "code": d.code, "state_id": d.state_id.id}
                      for d in districts],
            state=[{"id": s.id, "value": s.name, "code": s.code, "country_id": s.country_id.id} for s in states],
            country=[{"id": c.id, "value": c.name, "code": c.code, "phone_code": c.phone_code,
                      "fields": c.get_address_fields(), "zip_required": c.zip_required,
                      "state_required": c.state_required, } for c in country]
        )
