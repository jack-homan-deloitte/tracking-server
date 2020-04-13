class TestApi(object):
    def test_healthcheck(self, test_app):
        resp = test_app.get("/api/hc")
        assert resp.status_int == 200
