'''
Created on Oct 28, 2015

@author: boatkrap
'''


from nokkhum import config
import os
import json
import datetime
import argparse

from nokkhum.compute import benchmark
from nokkhum.compute import machine_specification

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


class GraphBuilder:
    def __init__(self, data, output_path):
        self.data = data
        self.results = data['results']
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self.start = 5
        self.end = 150

        self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
                              '-v', '-8', '-<', '->']

    def build_cpu_graph(self, image_size, key='Acquisition',
                        title=""):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        maker = 0

#         for image_size, results in image_size_results.items():
        for fps in FPSS:
            results = self.results[str(fps)]['%sx%s'%image_size]

            ax.plot([r['cpu_used'] for r in results[key]['results']][self.start: self.end],
                    self.graph_pattern[maker], label="%s fps" % fps)
            maker += 1

            #print("CPU mean %sx%s pixels:" % image_size,
                  #numpy.mean([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            #print("CPU std %sx%s pixels:" % image_size,
                  #numpy.std([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            #print("CPU max %sx%s pixels:" % image_size,
                  #numpy.max([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            #print("CPU min %sx%s pixels:" % image_size,
                  #numpy.min([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))

        fontsize = 25
        ax.set_xlabel("Time (s)",  fontsize=fontsize)
        ax.set_ylabel("CPU used (%)", fontsize=fontsize)
        ax.set_title(title + ' CPU Usage', fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-%s-%s-cpu.png' % ('%sx%s'%image_size, key.replace(" ", "-")))
        # fig.show()
        plt.close(fig)

    def build_memory_graph(self, image_size, key='Acquisition',
                           title=""):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        maker = 0

        for fps in FPSS:
            results = self.results[str(fps)]['%sx%s'%image_size]

            ax.plot([a['memory_used']/(10**6) for a in results[key]['results']][self.start: self.end],
                    self.graph_pattern[maker], label="%s fps" % fps)
            maker += 1
            #print("Memory mean %sx%s pixels:" % image_size,
                  #numpy.mean([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            #print("Memory std %sx%s pixels:" % image_size,
                  #numpy.std([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            #print("Memory max %sx%s pixels:" % image_size,
                  #numpy.max([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            #print("Memory min %sx%s pixels:" % image_size,
                  #numpy.min([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))

        fontsize = 25
        ax.set_xlabel("Time (s)", fontsize=fontsize)
        ax.set_ylabel("Memory usage (MB)", fontsize=fontsize)
        ax.set_title('Memory Usage of '+title, fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-%s-%s-memory.png' % ('%sx%s'%image_size, key.replace(" ", "-")))
        # fig.show()
        plt.close(fig)

    def build(self):
        # aquisition

        for image_size in IMAGE_SIZES:

            # for processing motion acquisition
            print("process acquisition")
            print("process graph image size:", image_size)

            self.build_cpu_graph(image_size, 'Acquisition',
                                 'Image Acquisition')
            self.build_memory_graph(image_size, 'Acquisition',
                                    'Image Acquisition')

            # for processing motion detector
            print("process motion detector")
            self.build_cpu_graph(image_size, 'Motion Detector',
                                 'Motion Detector')
            self.build_memory_graph(image_size, 'Motion Detector',
                                    'Motion Detector')

            # for processing video recorder
            self.build_cpu_graph(image_size, 'Video Recorder',
                                 'Video Recorder')
            self.build_memory_graph(image_size, 'Video Recorder',
                                    'Video Recorder')

            # for processing video recorder
            self.build_cpu_graph(image_size, 'Motion Recorder',
                                 'Motion Recorder')
            self.build_memory_graph(image_size, 'Motion Recorder',
                                    'Motion Recorder')



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-i', '--input',
                        help='input result')
    parser.add_argument('-g', '--graph_output',
                        help='graph output path')

    args = parser.parse_args()
    print("args:", args)
    with open(args.input, "r") as f:
        results = json.load(f)
        gb = GraphBuilder(results, args.graph_output)
        gb.build()
