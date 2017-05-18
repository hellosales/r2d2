from __future__ import absolute_import

import logging
import traceback

from django.conf import settings
from celery import Task  # http://docs.celeryproject.org/en/latest/userguide/application.html#abstract-tasks
from celery.utils.log import get_task_logger

from r2d2.celery import app
from r2d2.data_importer.models import RetriableError, RateLimitError
from r2d2.utils.class_tools import class_for_name

#logger = logging.getLogger('django')
logger = get_task_logger(__name__)


class BaseImporterTask(Task):
    """
    Base class for data import tasks.  Allows functionality to be centralized
    while still splitting tasks out into separate apps/modules/classes.
    """
    asbtract = True  # mark as abstract so Celery won't register this class for execution

    def _run_inner(self, model_str, pk, rate=None):
        """
        Queue-able call to fetch data, common to all channels (remote transaction APIs).

        - reconstitute DB object with (model, pk)
            * look for errors and handle exceptional cases:
                * rate limiting:
                    * catch exception, then
                    * ask model for retry seconds
                    * or ask model for rate limit?
                    * if rate limit set Control.rate_limit for this task name to the new limit.
                    * if model has rate limit use that
                    * else Use inverse exponential rate_limit strategy?
                    * if retry seconds
                    * set task.retry to retry seconds
                    * set all other tasks to += retry seconds
                * retries: use exponential retry strategy from
                    https://library.launchkit.io/three-quick-tips-from-two-years-with-celery-c05ff9d7f9eb
                    can also add 'jitter': https://blog.miguelgrinberg.com/post/how-to-retry-with-class
            * should separately set a global max_retries policy
            * all exception handling and failure cases should be handled here
            * call to log exception if not handled by retries

        Note:  Celery's design encourages tasks that should be handled by different
        queues and workers be packaged into different apps/modules/tasks.  This
        functionality is centralized here and then sub-classed by each app.

        Note for Celery 3.1.x:  this method isn't named run().  calling super().run() gave
        intermittent TypeErrors due to some funky class loader issue.  Not having
        to call super() sidesteps this issue.  This is likely due to how Celery
        handles task loading.
        """
        try:
            model = class_for_name(model_str)
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            # TODO:  log error, raise, or return?
            # return "%s with id %d not found" % (model, pk)
            raise

        try:
            obj.fetch_data()
        except RateLimitError as re:
            # update queue rate limit
            # NOTE:  rate limit indication varies significantly by channel, so
            # this logic backs off according to the rate_backoff method, which
            # should be overridden as needed. This logic will kick a rate-limited
            # request out to a longer retry to allow rate-limiting to loosen.
            if not re.rate_limit:
                if rate:
                    rl = self.rate_backoff(rate)
                elif self.rate_limit:
                    rl = self.rate_limit
                else:
                    rl = settings.DEFAULT_CHANNEL_API_RATE_LIMIT  # stab in the dark here
            else:
                rl = re.rate_limit

            logger.info("RateLimitError caught, task rate limit changed to %s for %s" % (rl, self.name))
            app.control.rate_limit(self.name, rl, destination=[self.request.hostname])

            self.retry(args=[model_str, pk, rl],
                       max_retries=obj.MAX_RETRIES,
                       countdown=settings.MIN_RATE_LIMIT_RETRY_TIME,
                       exc=re)
            args = [self.request.hostname, self.name]
            monitor_rate_limit.apply_async(args=args,
                                           queue=model.__name__,
                                           countdown=settings.RATE_LIMIT_QUEUE_CHECK_COUNTDOWN)
        except RetriableError as re:  # 2nd because RateLimitError subclasses this one
            # self.retry() exponential retry seconds loop until MAX_RETRIES
            if not re.retry_time:
                countdown = self.retry_backoff(self.request.retries)
            else:
                countdown = re.retry_time

            logger.info("RetriableError caught, task retrying with retry time %s for %s" % (countdown, self.name))
            self.retry(args=[model_str, pk],
                       max_retries=obj.MAX_RETRIES,
                       countdown=countdown,
                       exc=re)
        except Exception, e:
            # Not an exception we can retry.  Log error and fail the fetch
            logger.error(traceback.format_exc())
            obj.log_error(unicode(e))

    def retry_backoff(self, attempts):
        """
        Returns the number of seconds to schedule the next retry for, given the
        number of attempts made so far.

        Uses the exponential retry strategy.
        """
        return 2 ** attempts

    def rate_backoff(self, rate):
        """
        Returns the rate to execute tasks at, per 60 seconds

        Uses the inverse exponential rate strategy.
        """
        return rate/2


@app.task(bind=True, max_retries=None)
def monitor_rate_limit(self, worker, task):
    """
    Monitors to see if the queue is empty (besides this task), and if so resets
    the rate_limit on the queue to the default for that queue.  If not it retries
    in the future.  This task checks if another instance of itself is already-queued,
    and if so returns without taking any action.
    """
    logger.info("rate limit monitor working on worker, task, my id: %s, %s, %s" % (worker, task, self.request.id))
    i = app.control.inspect([worker])
    counter = 0

    # ensure only one of this task is present on each queue, but use the opportunity
    # to count other tasks on the queue at the same time
    for one in i.scheduled()[worker]:
        if one['request']['name'] == self.name:
            if not one['request']['id'] == self.request.id:
                logger.info("already have a rate limit monitor on queue, quitting")
                return
        else:
            counter += 1
    for one in i.active()[worker]:
        if one['name'] == self.name:
            if not one['id'] == self.request.id:
                logger.info("already have a rate limit monitor on queue, quitting")
                return
        else:
            counter += 1
    for one in i.reserved()[worker]:
        if one['name'] == self.name:
            if not one['id'] == self.request.id:
                logger.info("already have a rate limit monitor on queue, quitting")
                return
        else:
            counter += 1

    # If counter = 0 we can reset rate limits
    if counter == 0:
        rl = class_for_name(task).rate_limit
        logger.info("rate limit monitor detecting empty queue, reseting rate limit to: %s" % rl)
        if rl is None:
            rl = ''
        app.control.rate_limit(task, rl, destination=[worker])
    else:
        logger.info("rate limit monitor detecting not empty queue, will retry later")
        self.retry(args=[worker, task],
                   countdown=settings.RATE_LIMIT_QUEUE_CHECK_COUNTDOWN)
