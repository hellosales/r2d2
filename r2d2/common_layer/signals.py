from django.dispatch import Signal


object_imported = Signal(providing_args=["importer_class", "mapped_data"])
