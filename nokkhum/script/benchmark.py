'''
Created on Oct 29, 2014

@author: boatkrap
'''


from nokkhum import config
import os
import json
import datetime
import sys
import errno
from nokkhum.compute import benchmark

from matplotlib import pyplot as plt
import numpy


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class GraphBuilder:
    def __init__(self, data):
        self.data = data

    def build(self):
        # aquisition

        fig_aq_cpu = plt.figure()
        fig_aq_cpu.set_size_inches(18.5, 10.5)

        ax = fig_aq_cpu.add_subplot(111)

        print("xxx:", self.data['320x240']['Acquisition']['results'])
        ax.plot([a['cpu_used'] for a in self.data['320x240']['Acquisition']['results']][50:150], '-o', label="320x240 pixels")
        ax.plot([a['cpu_used'] for a in self.data['640x480']['Acquisition']['results']][50:150], '-^', label="640x480 pixels")
        ax.plot([a['cpu_used'] for a in self.data['960x720']['Acquisition']['results']][50:150], '-x', label="960x720 pixels")

        print("self.data['320x240']['Acquisition']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['320x240']['Acquisition']['results']][50:150]))
        print("self.data['640x480']['Acquisition']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['640x480']['Acquisition']['results']][50:150]))
        print("self.data['960x720 ']['Acquisition']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['960x720']['Acquisition']['results']][50:150]))

        print("self.data['320x240']['Acquisition']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['320x240']['Acquisition']['results']][50:150]))
        print("self.data['640x480']['Acquisition']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['640x480']['Acquisition']['results']][50:150]))
        print("self.data['960x720 ']['Acquisition']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['960x720']['Acquisition']['results']][50:150]))
        
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("CPU used (%)")
        ax.set_title('Image Acquisition CPU Usage')
        plt.legend()
        ax.grid(True)
        fig_aq_cpu.savefig('/tmp/fig_aq_cpu.png')
        fig_aq_cpu.show()

        fig_aq_mem = plt.figure()
        fig_aq_mem.set_size_inches(18.5, 10.5)

        ax = fig_aq_mem.add_subplot(111)

        ax.plot([a['memory_used']/(10**6) for a in self.data['320x240']['Acquisition']['results']][50:150], '-o', label="320x240 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['640x480']['Acquisition']['results']][50:150], '-^', label="640x480 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['960x720']['Acquisition']['results']][50:150], '-x', label="960x720 pixels")

        print("self.data['320x240']['Acquisition']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['320x240']['Acquisition']['results']][50:150]))
        print("self.data['640x480']['Acquisition']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['640x480']['Acquisition']['results']][50:150]))
        print("self.data['960x720 ']['Acquisition']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['960x720']['Acquisition']['results']][50:150]))

        print("self.data['640x480']['Acquisition']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['640x480']['Acquisition']['results']][50:150]))
        print("self.data['960x720 ']['Acquisition']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['960x720']['Acquisition']['results']][50:150]))

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Memory used (MB)")
        ax.set_title('Image Acquisition Memory Usage')
        plt.legend()
        ax.grid(True)
        fig_aq_mem.savefig('/tmp/fig_aq_mem.png')
        fig_aq_mem.show()

        # motion
        fig_mt_cpu = plt.figure()
        fig_mt_cpu.set_size_inches(18.5,10.5)

        ax = fig_mt_cpu.add_subplot(111)

        ax.plot([a['cpu_used'] for a in self.data['320x240']['Motion Detector']['results']][50:150], '-o', label="320x240 pixels")
        ax.plot([a['cpu_used'] for a in self.data['640x480']['Motion Detector']['results']][50:150], '-^', label="640x480 pixels")
        ax.plot([a['cpu_used'] for a in self.data['960x720']['Motion Detector']['results']][50:150], '-x', label="960x720 pixels")

        print("self.data['320x240']['Motion Detector']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['320x240']['Motion Detector']['results']][50:150]))
        print("self.data['640x480']['Motion Detector']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['640x480']['Motion Detector']['results']][50:150]))
        print("self.data['960x720 ']['Motion Detector']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['960x720']['Motion Detector']['results']][50:150]))

        print("self.data['320x240']['Motion Detector']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['320x240']['Motion Detector']['results']][50:150]))
        print("self.data['640x480']['Motion Detector']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['640x480']['Motion Detector']['results']][50:150]))
        print("self.data['960x720 ']['Motion Detector']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['960x720']['Motion Detector']['results']][50:150]))

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("CPU used (%)")
        ax.set_title('Motion Detector CPU Usage')
        plt.legend()
        ax.grid(True)
        fig_mt_cpu.savefig('/tmp/fig_mt_cpu.png')
        fig_mt_cpu.show()

        fig_mt_mem = plt.figure()
        fig_mt_mem.set_size_inches(18.5, 10.5)

        ax = fig_mt_mem.add_subplot(111)

        ax.plot([a['memory_used']/(10**6) for a in self.data['320x240']['Motion Detector']['results']][50:150], '-o', label="320x240 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['640x480']['Motion Detector']['results']][50:150], '-^', label="640x480 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['960x720']['Motion Detector']['results']][50:150], '-x', label="960x720 pixels")

        print("self.data['320x240']['Motion Detector']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['320x240']['Motion Detector']['results']][50:150]))
        print("self.data['640x480']['Motion Detector']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['640x480']['Motion Detector']['results']][50:150]))
        print("self.data['960x720']['Motion Detector']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['960x720']['Motion Detector']['results']][50:150]))

        print("self.data['320x240']['Motion Detector']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['320x240']['Motion Detector']['results']][50:150]))
        print("self.data['640x480']['Motion Detector']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['640x480']['Motion Detector']['results']][50:150]))
        print("self.data['960x720']['Motion Detector']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['960x720']['Motion Detector']['results']][50:150]))

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Memory used (MB)")
        ax.set_title('Motion Detector Memory Usage')
        plt.legend()
        ax.grid(True)
        fig_mt_mem.savefig('/tmp/fig_mt_mem.png')
        fig_mt_mem.show()

        # record
        fig_rd_cpu = plt.figure()
        fig_rd_cpu.set_size_inches(18.5, 10.5)

        ax = fig_rd_cpu.add_subplot(111)

        ax.plot([a['cpu_used'] for a in self.data['320x240']['Video Recorder']['results']][50:150], '-o', label="320x240 pixels")
        ax.plot([a['cpu_used'] for a in self.data['640x480']['Video Recorder']['results']][50:150], '-^', label="640x480 pixels")
        ax.plot([a['cpu_used'] for a in self.data['960x720']['Video Recorder']['results']][50:150], '-x', label="960x720 pixels")

        print("self.data['320x240']['Video Recorder']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['320x240']['Video Recorder']['results']][50:150]))
        print("self.data['640x480']['Video Recorder']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['640x480']['Video Recorder']['results']][50:150]))
        print("mself.data['960x720']['Video Recorder']['results'] cpu mean:", numpy.mean([a['cpu_used'] for a in self.data['960x720']['Video Recorder']['results']][50:150]))

        print("self.data['320x240']['Video Recorder']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['320x240']['Video Recorder']['results']][50:150]))
        print("self.data['640x480']['Video Recorder']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['640x480']['Video Recorder']['results']][50:150]))
        print("self.data['960x720']['Video Recorder']['results'] cpu std:", numpy.std([a['cpu_used'] for a in self.data['960x720']['Video Recorder']['results']][50:150]))

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("CPU used (%)")
        ax.set_title('VDO Recorder CPU Usage')
        plt.legend()
        ax.grid(True)
        fig_rd_cpu.savefig('/tmp/fig_rd_cpu.png')
        fig_rd_cpu.show()

        fig_rd_mem = plt.figure()
        fig_rd_mem.set_size_inches(18.5,10.5)

        ax = fig_rd_mem.add_subplot(111)

        ax.plot([a['memory_used']/(10**6) for a in self.data['320x240']['Video Recorder']['results']], '-o', label="320x240 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['640x480']['Video Recorder']['results']], '-^', label="640x480 pixels")
        ax.plot([a['memory_used']/(10**6) for a in self.data['960x720']['Video Recorder']['results']], '-x', label="960x720 pixels")

        print("self.data['320x240']['Video Recorder']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['320x240']['Video Recorder']['results']][50:150]))
        print("self.data['640x480']['Video Recorder']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['640x480']['Video Recorder']['results']][50:150]))
        print("self.data['960x720']['Video Recorder']['results'] memory mean:", numpy.mean([a['memory_used']/(10**6) for a in self.data['960x720']['Video Recorder']['results']][50:150]))

        print("self.data['320x240']['Video Recorder']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['320x240']['Video Recorder']['results']][50:150]))
        print("self.data['640x480']['Video Recorder']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['640x480']['Video Recorder']['results']][50:150]))
        print("self.data['960x720']['Video Recorder']['results'] memory std:", numpy.std([a['memory_used']/(10**6) for a in self.data['960x720']['Video Recorder']['results']][50:150]))

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Memory used (MB)")
        ax.set_title('VDO Recorder Memory Usage')
        plt.legend()
        ax.grid(True)
        fig_rd_mem.savefig('/tmp/fig_rd_mem.png')


class BenchmarkReport():
    def __init__(self):
        pass

    def do_benchmark(self, cameras, process_period=2):

        results = dict()
        attributes = {"image_processors": [{"name": "None Processor"}],
                      "cameras": cameras
                      }

        bm = benchmark.Benchmark('test_benchmark_aquisition', process_period)
        bm.start(attributes)
        result = bm.wait()
        results['Acquisition'] = result.to_dict()

        attributes = {"image_processors": [{"name": "Motion Detector",
                                            "wait_motion_time": 5,
                                            "interval": 3,
                                            "sensitive": 95,
                                            "image_processors":[{"name": "None Processor"}]}],
                      "cameras": cameras
                      }

        bm = benchmark.Benchmark('test_benchmark_motion_detector')
        bm.start(attributes)
        result = bm.wait()
        results['Motion Detector'] = result.to_dict()

        attributes = {"image_processors": [{"name": "Video Recorder",
                                            "fps": 10,
                                            "height": cameras[0]['height'],
                                            "width": cameras[0]['width'],
                                            "directory": "/tmp/nokkhum-records/test_benchmark"
                                            }],
                      "cameras": cameras
                      }

        bm = benchmark.Benchmark('test_benchmark_video_recorder', 10)
        bm.start(attributes)
        result = bm.wait()
        results['Video Recorder'] = result.to_dict()

        return results

    def benchmark(self):

        cameras = [{"width": 320,
                    "name": "camera-02",
                    "height": 240,
                    "fps": 10,
                    "image_uri": "http://admin:@172.30.235.51/image/jpeg.cgi",
                    "username": "admin",
                    "model": "DCS-930L",
                    "audio_uri": "http://admin:@172.30.235.51/audio.cgi",
                    "video_uri": "http://admin:@172.30.235.51/video/mjpg.cgi?.mjpg",
                    "id": "527836e024b5b108ba95a1a0",
                    "password": ""}]

        results = dict()
        print("image size: 320x240")
        result = self.do_benchmark(cameras, 2)
        results['320x240'] = result

        print("image size: 640x480")
        cameras[0]["height"] = 480
        cameras[0]["width"] = 640
        result = self.do_benchmark(cameras, 2)
        results['640x480'] = result

        print("image size: 960x720")
        cameras[0]["height"] = 720
        cameras[0]["width"] = 960
        result = self.do_benchmark(cameras, 2)
        results['960x720'] = result

        with open('/tmp/xxx.json', 'w') as f:
            print("dump to json")
            json.dump(results, f, cls=DateTimeJSONEncoder)

        print('finish benchmark')

    def graph(self, results, show=False):
        graph = GraphBuilder(results)
        graph.build()

        if show:
            plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write( "Use: " + sys.argv[0] + "cmd")
        sys.stderr.write("cmd: analyze config_file")
        sys.stderr.write("cmd: graph show=true results.json")
        sys.exit(errno.EINVAL)

    if sys.argv[1] == 'analyze':
        configurator = config.Configurator(sys.argv[2])

        directory = configurator.settings.get('nokkhum.log_dir')
        if not os.path.exists(directory):
            os.makedirs(directory)

        record_directory = configurator.settings.get('nokkhum.processor.record_path')
        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

        br = BenchmarkReport()
        br.benchmark()

    if sys.argv[1] == 'graph':
        show = True if sys.argv[2].split('=')[1] in ['True', 'true'] else False

        with open(sys.argv[3], "r") as f:
            results = json.load(f)
            br = BenchmarkReport()
            br.graph(results, show)
