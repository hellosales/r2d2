# from django.conf import settings
# from ws4redis.publisher import RedisPublisher
# from ws4redis.redis_store import RedisMessage
# from rest_framework.renderers import JSONRenderer


def publish(user, item=None, additional_data=None):
    pass
    # if additional_data is None:
    #     additional_data = {}
    # redis_publisher = RedisPublisher(facility='all', users=[user.email])
    # r = JSONRenderer()
    # if item is None:
    #     data = {}
    # else:
    #     data = item.as_dict()
    # data.update(additional_data)
    # data = r.render(data)
    # message = RedisMessage(data)
    # if settings.TESTING:
    #     # Do not send in tests
    #     return
    # redis_publisher.publish_message(message)
