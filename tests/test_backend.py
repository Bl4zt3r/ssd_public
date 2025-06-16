import requests

def test_backend_running():
    resp = requests.get("http://localhost:8000/api/contenedores")
    assert resp.status_code in (200, 404)
