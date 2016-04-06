from r2d2.celery import app


@app.task
def fetch_data_task(model, pk):
    try:
        obj = model.objects.get(pk=pk)
        obj.fetch_data()
    except model.DoesNotExist:
        return "%s with id %d not found" % (model, pk)
