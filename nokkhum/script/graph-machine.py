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
    def __init__(self, directory, output_path):

        pattern = re.compile('.*\.json$')
        dname = [directory+"/"+name for name in  sorted(os.listdir(directory))\
                if pattern.match(name)]
        # print("check name:", dname)
        # sys.exit();
        self.results = []
        for fname in dname:
            with open(fname, 'r') as f:
                self.results.append(json.load(f))

        self.output_path = output_path
        self.start = 5
        self.end = 150

        self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
                              '-v', '-8', '-<', '->']


    def build_machine_graph(self, fps, image_size, video_analysis, machine_path=None):

        cpu_fig = plt.figure()
        cpu_fig.set_size_inches(18.5, 10.5)
        cpu_ax = cpu_fig.add_subplot(111)

        mem_fig = plt.figure()
        mem_fig.set_size_inches(18.5, 10.5)
        mem_ax = mem_fig.add_subplot(111)


        marker = 0

        for result in self.results:
            ms = result['machine_specification']
            presults = result['results'][str(fps)]['%sx%s'%image_size][video_analysis]['results']
            cpu_ax.plot([r['cpu_used'] for r in presults][self.start: self.end],
                    self.graph_pattern[marker], label="%.1f MHz:%s"%(ms['cpu_frequency'], ms['cpu_model']))
            mem_ax.plot([r['memory_used']/(10**6) for r in presults][self.start: self.end],
                    self.graph_pattern[marker], label="%.1f MHz:%s"%(ms['cpu_frequency'], ms['cpu_model']))
            marker += 1

        fontsize = 25
        cpu_ax.set_xlabel("Time (s)",  fontsize=fontsize)
        cpu_ax.set_ylabel("CPU usage (%)", fontsize=fontsize)
        cpu_ax.set_title('CPU Usage of '+video_analysis, fontsize=fontsize)
        cpu_ax.legend()
        cpu_ax.tick_params(labelsize=fontsize)
        cpu_ax.grid(True)

        mem_ax.set_xlabel("Time (s)",  fontsize=fontsize)
        mem_ax.set_ylabel("Memory usage (MB)", fontsize=fontsize)
        mem_ax.set_title('Memory Usage of ' + video_analysis, fontsize=fontsize)
        mem_ax.legend()
        mem_ax.tick_params(labelsize=fontsize)
        mem_ax.grid(True)


        #plt.legend(prop={'size': fontsize})
        if machine_path:
            cpu_fig.savefig(machine_path +
                    '/fig-%sfps-%s-%s-cpu.png' % (fps, '%dx%d'%image_size, video_analysis.replace(" ", "-")))

            mem_fig.savefig(machine_path +
                    '/fig-%sfps-%s-%s-memory.png' % (fps, '%dx%d'%image_size, video_analysis.replace(" ", "-")))
        else:
            cpu_fig.savefig(self.output_path +
                    '/fig-%sfps-%s-%s-cpu.png' % (fps, '%dx%d'%image_size, video_analysis.replace(" ", "-")))

            mem_fig.savefig(self.output_path +
                    '/fig-%sfps-%s-%s-memory.png' % (fps, '%dx%d'%image_size, video_analysis.replace(" ", "-")))

        # cpu_fig.show()
        # mem_fig.show()
        plt.close(cpu_fig)
        plt.close(mem_fig)

    def build_all(self):
        machine_path = self.output_path+'/machines/'
        if not os.path.exists(machine_path):
            os.makedirs(machine_path)

        for fps in FPSS:
            for image_size in IMAGE_SIZES:
                for video_analysis in VIDEO_ANALYSIS:
                    self.build_machine_graph(fps, image_size, video_analysis, machine_path)


    def build_cpu_graph(self, image_size_results, key='Acquisition',
                        title="", fps=0):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        marker = 0


#         for image_size, results in image_size_results.items():
        for image_size in IMAGE_SIZES:
            results = image_size_results['%sx%s'%image_size]

            print("image size %sx%s:" % image_size)

            ax.plot([r['cpu_used'] for r in results[key]['results']][self.start: self.end],
                    self.graph_pattern[marker], label="%sx%s pixels" % image_size)
            marker += 1

            print("CPU mean %sx%s pixels:" % image_size,
                  numpy.mean([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            print("CPU std %sx%s pixels:" % image_size,
                  numpy.std([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            print("CPU max %sx%s pixels:" % image_size,
                  numpy.max([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))
            print("CPU min %sx%s pixels:" % image_size,
                  numpy.min([r['cpu_used'] for r in results[key]['results']][self.start: self.end]))

        fontsize = 25
        ax.set_xlabel("Time (s)",  fontsize=fontsize)
        ax.set_ylabel("CPU usage (%)", fontsize=fontsize)
        ax.set_title('CPU Usage of ' + title, fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-%sfps-%s-cpu.png' % (fps, key.replace(" ", "-")))
        fig.show()

    def build_memory_graph(self, image_size_results, key='Acquisition',
                           title="", fps=0):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        marker = 0

        for image_size in IMAGE_SIZES:
            results = image_size_results['%sx%s'%image_size]

            ax.plot([a['memory_used']/(10**6) for a in results[key]['results']][self.start: self.end],
                    self.graph_pattern[marker], label="%sx%s pixels" % image_size)
            marker += 1
            print("Memory mean %sx%s pixels:" % image_size,
                  numpy.mean([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            print("Memory std %sx%s pixels:" % image_size,
                  numpy.std([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            print("Memory max %sx%s pixels:" % image_size,
                  numpy.max([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))
            print("Memory min %sx%s pixels:" % image_size,
                  numpy.min([r['memory_used']/(10**6) for r in results[key]['results']][self.start: self.end]))

        fontsize = 25
        ax.set_xlabel("Time (s)", fontsize=fontsize)
        ax.set_ylabel("Memory used (MB)", fontsize=fontsize)
        ax.set_title(title + ' Memory Usage', fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-%sfps-%s-memory.png' % (fps, key.replace(" ", "-")))
        fig.show()

    def build(self, show):
        print('results: ', self.results)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-d', '--directory',
                        help='benchmark directory')
    parser.add_argument('-o', '--output',
                        help='performance result')

    parser.add_argument('-p', '--video_path',
                        help='video path')
    parser.add_argument('-x', '--video_prefix',
                        help='video prefix')
    parser.add_argument('-t', '--video_type',
                        help='video type')

    parser.add_argument('-i', '--input',
                        help='input result')
    parser.add_argument('-g', '--graph_output',
                        help='graph output path')
    parser.add_argument('-s', '--show_graph', action='store_true',
                        default=False,
                        help='show graph after build')

    args = parser.parse_args()
    print("args:", args)
    if os.path.isdir(args.directory):
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        gb = GraphBuilder(args.directory, args.output)
        gb.build_all()
    else:
        print('wrong directory')
