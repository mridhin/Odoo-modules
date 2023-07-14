import logging
from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GitlabController(http.Controller):

    @http.route('/issue', type='json', auth='public')
    def get_project_issue(self, **kwargs):
        data = request.jsonrequest
        request.env['gitlab.connector'].sudo().update_gitlab_issue_webhook(data)
