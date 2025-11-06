import time
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class IrCron(models.Model):
    _inherit = 'ir.cron'

    last_duration = fields.Float(string="Last Duration (s)", readonly=True, help="Duration of last execution in seconds")
    last_status = fields.Selection(
        [('running', 'Running'), ('success', 'Success'), ('failed', 'Failed')],
        string="Last Status", readonly=True,
    )

    def _callback(self):
        """Override to track execution time and status."""
        start = time.time()
        self.write({'last_status': 'running'})
        try:
            result = super()._callback()
            duration = time.time() - start
            self.write({
                'last_duration': duration,
                'last_status': 'success'
            })
            _logger.info("Job `%s (ID %s)` done in %.2fs [success]",
                         self.name, self.id, duration)
            return result
        except Exception as e:
            duration = time.time() - start
            self.write({
                'last_duration': duration,
                'last_status': 'failed'
            })
            _logger.warning("Job `%s (ID %s)` failed after %.2fs: %s",
                            self.name, self.id, duration, str(e))
            raise  # re-raise so Odoo handles it as usual
