from rest_framework.reverse import reverse


def test_MetaViewSet_list(api_client):
    response = api_client.get(reverse("meta-list"))

    assert response.status_code == 200
    assert response.data == {
        "name": "gissues",
        "version": "0.1.0",
    }
