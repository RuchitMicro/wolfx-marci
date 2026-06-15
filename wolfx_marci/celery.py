import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()  # ← add this before anything else

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wolfx_marci.settings')

app = Celery('wolfx_marci')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    raise NotImplementedError('Debug task — prints request info.')