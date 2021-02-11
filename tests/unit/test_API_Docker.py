from pprint import pprint
from unittest import TestCase

from osbot_utils.utils.Json import json_parse

from osbot_utils.utils.Files import path_combine, folder_exists, file_exists, temp_folder

from osbot_docker.API_Docker import API_Docker
from osbot_utils.utils.Misc import lower, random_string


class test_API_Docker(TestCase):

    def setUp(self) -> None:
        self.api_docker = API_Docker()
        self.path_docker_images = path_combine(__file__, '../../_test_data/docker_images')
        print()

    def test_client(self):
        assert type(self.api_docker.client()).__name__ == 'DockerClient'

    def test_container_run(self):
        assert 'Hello from Docker!' in self.api_docker.container_run('hello-world').get('output')
        assert self.api_docker.container_run('hello-world', 'bbbb').get('error') == ('404 Client Error for '
                                                                                     'http+docker://localhost/v1.40/images/create?tag=bbbb&fromImage=hello-world: '
                                                                                     'Not Found ("manifest for hello-world:bbbb not found: manifest unknown: '
                                                                                     'manifest unknown")')
        assert self.api_docker.container_run('aaaa', 'bbbb').get('error') == ('404 Client Error for '
                                                                              'http+docker://localhost/v1.40/images/create?tag=bbbb&fromImage=aaaa: '
                                                                              'Not Found ("pull access denied for aaaa, repository does not '
                                                                              "exist or may require 'docker login': denied: requested access to the "
                                                                              'resource is denied")')


    def test_containers(self):
        assert type(self.api_docker.containers()) is list            # todo once we create a container per execution change this to reflect that

    def test_docker_params_append_options(self):
        docker_params = ['run']
        options        = {'key': '-v', 'value':'/a:/b'}
        result         = self.api_docker.docker_params_append_options(docker_params=docker_params,options=options)
        assert result == ['run', '-v','/a:/b']

        options        = [{'key': '-v', 'value':'/c:/d'}, {'key': '-v', 'value':'/e:/f'}]
        result         = self.api_docker.docker_params_append_options(docker_params, options)
        assert result == ['run', '-v', '/a:/b', '-v', '/c:/d', '-v', '/e:/f']

    def test_image_build(self):
        target_image      = 'centos'
        expected_size     = 209348126
        folder_dockerFile = path_combine(self.path_docker_images, target_image)
        path_dockerfile   = path_combine(folder_dockerFile, 'Dockerfile')
        repository        = "osbot_docker__test_image_build"
        tag               = "abc"
        image_name        = f"{repository}:{tag}"

        assert folder_exists(folder_dockerFile)
        assert file_exists(path_dockerfile)

        result = self.api_docker.image_build(folder_dockerFile, repository, tag)

        build_logs = result.get('build_logs')
        image      = result.get('image')
        status     = result.get('status')
        tags       = result.get('tags')

        assert self.api_docker.image_exists(repository, tag)
        assert status == 'ok'
        assert image_name in tags
        assert image_name in self.api_docker.images_names()
        assert image.get('Size') == expected_size
        assert next(build_logs) == {'stream': 'Step 1/3 : FROM centos:8'}

        assert self.api_docker.image_delete(repository,tag) is True

        assert image_name not in self.api_docker.images_names()

    def test_image_build__bad_data(self):
        assert self.api_docker.image_build(None         , None).get('error') == 'Either path or fileobj needs to be provided.'
        assert self.api_docker.image_build(''           , None).get('error') == 'You must specify a directory to build in path'
        # todo: find out why in GH Actions the line below throws the error: AttributeError: 'APIError' object has no attribute 'msg'
        #assert self.api_docker.image_build(temp_folder(), None).get('exception').msg.get('message') == 'Cannot locate specified Dockerfile: Dockerfile'

    def test_image_build_scratch(self):
        path       = path_combine(self.path_docker_images, 'scratch')
        repository  = 'scratch'
        tag         = 'latest'
        result = self.api_docker.image_build(path=path, repository=repository, tag=tag)
        assert result.get('image').get('Size') == 0

    def test_image_info(self):
        assert self.api_docker.image_info(random_string()) is None

    def test_image_exists(self):
        assert self.api_docker.image_exists(random_string()) is False

    def test_image_pull(self):
        repository = 'centos'
        tag        = '8'
        image = self.api_docker.image_pull(repository,tag)
        assert image.tags == ['centos:8']
        assert self.api_docker.container_run(repository, tag, "pwd"                    ) == {'output': '/'                            , 'status': 'ok'}
        assert self.api_docker.container_run(repository, tag, "cat /etc/redhat-release") == {'output': 'CentOS Linux release 8.3.2011', 'status': 'ok'}



    def test_images(self):
        images = self.api_docker.images()
        assert len(images) > 0

    def test_images_names(self):
        names = self.api_docker.images_names()
        assert 'hello-world:latest' in names

    def test_server_info(self):
        server_info = self.api_docker.server_info()
        assert 'KernelMemory' in server_info
        assert lower(server_info.get('OSType')) == 'linux'
