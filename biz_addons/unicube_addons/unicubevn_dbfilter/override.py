# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import http
from odoo.http import request
from odoo.tools import config

db_filter_org = http.db_filter


# def db_filter(dbs, httprequest=None):
#     print("dbs: %s - httprequest: %s" % (dbs, httprequest))
#     dbs = db_filter_org(dbs, httprequest)
#     httprequest = httprequest or http.request.httprequest
#     db_filter_hdr = httprequest.environ.get("HTTP_X_DBFILTER")
#     if db_filter_hdr:
#         dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
#     return dbs

def db_filter(dbs, host=None):
    """
    This is the override function for db_filter function

    This add priority rule that checking if the HTTP_X_DBFILTER value is exist,
    it will return the database list that match with HTTP_X_DBFILTER value
    Otherwise use the origin flow

    Return the subset of ``dbs`` that match the dbfilter or the dbname
    server configuration. In case neither are configured, return ``dbs``
    as-is.

    :param Iterable[str] dbs: The list of database names to filter.
    :param host: The Host used to replace %h and %d in the dbfilters
        regexp. Taken from the current request when omitted.
    :returns: The original list filtered.
    :rtype: List[str]
    """
    # custom
    db_filter_hdr = request.httprequest.environ.get('HTTP_X_DBFILTER')
    _logger.info("Database filter key: %s" % db_filter_hdr)
    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
        return dbs

    if config['dbfilter']:
        #        host
        #     -----------
        # www.example.com:80
        #     -------
        #     domain
        if host is None:
            host = request.httprequest.environ.get('HTTP_HOST', '')
        host = host.partition(':')[0]
        if host.startswith('www.'):
            host = host[4:]
        domain = host.partition('.')[0]

        dbfilter_re = re.compile(
            config["dbfilter"].replace("%h", re.escape(host))
            .replace("%d", re.escape(domain)))
        return [db for db in dbs if dbfilter_re.match(db)]

    if config['db_name']:
        # In case --db-filter is not provided and --database is passed, Odoo will
        # use the value of --database as a comma separated list of exposed databases.
        exposed_dbs = {db.strip() for db in config['db_name'].split(',')}
        return sorted(exposed_dbs.intersection(dbs))

    return list(dbs)


if config.get("proxy_mode") and "unicubevn_dbfilter" in config.get("server_wide_modules"):
    _logger = logging.getLogger(__name__)
    _logger.info("The UniCube database filter by header is running...")
    http.db_filter = db_filter
