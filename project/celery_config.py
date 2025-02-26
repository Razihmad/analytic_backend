from kombu import Exchange, Queue

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
}
