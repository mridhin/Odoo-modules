# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BlogPost(models.Model):
    _inherit = 'blog.post'

    blog_image = fields.Binary(string='Blog Image', attachment=True)

