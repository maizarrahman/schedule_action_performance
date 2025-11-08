# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class MyCronLog(osv.osv):
    _name = 'my.cron.log'
    _description = 'My Cron Job Execution Log'
    _order = 'start_time desc'

    _columns = {
        'cron_id': fields.many2one('ir.cron', "Job ID", ondelete="cascade", readonly=True),
        'cron_name': fields.char("Job Name", readonly=True),
        'start_time': fields.datetime("Start Time", readonly=True),
        'duration': fields.float("Duration (s)", readonly=True),
        'status': fields.selection(
            [('success', 'Success'), ('failed', 'Failed')],
            "Status", readonly=True
        ),
        'error_message': fields.text("Error Message", readonly=True),
        'avg_duration': fields.float("Average Duration (s)", group_operator="avg", readonly=True),
        'max_duration': fields.float("Maximum Duration (s)", group_operator="max", readonly=True),
        'min_duration': fields.float("Minimum Duration (s)", group_operator="min", readonly=True),
    }