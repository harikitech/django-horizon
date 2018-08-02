from django.db.models.manager import Manager

from .query import QuerySet


class HorizontalManager(Manager.from_queryset(QuerySet)):
    use_for_related_fields = True
    use_in_migrations = True

    def __init__(self):
        super(HorizontalManager, self).__init__()
