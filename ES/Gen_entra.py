#encoding:utf-8

import json
import requests
import datetime
import time
import sys
import copy
import os
from configparser import ConfigParser
from common_tool import CStatisticTool

class GenData:

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_dir = os.path.dirname(os.path.abspath(config_path))
        self.data_path = "None"
        self.module = "None"
        self.module_list = []
        self.module_data = {}
        self.time_range = {}
        self.module_config = {}
        self.module_operation = {}
        self.ReadConfig()

    def __getattr__(self, item):
        try:
            return json.dumps(self.module_data)
        except:
            raise AttributeError(r"object has no attribute '%s'" %item)

    def GenTimeRange(self, gap, remainder, num_advance=0):
        """ gen time range [gte, lt)
            while gap is lt - gte
            remainder is lastest lt
            """
        current_time = int(time.time())
        time_remainder = current_time % (60 * remainder)
        range_lt = current_time - time_remainder - 60 * gap * num_advance
        range_gte = range_lt - 60 * gap

        self.time_range["lt"]  = self.TimeFormat(range_lt)
        self.time_range["gte"] = self.TimeFormat(range_gte)


    def TimeFormat(self, timestamp):
        time_local = time.localtime(timestamp - 8 * 3600)
        time_str = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time_local)
        return time_str

    def ReadConfig(self):
        config = ConfigParser()
        config.read(self.config_path)

        # read data path
        if "basic" not in config:
            raise KeyError("basic not in config")
        data = config["basic"]["data"] if "data" in config["basic"] else "../data/default"
        self.data_path = self.config_dir + data

        # read module info
        if "module" not in config["basic"]:
            raise KeyError("module not in basic")
        self.module = config["basic"]["module"]
        self.module_list = self.module.split(';')

        #read time_range
        if "time_range" in config["basic"] and config["basic"]["time_range"]:
            time_range_items = config["basic"]["time_range"].split(':')
            gap = time_range_items[0]
            remainder = time_range_items[1]
            num_advance = time_range_items[2]
            self.GenTimeRange(int(gap), int(remainder), int(num_advance))

        for module_item in self.module_list:
            if "config" in config[module_item]:
                self.module_config[module_item] = self.config_dir + '/' + config[module_item]["config"]
            if "operation" in config[module_item]:
                self.module_operation[module_item] = config[module_item]["operation"]

    def RequestData(self):
        for (module, config_path) in self.module_config.items():
            # statistic data
            cst = CStatisticTool(self.time_range)
            cst.Run(config_path)
            value = cst.HandleResponseResult()
            self.module_data[module] = value

        for (module, operation) in self.module_operation.items():
            # check param exist
            one_operation = eval(operation, self.module_data)
            self.module_data[module] = 0 if one_operation < 0 else one_operation

        #eval bug
        #TODO
        if "__builtins__" in self.module_data:
            del self.module_data["__builtins__"]



if __name__ == "__main__":
    config_file = sys.argv[1]
    gen_data = GenData(config_file)
    gen_data.RequestData()
    print json.dumps(gen_data.module_data)
