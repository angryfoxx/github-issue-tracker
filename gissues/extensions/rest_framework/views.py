from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class MetaViewSet(GenericViewSet):
    def list(self, request, *args, **kwargs):
        meta = {
            "name": "gissues",
            "version": "0.1.0",
        }
        return Response(meta)
