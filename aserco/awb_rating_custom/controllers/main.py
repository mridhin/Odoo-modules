# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools.misc import get_lang
from odoo.addons.rating.controllers.main import Rating


class Rating(Rating):
    @http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
    def action_open_rating(self, token, rate, **kwargs):
        assert rate in (1, 2, 3, 4, 5), "Incorrect rating"
        rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        lang = rating.partner_id.lang or get_lang(request.env).code
        if rating.rating_done:
            return request.env['ir.ui.view'].with_context(lang=lang)._render_template(
                'rating.rating_external_page_view', {
                    'web_base_url': rating.get_base_url(),
                    'rating': rating,
                })
        rate_names = {
            1: _("Dissatisfied"),
            2: _("Somewhat Okay"),
            3: _("Okay"),
            4: _('Somewhat Satisfied'),
            5: _("Satisfied"),
        }
        rating.write({'rating': rate, 'consumed': True})
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('awb_rating_custom.rating_external_page_submit', {
            'rating': rating, 'token': token,
            'rate_names': rate_names, 'rate': rate
        })

    @http.route(['/rate/<string:token>/submit_feedback'], type="http", auth="public", methods=['post', 'get'], website=True)
    def action_submit_rating(self, token, **kwargs):
        rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        for rec in rating:
            rec.rating_done = True
        if request.httprequest.method == "POST":
            rate = int(kwargs.get('rate'))
            assert rate in (1, 2, 3, 4, 5), "Incorrect rating"
            record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
            record_sudo.rating_apply(rate, token=token, feedback=kwargs.get('feedback'))
        lang = rating.partner_id.lang or get_lang(request.env).code
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('rating.rating_external_page_view', {
            'web_base_url': rating.get_base_url(),
            'rating': rating,
        })
