from constance import config

from django.conf import settings

from r2d2.celery import app
from r2d2.emails.send import send_email


@app.task
def send_insight_task(pk):
    from r2d2.insights.models import Insight
    from r2d2.data_importer.models import reconstitute_data_provider

    initial_insight_email = {'subject': 'Your First Insight for %(merchant)s',
                             'header_text': 'Great, you\'ve set up %(channel_str)s and we\'ve successfully received your sales activity.\n\n\
Each time you add a new channel you\'ll get an email with an insight for that channel.  From then on out, Hello Sales\
 will look for new sales transactions daily and analyze them as they\'re available.  We\'ll send new insights directly\
 to your inbox.\n\nYour first insight is below and your entire history is always available in your'}

    insight_email = {'subject': 'Daily Sales Insight for %(merchant)s',
                     'header_text': 'We\'ve taken a look at your %(channel_str)s sales activity from %(time_period)s and have a new\
 insight ready for you.  You can always view all insights in your'}

    try:
        insight = Insight.objects.get(pk=pk)
        client_domain = config.CLIENT_DOMAIN

        channel_str = ''
        protocol = 'https://' if getattr(settings, 'IS_SECURE', False) else 'http://'

        if insight.is_initial:
            messaging = initial_insight_email

            # Channel in question should be the DataProvider that fired the Insight
            # for the first Insight email
            channel_str = reconstitute_data_provider(insight.data_provider_name,
                                                     insight.data_provider_id).name
        else:
            messaging = insight_email
            insight_channels_covered = []  # Channels referenced in the Insight
            channels = insight.channel_set.all()

            for one_channel in channels:
                insight_channels_covered.append(reconstitute_data_provider(one_channel.data_provider_name,
                                                                           one_channel.data_provider_id).name)

            if len(insight_channels_covered) == 1:
                channel_str = insight_channels_covered[0]
            elif len(insight_channels_covered) == 2:
                channel_str = ' and '.join(insight_channels_covered)
            elif len(insight_channels_covered) > 2:
                channel_str = ', '.join(insight_channels_covered[0:-1])
                channel_str = ', and '.join([channel_str, insight_channels_covered[-1]])

        replace_vals = {'channel_str': channel_str,
                        'merchant': insight.user.merchant_name,
                        'time_period': insight.time_period,
                        'protocol': protocol,
                        'client_domain': client_domain}

        subject = messaging['subject']
        header_text = messaging['header_text']
        header_text = header_text % replace_vals

        send_email('insight',
                   "%s <%s>" % (insight.user.get_full_name(), insight.user.email),
                   subject % replace_vals,
                   {'header_text': header_text,
                    'protocol': protocol,
                    'client_domain': client_domain,
                    'insight': insight,
                    'channel_names': channel_str})
    except Insight.DoesNotExist:
        pass
