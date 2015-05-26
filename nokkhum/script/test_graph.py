'''
Created on Oct 29, 2014

@author: boatkrap
'''


from nokkhum import config
import os
import json
import datetime
import argparse

from nokkhum.compute import benchmark

from matplotlib import pyplot as plt
import numpy

FPSS = [1, 5, 7, 10, 15, 20, 25, 30]
IMAGE_SIZES = [(160, 120), (320, 240), (640, 480), (800, 600),
               (960, 720), (1120, 840)]

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class ResultBuilder:
    def __init__(self, data, output_path):
        self.data = data
        self.output_path = output_path
        if output_path is not None and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self.start = 5
        self.end = 150

        # self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
        #                       '-v', '-8', '-<', '->']

    def build(self, show):
        # aquisition

        for fps, image_size_results in self.data.items():
            for image_size, image_analysis_results in image_size_results.items():
                for image_analysis, results in image_analysis_results.items():
                    cpu_used = [result['cpu_used'] for result in results['results'][self.start: self.end]]
                    memory_used = [result['memory_used'] for result in results['results'][self.start: self.end]]

                    print(", ".join([fps,
                                        image_size,
                                        image_analysis,
                                        str(max(cpu_used)),
                                        str(min(cpu_used)),
                                        str(sum(cpu_used)/len(cpu_used)),
                                        str(max(memory_used)),
                                        str(min(memory_used)),
                                        str(sum(memory_used)/len(memory_used)),
                                    ]))
                    # print(max([result['cpu_used'] for result in results['results']]))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', choices=['graph'],
                        help='cmd help')

    parser.add_argument('-o', '--output',
                        help='performance result')
    parser.add_argument('-i', '--input',
                        help='input result')
    parser.add_argument('-g', '--graph_output',
                        help='graph output path')
    parser.add_argument('-s', '--show_graph', action='store_true',
                        default=False,
                        help='show graph after build')

    args = parser.parse_args()
    print("args:", args)

    if args.cmd == 'graph':
        with open(args.input, "r") as f:
            results = json.load(f)
            gb = ResultBuilder(results, args.graph_output)
            gb.build(args.show_graph)
