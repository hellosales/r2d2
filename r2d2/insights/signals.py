from django.dispatch import Signal


data_fetched = Signal(providing_args=["account", "fetched_from_all", "success"])
