# -*- coding: utf-8 -*-
import time
import logging
import pytz
from odoo import models, fields, api
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}

class IrCron(models.Model):
    _inherit = 'ir.cron'

    last_duration = fields.Float(string="Last Duration (s)", readonly=True, 
        help="Duration of last execution in seconds")
    last_status = fields.Selection(
        [('success', 'Success'), ('failed', 'Failed')],
        string="Last Status", readonly=True,
        help="Status of last execution"
    )

    def button_show_logs(self):
        return {
            'name': 'Logs',
            'type': 'ir.actions.act_window',
            'res_model': 'my.cron.log',
            'view_mode': 'tree,form',
            'domain': [('cron_id', '=', self.id)],
            'context': {'search_default_groupby_cron_name': 1},
        }

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        start_time = time.time()
        try:
            with api.Environment.manage():
                cron = api.Environment(job_cr, job['user_id'], {
                    'lastcall': fields.Datetime.from_string(job['lastcall'])
                })[cls._name]
                now = fields.Datetime.context_timestamp(cron, datetime.now())
                nextcall = fields.Datetime.context_timestamp(cron, fields.Datetime.from_string(job['nextcall']))
                numbercall = job['numbercall']
                utc_now = fields.Datetime.to_string(now.astimezone(pytz.UTC)),
                ok = False
                while nextcall < now and numbercall:
                    if numbercall > 0:
                        numbercall -= 1
                    if not ok or job['doall']:
                        cron._callback(job['cron_name'], job['ir_actions_server_id'], job['id'])
                    if numbercall:
                        nextcall += _intervalTypes[job['interval_type']](job['interval_number'])
                    ok = True
                addsql = ''
                if not numbercall:
                    addsql = ', active=False'
                end_time = time.time()
                duration = end_time - start_time
                cron_cr.execute("UPDATE ir_cron SET nextcall=%s, numbercall=%s, lastcall=%s, last_duration=%s, last_status=%s" + addsql + " WHERE id=%s", (
                    fields.Datetime.to_string(nextcall.astimezone(pytz.UTC)),
                    numbercall,
                    fields.Datetime.to_string(now.astimezone(pytz.UTC)),
                    duration,
                    'success',
                    job['id']
                ))
                cron_cr.execute("INSERT INTO my_cron_log (cron_id, cron_name, start_time, duration, status, avg_duration, max_duration, min_duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (
                        job['id'],
                        job['cron_name'],
                        utc_now,
                        duration,
                        'success',
                        duration,
                        duration,
                        duration
                    ))
                cron.flush()
                cron.invalidate_cache()
        except Exception as e:
            cron_cr.execute("UPDATE ir_cron SET last_status='failed' WHERE id=%s", (job['id'],))
            cron_cr.execute("INSERT INTO my_cron_log (cron_id, cron_name, start_time, status, error_message) VALUES (%s, %s, %s, %s, %s)", 
                (
                    job['id'],
                    job['cron_name'],
                    utc_now,
                    'failed',
                    str(e),
                ))
        finally:
            job_cr.commit()
            cron_cr.commit()
