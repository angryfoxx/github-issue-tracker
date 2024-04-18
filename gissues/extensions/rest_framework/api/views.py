from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class MetaViewSet(GenericViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        meta = {
            "name": "gissues",
            "version": "0.1.0",
        }
        return Response(meta)
