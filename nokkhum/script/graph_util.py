'''
Created on Oct 29, 2014

@author: boatkrap
'''


from nokkhum import config
import os
import sys
import json
import datetime
import argparse
import re

from nokkhum.compute import benchmark
from nokkhum.compute import machine_specification

from matplotlib import pyplot as plt
import numpy

FPSS = [1, 5, 7, 10, 15, 20, 25, 30]
IMAGE_SIZES = [(160, 120), (320, 240), (640, 480), (800, 600),
               (960, 720), (1120, 840)]


VIDEO_ANALYSIS = ['Acquisition', 'Motion Detector', 'Video Recorder', 'Motion Recorder']
DEFAULT_VIDEO_ANALYSIS = 'Motion Detector'
DEFAULT_FPS = 10
DEFAULT_IMAGE_SIZE = (640, 480)

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class GraphBuilder:
    def __init__(self, fname, output_path):

        self.results = None

        with open(fname, 'r') as f:
            self.results = json.load(f)
        if self.results is None:
            sys.exit()

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.output_path = output_path
        self.start = 5
        self.end = 150

        self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
                              '-v', '-8', '-<', '->']


    def build_cpu_criteria(self, results):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        marker = 0

        cpu_results = [r['cpu_used'] for r in results][self.start: self.end]

        print(cpu_results)

        g_mean = numpy.mean(cpu_results)
        g_max = numpy.max(cpu_results)
        g_min = numpy.min(cpu_results)
        g_avg_max = numpy.mean([c for c in cpu_results if c >= g_mean])
        g_avg_min = numpy.mean([c for c in cpu_results if c < g_mean])



        print("CPU mean:", g_mean)
        print("CPU std:", numpy.std(cpu_results))
        print("CPU max:", g_max)
        print("CPU min:", g_min)

        ax.plot(cpu_results,
                self.graph_pattern[marker], label="CPU usage")
        marker += 1

        ax.plot([0, len(cpu_results)], [g_mean, g_mean],
                self.graph_pattern[marker], lw=2, label="Avg CPU usage")
        marker += 1
        ax.plot([0, len(cpu_results)], [g_max, g_max],
                self.graph_pattern[marker], lw=2, label="Max CPU usage")
        marker += 1
        ax.plot([0, len(cpu_results)], [g_min, g_min],
                self.graph_pattern[marker], lw=2, label="Min CPU usage")
        marker += 1
        ax.plot([0, len(cpu_results)], [g_avg_max, g_avg_max],
                self.graph_pattern[marker], lw=2, label="Avg Max CPU usage")
        marker += 1
        ax.plot([0, len(cpu_results)], [g_avg_min, g_avg_min],
                self.graph_pattern[marker], lw=2, label="Avg Min CPU usage")
        marker += 1


        fontsize = 25
        ax.set_xlabel("Time (s)",  fontsize=fontsize)
        ax.set_ylabel("CPU usage (%)", fontsize=fontsize)
        ax.set_title('CPU Usage Criteria', fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-cpu-criteria.png')
        plt.close()


    def build(self):
        image_results = self.results['results'][str(DEFAULT_FPS)]['%sx%s'%DEFAULT_IMAGE_SIZE][DEFAULT_VIDEO_ANALYSIS]['results']
        self.build_cpu_criteria(image_results)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-i', '--input',
                        help='benchmark input')
    parser.add_argument('-o', '--output',
                        help='performance result')

    args = parser.parse_args()
    print("args:", args)

    if not os.path.exists(args.input):
        print('file does not exist')
        sys.exit()

    if not os.path.exists(args.output):
        print('xxxx')
        os.makedirs(args.output)

    gb = GraphBuilder(args.input, args.output)
    gb.build()

