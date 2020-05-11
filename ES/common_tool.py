import json
import requests
import sys
from configparser import ConfigParser

class CStatisticTool:

    def __init__(self, in_time_range=""):
        self.url = "default"
        self.module = "default"
        self.term_list = "default"
        self.template = {}
        self.response = "default"
        self.request_url = "default"
        self.time_range = in_time_range
        pass

    def ReadConfig(self, config_path):
        config = ConfigParser()
        config.read(config_path)

        if "basic" in config:
            if "url" not in config["basic"]:
                return 1
        else:
            return 2
        return config

    def SetTerm(self, config, term):
        if term not in config:
            return

        if "query" not in self.template:
            self.template["query"] = {}

        if "bool" not in self.template["query"]:
            self.template["query"]["bool"] = {}

        for key in config[term]:
            if "type" == key:
                type = config[term][key]

                if type not in self.template["query"]["bool"]:
                    self.template["query"]["bool"][type] = []

            elif self.time_range =={} and "range" == type:
                if "must" not in self.template["query"]["bool"]:
                    self.template["query"]["bool"]["must"] = []
                range_item = {}
                range_item[term] = {}
                for (term_key, term_value) in config[term].items():
                    if "type" == term_key:
                        continue
                    range_item[term][term_key] = term_value
                item = {}
                item["range"] = range_item
                self.template["query"]["bool"]["must"].append(item)

            elif "range" != type:
                item = {key:{}}
                term_info = config[term][key]
                if "terms" == key:
                    item[key][term] = []
                    for one_info in term_info.split(';'):
                        item[key][term].append(one_info)
                else:
                    item[key][term] = term_info
                self.template["query"]["bool"][type].append(item)

    def GenRequestUrl(self, config):
        self.url = config["basic"]["url"]
        self.module = config["basic"]["module"]
        self.term_list = config["basic"]["term_list"]

        self.request_url = self.url + "spider_log_" + self.module + "_*/logs/_search"

        terms = self.term_list.split(';')
        for term in terms:
            self.SetTerm(config, term)
        if self.time_range:
            if self.template == {}:
                self.template = {"query":{"bool":{"must":[]}}}
            item = {"range":{}}
            item["range"]["@timestamp"] = self.time_range
            self.template["query"]["bool"]["must"].append(item)

        self.request_data = json.dumps(self.template)


    def RequestElasticSearch(self):
        #print self.request_data
        response = requests.post(self.request_url, self.request_data)
        self.response = json.loads(response.text)
        pass

    def HandleResponseResult(self):
        #print self.module, self.response['hits']['total']
        return self.response['hits']['total']

    def GetResult(self):
        pass

    def Run(self, config_path):
        config = self.ReadConfig(config_path)
        self.GenRequestUrl(config)
        self.RequestElasticSearch()
        #self.HandleResponseResult()
        pass

