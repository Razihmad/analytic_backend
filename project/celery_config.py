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
)

task_routes = {
    "amazon.tasks.testing_tasks": {
        "queue": "process_report",
        "routing_key": "report",
    },
}
