{
    "name": "Schedule Action Performance",
    "summary": "Track execution time and succesfulness of each ir.cron job",
    "version": "13.0.1.0.0",
    "author": "Maizar, ChatGPT",
    "category": "Technical",
    "depends": ["base"],
    "installable": True,
    "application": False,

    'data': [
        'security/ir.model.access.csv',
        'views/ir_cron_views.xml',
        'views/my_cron_log_views.xml',
    ],
}
