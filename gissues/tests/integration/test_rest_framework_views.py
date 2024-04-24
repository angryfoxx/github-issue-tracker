import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_meta_view_set_list(api_client):
    response = api_client.get(reverse("api:meta-list"))

    assert response.status_code == 200
    assert response.data == {
        "name": "gissues",
        "version": "0.1.0",
    }
