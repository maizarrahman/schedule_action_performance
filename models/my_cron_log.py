# -*- coding: utf-8 -*-
from odoo import models, fields, api

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
    error_message = fields.Text(string="Error Message")
    avg_duration = fields.Float(string="Average Duration (s)", compute='_copy_duration', group_operator="avg", store=True)
    max_duration = fields.Float(string="Maximum Duration (s)", compute='_copy_duration', group_operator="max", store=True)
    min_duration = fields.Float(string="Minimum Duration (s)", compute='_copy_duration', group_operator="min", store=True)

    @api.depends('duration')
    def _copy_duration(self):
        for rec in self:
            rec.avg_duration = rec.duration
            rec.max_duration = rec.duration
            rec.min_duration = rec.duration