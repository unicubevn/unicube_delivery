import logging
import json
from odoo.addons.web.controllers.report import ReportController
from odoo.http import content_disposition, request,route
_logger = logging.getLogger(__name__)
import werkzeug.exceptions

class ReportController(ReportController):
    #------------------------------------------------------
    # Report controllers
    #------------------------------------------------------
    @route([
        '/report_api/<converter>/<reportname>',
        '/report_api/<converter>/<reportname>/<docids>',
    ], type='http', auth='none', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report'].sudo()
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',') if i.isdigit()]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            data['context'] = json.loads(data['context'])
            context.update(data['context'])
        if converter == 'html':
            html = report.with_context(context)._render_qweb_html(reportname, docids, data=data)[0]
            return request.make_response(html)
        elif converter == 'pdf':
            print('-------converter == pdf---')
            pdf = report.with_context(context)._render_qweb_pdf(reportname, docids, data=data)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        elif converter == 'text':
            text = report.with_context(context)._render_qweb_text(reportname, docids, data=data)[0]
            texthttpheaders = [('Content-Type', 'text/plain'), ('Content-Length', len(text))]
            return request.make_response(text, headers=texthttpheaders)
        else:
            raise werkzeug.exceptions.HTTPException(description='Converter %s not implemented.' % converter)