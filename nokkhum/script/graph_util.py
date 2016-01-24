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
DEFAULT_VIDEO_ANALYSIS = 'Video Recorder'
DEFAULT_FPS = 10
DEFAULT_IMAGE_SIZE = (640, 480)

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class GraphBuilder:
    def __init__(self, input_path, output_path):

        self.results = []

        pattern = re.compile('.*\.json$')
        dname = [input_path+'/'+name for name in  sorted(os.listdir(input_path))\
                    if pattern.match(name)]

        for fname in dname:
            with open(fname, 'r') as f:
                self.results.append(json.load(f))

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
        c_fig = plt.figure()
        c_fig.set_size_inches(18.5, 10.5)
        c_ax = c_fig.add_subplot(111)
        marker = 0

        cpu_results = [r['cpu_used'] for r in results][self.start: self.end]
        mem_results = [r['memory_used'] for r in results][self.start: self.end]


        c_mean = numpy.mean(cpu_results)
        c_max = numpy.max(cpu_results)
        c_min = numpy.min(cpu_results)
        c_avg_max = numpy.mean([c for c in cpu_results if c >= c_mean])
        c_avg_min = numpy.mean([c for c in cpu_results if c < c_mean])

        m_mean = numpy.mean(mem_results)
        m_max = numpy.max(mem_results)
        m_min = numpy.min(mem_results)
        m_avg_max = numpy.mean([m for m in mem_results if m >= m_mean])
        m_avg_min = numpy.mean([m for m in mem_results if m < m_mean])

        print('CPU mean:', c_mean)
        print('CPU std:', numpy.std(cpu_results))
        print('CPU max:', c_max)
        print('CPU min:', c_min)
        print('CPU avg min:', c_avg_min)
        print('CPU avg max:', c_avg_max)

        print('MEM mean:', m_mean)
        print('MEM std:', numpy.std(mem_results))
        print('MEM max:', m_max)
        print('MEM min:', m_min)
        print('MEM avg min:', m_avg_min)
        print('MEM avg max:', m_avg_max)


        step_marker = range(0, len(cpu_results), 10)

        c_ax.plot(cpu_results,
                self.graph_pattern[marker], label='CPU usage')
        marker += 1

        c_ax.plot(step_marker, [c_mean]*len(step_marker),
                self.graph_pattern[marker], lw=3, ms=10, label='Avg CPU usage')
        marker += 1
        c_ax.plot(step_marker, [c_max]*len(step_marker),
                self.graph_pattern[marker], lw=3, ms=10, label='Max CPU usage')
        marker += 1
        c_ax.plot(step_marker, [c_min]*len(step_marker),
                self.graph_pattern[marker], lw=3, ms=10, label='Min CPU usage')
        marker += 1
        c_ax.plot(step_marker, [c_avg_max]*len(step_marker),
                self.graph_pattern[marker], lw=3, ms=10, label='Avg Max CPU usage')
        marker += 1
        c_ax.plot(step_marker, [c_avg_min]*len(step_marker),
                self.graph_pattern[marker], lw=3, ms=10, label='Avg Min CPU usage')
        marker += 1


        fontsize = 25
        c_ax.set_xlabel('Time (s)',  fontsize=fontsize)
        c_ax.set_ylabel('CPU usage (%)', fontsize=fontsize)
        c_ax.set_title('CPU Usage Criteria', fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        c_ax.grid(True)
        c_fig.savefig(self.output_path +
                    '/fig-cpu-criteria.png')
        plt.close()


    def build_image_size(self, results):
        c_fig = plt.figure()
        c_fig.set_size_inches(18.5, 10.5)
        c_ax = c_fig.add_subplot(111)

        m_fig = plt.figure()
        m_fig.set_size_inches(18.5, 10.5)
        m_ax = m_fig.add_subplot(111)

        marker = 0
        image_size_labels = ['%sx%s'%imgs for imgs in IMAGE_SIZES]
        image_size_pixels = [imgs[0]*imgs[1] for imgs in IMAGE_SIZES]

        for m_results in results:
            cpu_mean = []
            cpu_avg_max = []
            cpu_avg_min = []

            mem_mean = []
            mem_avg_max = []
            mem_avg_min = []

            for image_size in IMAGE_SIZES:
                image_results = m_results['results'][str(DEFAULT_FPS)]['%sx%s'%image_size][DEFAULT_VIDEO_ANALYSIS]['results']
                cpu_results = [r['cpu_used'] for r in image_results][self.start: self.end]
                mem_results = [r['memory_used'] for r in image_results][self.start: self.end]

                c_mean = numpy.mean(cpu_results)
                c_avg_max = numpy.mean([c for c in cpu_results if c >= c_mean])
                c_avg_min = numpy.mean([c for c in cpu_results if c < c_mean])

                cpu_mean.append(c_mean)
                cpu_avg_max.append(c_avg_max)
                cpu_avg_min.append(c_avg_min)

                m_mean = numpy.mean(mem_results)
                m_avg_max = numpy.mean([m for m in mem_results if m >= m_mean])
                m_avg_min = numpy.mean([m for m in mem_results if m < m_mean])

                mem_mean.append(m_mean)
                mem_avg_max.append(m_avg_max)
                mem_avg_min.append(m_avg_min)

            #print('   cmean:', len(cpu_mean))
            #print('mincmean:', len(cpu_avg_min))
            #print('maxcmean:', len(cpu_avg_max))

            c_ax.plot(image_size_pixels, cpu_mean,
                    self.graph_pattern[marker], label='mean of CPU usage %s' % m_results['machine_specification']['cpu_frequency'])
            m_ax.plot(image_size_pixels, mem_mean,
                    self.graph_pattern[marker], label='mean of memory usage %s' % m_results['machine_specification']['cpu_frequency'])
            marker += 1
            #ax.plot(FPSS, cpu_avg_max,
                    #self.graph_pattern[marker], label='average maximum CPU usage')
            #marker += 1
            #ax.plot(FPSS, cpu_avg_min,
                    #self.graph_pattern[marker], label='average minimum CPU usage')
            #marker += 1
            #for X, Y, Z in zip(image_size_pixels, cpu_mean, image_size_label):
                # Annotate the points 5 _points_ above and to the left of the vertex
            #    c_ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(-5, 5), ha='right',
            #        textcoords='offset points')


        fontsize = 25
        c_ax.set_xlabel('Image Size (pixels)',  fontsize=fontsize)
        c_ax.set_ylabel('CPU usage (%)', fontsize=fontsize)
        c_ax.set_title('CPU Usage Image Size', fontsize=fontsize)
        c_ax.legend(prop={'size': fontsize}, loc=0)
        c_ax.tick_params(labelsize=fontsize)
        c_ax.set_xticks(image_size_pixels)
        c_ax.set_xticklabels(image_size_labels)
        c_ax.grid(True)
        c_fig.savefig(self.output_path +
                    '/fig-cpu-image-size.png')

        m_ax.set_xlabel('Image Size (pixels)',  fontsize=fontsize)
        m_ax.set_ylabel('Memory usage (Mb)', fontsize=fontsize)
        m_ax.set_title('Memory Usage Criteria', fontsize=fontsize)
        m_ax.legend(prop={'size': fontsize}, loc=0)
        m_ax.tick_params(labelsize=fontsize)
        m_ax.set_xticks(image_size_pixels)
        m_ax.set_xticklabels(image_size_labels)
        m_ax.grid(True)
        m_fig.savefig(self.output_path +
                    '/fig-mem-image-size.png')

        plt.close(c_fig)
        plt.close(m_fig)

    def build_frequency(self, results):
        c_fig = plt.figure()
        c_fig.set_size_inches(18.5, 10.5)
        c_ax = c_fig.add_subplot(111)

        m_fig = plt.figure()
        m_fig.set_size_inches(18.5, 10.5)
        m_ax = m_fig.add_subplot(111)

        marker = 0


        for m_results in results:
            cpu_mean = []
            cpu_avg_max = []
            cpu_avg_min = []

            mem_mean = []
            mem_avg_max = []
            mem_avg_min = []

            for i in FPSS:
                image_results = m_results['results'][str(i)]['%sx%s'%DEFAULT_IMAGE_SIZE][DEFAULT_VIDEO_ANALYSIS]['results']
                cpu_results = [r['cpu_used'] for r in image_results][self.start: self.end]
                mem_results = [r['memory_used'] for r in image_results][self.start: self.end]

                c_mean = numpy.mean(cpu_results)
                c_avg_max = numpy.mean([c for c in cpu_results if c >= c_mean])
                c_avg_min = numpy.mean([c for c in cpu_results if c < c_mean])

                cpu_mean.append(c_mean)
                cpu_avg_max.append(c_avg_max)
                cpu_avg_min.append(c_avg_min)

                m_mean = numpy.mean(mem_results)
                m_avg_max = numpy.mean([m for m in mem_results if m >= m_mean])
                m_avg_min = numpy.mean([m for m in mem_results if m < m_mean])

                mem_mean.append(m_mean)
                mem_avg_max.append(m_avg_max)
                mem_avg_min.append(m_avg_min)

            #print('   cmean:', len(cpu_mean))
            #print('mincmean:', len(cpu_avg_min))
            #print('maxcmean:', len(cpu_avg_max))

            c_ax.plot(FPSS, cpu_mean,
                    self.graph_pattern[marker], label='mean of CPU usage %s' % m_results['machine_specification']['cpu_frequency'])
            m_ax.plot(FPSS, mem_mean,
                    self.graph_pattern[marker], label='mean of memory usage %s' % m_results['machine_specification']['cpu_frequency'])
            marker += 1
            #ax.plot(FPSS, cpu_avg_max,
                    #self.graph_pattern[marker], label='average maximum CPU usage')
            #marker += 1
            #ax.plot(FPSS, cpu_avg_min,
                    #self.graph_pattern[marker], label='average minimum CPU usage')
            #marker += 1


        fontsize = 25
        c_ax.set_xlabel('FPS',  fontsize=fontsize)
        c_ax.set_ylabel('CPU usage (%)', fontsize=fontsize)
        c_ax.set_title('CPU Usage Criteria', fontsize=fontsize)
        c_ax.legend(prop={'size': fontsize}, loc=0)
        c_ax.tick_params(labelsize=fontsize)
        c_ax.grid(True)
        c_fig.savefig(self.output_path +
                    '/fig-cpu-frequency.png')

        m_ax.set_xlabel('FPS',  fontsize=fontsize)
        m_ax.set_ylabel('Memory usage (Mb)', fontsize=fontsize)
        m_ax.set_title('Memory Usage Criteria', fontsize=fontsize)
        m_ax.legend(prop={'size': fontsize}, loc=0)
        m_ax.tick_params(labelsize=fontsize)
        m_ax.grid(True)
        m_fig.savefig(self.output_path +
                    '/fig-mem-frequency.png')

        plt.close(c_fig)
        plt.close(m_fig)

    def build(self):

        selected_results = self.results[-1]
        image_results = selected_results['results'][str(DEFAULT_FPS)]['%sx%s'%DEFAULT_IMAGE_SIZE][DEFAULT_VIDEO_ANALYSIS]['results']
        print('CPU criteria: FPS=',DEFAULT_FPS, 'image size=%sx%s'%DEFAULT_IMAGE_SIZE, 'analysis=', DEFAULT_VIDEO_ANALYSIS)
        print('machine_specification', selected_results['machine_specification'])
        self.build_cpu_criteria(image_results)
        self.build_frequency(self.results)
        self.build_image_size(self.results)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-i', '--input',
                        help='benchmark input')
    parser.add_argument('-o', '--output',
                        help='performance result')

    args = parser.parse_args()
    print('args:', args)

    if not os.path.exists(args.input):
        print('file does not exist')
        sys.exit()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    gb = GraphBuilder(args.input, args.output)
    gb.build()

