# -*- coding: utf-8 -*-
import time
import logging
import pytz
from openerp.osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

_intervalTypes = {
    'work_days': lambda interval: relativedelta(days=interval),
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}

class IrCron(osv.osv):
    _inherit = 'ir.cron'

    _columns = {
        'last_duration': fields.float("Last Duration (s)", readonly=True, 
            help="Duration of last execution in seconds"),
        'last_status': fields.selection(
            [('success', 'Success'), ('failed', 'Failed')],
            "Last Status", readonly=True,
            help="Status of last execution"
        ),
    }

    def button_show_logs(self, cr, uid, ids, context=None):
        return {
            'name': 'Logs',
            'type': 'ir.actions.act_window',
            'res_model': 'my.cron.log',
            'view_mode': 'tree,form',
            'domain': [('cron_id', 'in', ids)],
            'context': {'search_default_groupby_cron_name': 1},
        }

    def _process_job(self, job_cr, job, cron_cr):
        start_time = time.time()
        try:
            with api.Environment.manage():
                now = fields.datetime.context_timestamp(job_cr, job['user_id'], datetime.now())
                nextcall = fields.datetime.context_timestamp(job_cr, job['user_id'], datetime.strptime(job['nextcall'], DEFAULT_SERVER_DATETIME_FORMAT))
                numbercall = job['numbercall']

                ok = False
                while nextcall < now and numbercall:
                    if numbercall > 0:
                        numbercall -= 1
                    if not ok or job['doall']:
                        self._callback(job_cr, job['user_id'], job['model'], job['function'], job['args'], job['id'])
                    if numbercall:
                        nextcall += _intervalTypes[job['interval_type']](job['interval_number'])
                    ok = True
                addsql = ''
                if not numbercall:
                    addsql = ', active=False'
                end_time = time.time()
                duration = end_time - start_time
                cron_cr.execute("UPDATE ir_cron SET nextcall=%s, numbercall=%s, last_duration=%s, last_status=%s" + addsql + " WHERE id=%s", (
                    nextcall.astimezone(pytz.UTC).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    numbercall,
                    duration,
                    'success',
                    job['id']
                ))
                cron_cr.execute("INSERT INTO my_cron_log (cron_id, cron_name, start_time, duration, status, avg_duration, max_duration, min_duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (
                        job['id'],
                        job['name'],
                        now.astimezone(pytz.UTC).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        duration,
                        'success',
                        duration,
                        duration,
                        duration
                    ))
                self.invalidate_cache(job_cr, SUPERUSER_ID)
        except Exception as e:
            cron_cr.execute("UPDATE ir_cron SET last_status='failed' WHERE id=%s", (job['id'],))
            cron_cr.execute("INSERT INTO my_cron_log (cron_id, cron_name, start_time, status, error_message) VALUES (%s, %s, %s, %s, %s)", 
                (
                    job['id'],
                    job['name'],
                    now.astimezone(pytz.UTC).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'failed',
                    str(e),
                ))
        finally:
            job_cr.commit()
            cron_cr.commit()
