from odoo import http
from odoo.http import request
import base64
from werkzeug.exceptions import BadRequest
import logging
_logger = logging.getLogger(__name__)


class AWBController(http.Controller):

    @http.route('/feedback',  type='http', auth='public', website=True)
    def customer_testimonial(self, **post):
        print("something")
        values = {}
        partner_id = False
        user_id = request.env.user
        if request.session.uid and user_id:
            partner_id = user_id.partner_id
        values.update({
            'name': partner_id.name if partner_id else None
        })
        return request.render("awb_customer_testimonial.customer_testimonial", values)

    def _prepare_vals(self, post, model):
        values = {}
        fields = request.env['ir.model'].sudo().search([('model', '=', model)],
                                                       limit=1).field_id
        for key, val in post.items():
            if key!='modal_name' and key!='redirect':
                field_id = fields.sudo().filtered(
                    lambda r: r.sudo().name == key).sudo()
                if not field_id:
                    continue
                if field_id.ttype == 'binary':
                    val = base64.b64encode(val.read()) if val and val != '' else False
                if field_id.ttype == 'integer':
                    val = int(val) if val else 0
                if field_id.ttype == 'many2one':
                    val = int(val) if val else False
                if field_id.ttype == "boolean":
                    val = True if val and (val == 'yes' or val == 'on' or val == 'True') else False
                if field_id.ttype == "one2many":
                    val = [(5, 0)] + [(0, 0, line) for line in val]
                if field_id.ttype == 'binary':
                    if val:
                        values.update({
                            key: val
                        })
                else:
                    values.update({
                        key: val
                    })
        return values

    @http.route('/customer_testimonial_success',  type='http', auth="user", website=True)
    def customer_testimonial_success(self, **post):
        return request.render("awb_customer_testimonial.customer_testimonial_success")

    @http.route('/submit_customer_review',  type='http', auth="user", website=True)
    def submit_customer_review(self, **post):
        if post:
            if post.get('modal_name') is not None:
                vals = self._prepare_vals(post, post['modal_name'])
                record_inserted = request.env[post['modal_name']].sudo().create(vals)
                if record_inserted:
                    if post.get('redirect') is not None:
                        return request.redirect(post.get('redirect'))
                    else:
                        _logger.warning("redirect is not defined")
                        raise BadRequest('redirect is not defined')
                else:
                    _logger.warning("There is an issue while insert")
                    raise BadRequest('There is an issue while insert')
            else:
                _logger.warning("modal_name is not defined")
                raise BadRequest('modal_name is not defined')
        else:
            raise BadRequest('post values are not available')





