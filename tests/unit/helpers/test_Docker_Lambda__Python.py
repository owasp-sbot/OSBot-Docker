from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import wait_for

import docker_images
from osbot_docker.helpers.Docker_Lambda__Python import Docker_Lambda__Python
from osbot_utils.utils.Files                    import path_combine, folder_exists, file_exists


class test_Docker_Lambda__Python(TestCase):

    def setUp(self):
        self.docker_lambda__python = Docker_Lambda__Python()
        pass

    def teardown(self):
        pass

    def test_create_container(self):
        with self.docker_lambda__python.create_container() as _:
            assert _.exists       () is True
            assert _.info         ().get('image') == f"{self.docker_lambda__python.image_name}:latest"
            assert _.status       () == 'created'
            assert _.start        () is True
            assert _.status       () == 'running'
            assert _.wait_for_logs() is True

            assert "(rapid) exec '/var/runtime/bootstrap' (cwd=/var/task, handler=)" in _.logs()

            assert _.stop        () is True
            assert _.status      () == 'exited'
            assert _.delete      () is True

    def test_image_build(self):
        result = self.docker_lambda__python.image_build()
        assert result.get('status') == 'ok'

    def test_dockerfile(self):
        assert self.docker_lambda__python.dockerfile().startswith('FROM public.ecr.aws/lambda/python:3.11')

    def test_path_docker_dockerfile(self):
        assert file_exists(self.docker_lambda__python.path_docker_dockerfile())

    def test_path_docker_images(self):
        assert self.docker_lambda__python.path_docker_images() == docker_images.folder
        assert folder_exists(self.docker_lambda__python.path_docker_images())

    def test_path_lambda_python(self):
        assert folder_exists(self.docker_lambda__python.path_lambda_python())