# -*- coding: utf-8 -*-
"""imports from python lib"""
import logging
from datetime import datetime, timedelta
"""imports from odoo"""
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

"""created a new model and added the fields"""
class AuditlogAutovacuum(models.TransientModel):
    _name = "auditlog.autovacuum"
    _description = "Auditlog - Delete old logs"

    @api.model
    def autovacuum(self, days, chunk_size=None):
        """Delete all logs older than ``days``. This includes:
            - CRUD logs (create, read, write, unlink)
            - HTTP requests
            - HTTP user sessions

        Called from a cron.
        """
        days = (days > 0) and int(days) or 0
        deadline = datetime.now() - timedelta(days=days)
        data_models = ("auditlog.log", "auditlog.http.request", "auditlog.http.session")
        for data_model in data_models:
            records = self.env[data_model].search(
                [("create_date", "<=", fields.Datetime.to_string(deadline))],
                limit=chunk_size,
                order="create_date asc",
            )
            nb_records = len(records)
            with self.env.norecompute():
                records.unlink()
            _logger.info("AUTOVACUUM - %s '%s' records deleted", nb_records, data_model)
        return True
