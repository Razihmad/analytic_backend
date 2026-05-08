from kombu import Exchange, Queue
from celery.schedules import crontab

task_default_queue = "default"
task_default_exchange = "default"
task_default_exchange_type = "direct"
task_default_routing_key = "default"
task_queue_max_priority = 5

task_queues = (
    Queue(
        "process_report",
        Exchange("process_report", type="direct"),
        routing_key="report",
    ),
    Queue(
        "process_ads_report",
        Exchange("process_ads_report", type="direct"),
        routing_key="ads_report",
    ),
)

task_routes = {
    "amazon.tasks.testing_tasks": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.fetch_seller_central_report_data_by_date": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.get_report_and_process_data": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.process_report_document": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.fetch_sales_report_by_date_range": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.run_user_sales_report_for_date_minus_2": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.get_report_and_process_data_task": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon.tasks.create_sale_and_traffic_report": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon_ads.tasks.start_tasks_to_check_report_status": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon_ads.tasks.download_file_and_process_report_data": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon_ads.tasks.start_fetching_amazon_ads_campaign_by_date_range": {
        "queue": "process_report",
        "routing_key": "report",
    },
    "amazon_ads.tasks.create_ads_campaign_data_report_by_date": {
        "queue": "process_report",
        "routing_key": "report",
    }
}


beat_tasks = {
    "run-user-1-sales-report-date-minus-2-daily": {
        "task": "amazon.tasks.run_user_sales_report_for_date_minus_2",
        "schedule": crontab(hour=7, minute=30),
        "kwargs": {"user_id": 2},
    },
}
