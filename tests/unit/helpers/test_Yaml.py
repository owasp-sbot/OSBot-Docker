from unittest import TestCase

from osbot_utils.utils.Files import file_exists, file_contents, file_save
from osbot_utils.utils.Process import exec_process, exec_open

from osbot_docker.helpers.Yaml import yaml_parse, yaml_save, yaml_load, Yaml

yaml_code = ('''
age: 30
automobiles:
- brand: Honda
  type: Odyssey
  year: 2018
- brand: Toyota
  type: Sienna
  year: 2015
name: John''').strip() + '\n'       # extra line will make it equal to the result of yaml_save

class test_Yaml(TestCase):
    def setUp(self):
        pass

    def test_yaml_save__load(self):
        yaml    = yaml_parse(yaml_code)
        yaml_file = yaml_save(yaml)

        assert file_exists(yaml_file) is True
        assert file_contents(yaml_file) == yaml_code

        assert yaml_load(yaml_file) == yaml


    def test_yaml_parse(self):

        result = Yaml.yaml_parse(yaml_code)
        assert result['name'] == 'John'
        assert result['age' ]  == 30
        assert len(result["automobiles"]) == 2
        assert result["automobiles"][0]["brand"] == "Honda"
        assert result["automobiles"][1]["year"]  == 2015

        assert Yaml.yaml_parse == yaml_parse