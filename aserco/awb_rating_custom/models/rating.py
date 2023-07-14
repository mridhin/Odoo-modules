# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.modules.module import get_resource_path
import base64

RATING_LIMIT_SATISFIED = 5
RATING_LIMIT_SOMEWHAT_SATISFIED = 4
RATING_LIMIT_OK = 3
RATING_LIMIT__SOMEWHAT_OK = 2
RATING_LIMIT_MIN = 1


class Rating(models.Model):
    _inherit = 'rating.rating'

    rating_done = fields.Boolean(default=False)

    def _get_rating_image_filename(self):
        self.ensure_one()
        if self.rating >= RATING_LIMIT_SATISFIED:
            rating_int = 5
        elif self.rating >= RATING_LIMIT_SOMEWHAT_SATISFIED:
            rating_int = 4
        elif self.rating >= RATING_LIMIT_OK:
            rating_int = 3
        elif self.rating >= RATING_LIMIT__SOMEWHAT_OK:
            rating_int = 2
        elif self.rating >= RATING_LIMIT_MIN:
            rating_int = 1
        else:
            rating_int = 0
        return 'rating_%s.png' % rating_int

    def _compute_rating_image(self):
        for rating in self:
            try:
                image_path = get_resource_path('awb_rating_custom', 'static/src/img', rating._get_rating_image_filename())
                rating.rating_image = base64.b64encode(open(image_path, 'rb').read()) if image_path else False
            except (IOError, OSError):
                rating.rating_image = False
