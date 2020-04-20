import logging
import pathlib
import os
import time

from docker import DockerClient
import requests
import git
import pytest


_logger = logging.getLogger(__name__)


def docker_run(*args, **kwargs):
    client = DockerClient(base_url="unix://var/run/docker.sock")
    return client.containers.run(*args, **kwargs)


def docker_build(*args, **kwargs):
    client = DockerClient(base_url="unix://var/run/docker.sock")
    return client.images.build(*args, **kwargs)


@pytest.mark.system
class TestSystem(object):

    @classmethod
    def setup_class(cls):
        port = 9999
        repo = git.Repo(os.path.dirname(__file__),
                        search_parent_directories=True)
        top = repo.git.rev_parse("--show-toplevel")
        path = pathlib.Path(top)

        tag = "idiet-system-test:" + str(port)
        image, logs = docker_build(path=path.as_posix(), tag=tag)
        for log in logs:
            _logger.debug(log.get("stream", "").strip())

        secret_set_in_env = "MY_SECRET_KEY"
        container = docker_run(
            tag, ports={"8080/tcp": port}, detach=True,
            environment={
                "IDIET_TRACKING_SECRET": secret_set_in_env
            }
        )
        # nginx = docker_run("nginx", ports={"80": port}, detach=True)
        time.sleep(1)
        cls.container = container
        cls.port = port
        cls.secret_set_in_env = secret_set_in_env

    @classmethod
    def teardown_class(cls):
        logs = cls.container.logs(stream=True)
        cls.container.kill()
        cls.container.remove()
        for log in logs:
            _logger.debug(log.decode().strip())

    def test_healthcheck(self):
        port = type(self).port
        r = requests.get(f"http://localhost:{port}/api/hc")
        assert r.status_code == 200

    def test_can_request_user_from_request(self):
        port = type(self).port
        data = {
            "username": "jmh25@njit.edu",
            "password": "my-password"
        }
        r = requests.post(f"http://localhost:{port}/api/register",
                          json=data)
        assert r.status_code == 201
        assert r.json().get("status") == "success"

    def test_can_use_token(self):
        port = type(self).port
        data = {
            "username": "jmh25@njit.edu",
            "password": "my-password"
        }
        r = requests.post(f"http://localhost:{port}/api/register", json=data)
        r = requests.post(f"http://localhost:{port}/api/login", json=data)
        token = r.json().get("token")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        r = requests.get(
            f"http://localhost:{port}/api/user/profile",
            headers=headers
        )
        data = r.json().get("data")
        assert data["member_since"]
        assert r.status_code == 202
