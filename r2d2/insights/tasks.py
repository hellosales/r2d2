from constance import config

from r2d2.celery import app
from r2d2.emails.send import send_email


@app.task
def send_insight_task(pk):
    from r2d2.insights.models import Insight

    try:
        insight = Insight.objects.get(pk=pk)
        client_domain = config.CLIENT_DOMAIN

        send_email('insight', "%s <%s>" % (insight.user.get_full_name(), insight.user.email), 'New Insight!',
                   {'domain': client_domain, 'insight': insight})
    except Insight.DoesNotExist:
        pass
