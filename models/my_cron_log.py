from odoo import models, fields

class MyCronLog(models.Model):
    _name = 'my.cron.log'
    _description = 'My Cron Job Execution Log'
    _order = 'start_time desc'

    cron_id = fields.Many2one('ir.cron', string="Job ID", ondelete="cascade")
    cron_name = fields.Char(string="Job Name")
    start_time = fields.Datetime(string="Start Time", required=True)
    duration = fields.Float(string="Duration (s)")
    status = fields.Selection(
        [('success', 'Success'), ('failed', 'Failed')],
        string="Status", required=True
    )
