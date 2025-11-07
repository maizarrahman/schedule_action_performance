# -*- coding: utf-8 -*-
from odoo import models, fields

class MyCronLog(models.Model):
    _name = 'my.cron.log'
    _description = 'My Cron Job Execution Log'
    _order = 'start_time desc'

    cron_id = fields.Many2one('ir.cron', string="Job ID", ondelete="cascade", readonly=True)
    cron_name = fields.Char(string="Job Name", readonly=True)
    start_time = fields.Datetime(string="Start Time", readonly=True)
    duration = fields.Float(string="Duration (s)", readonly=True)
    status = fields.Selection(
        [('success', 'Success'), ('failed', 'Failed')],
        string="Status", readonly=True
    )
    error_message = fields.Text(string="Error Message", readonly=True)
    avg_duration = fields.Float(string="Average Duration (s)", group_operator="avg", readonly=True)
    max_duration = fields.Float(string="Maximum Duration (s)", group_operator="max", readonly=True)
    min_duration = fields.Float(string="Minimum Duration (s)", group_operator="min", readonly=True)