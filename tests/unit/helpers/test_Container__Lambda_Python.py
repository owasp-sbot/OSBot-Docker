import pytest
from unittest                                       import TestCase
from osbot_utils.utils.Env                          import in_github_action
from osbot_docker.helpers.Container__Lambda_Python  import Container__Lambda_Python


class test_Container__Lambda_Python(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if in_github_action():
            pytest.skip('this test is failing in GH Actions with: Not Found ("No such image: lambda_python__3_11:latest")')  # todo: figure out why this is happening

    def test__enter__exit(self):
        with Container__Lambda_Python() as _:
            assert _.container.exists() is True
            assert _.container.wait_for_logs() is True
            assert _.invoke(               ) == 'docker - hello world!'
            assert _.invoke({'name':'aaaa'}) == 'docker - hello aaaa!'
        assert _.container.exists() is False

    # def test_docker_setup(self):
    #     container_id = 'd8d90564323a'
    #     container = Docker_Container(container_id=container_id)
    #     pprint(container.info_raw())