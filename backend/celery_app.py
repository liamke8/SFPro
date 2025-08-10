import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
# This is not Django, but Celery uses a similar concept.
# We will define the broker URL from an environment variable.
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.tasks"],
)

# Optional configuration, see the Celery documentation for more options.
celery_app.conf.update(
    result_expires=3600,
)

if __name__ == "__main__":
    celery_app.start()
