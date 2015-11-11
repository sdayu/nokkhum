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

    def build_cpu_graph(self, image_size_results, key='Acquisition',
                        title="", fps=0):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        maker = 0


#         for image_size, results in image_size_results.items():
        for image_size in IMAGE_SIZES:
            results = image_size_results['%sx%s'%image_size]

            print("image size %sx%s:" % image_size)

            ax.plot([r['cpu_used'] for r in results[key]['results']][self.start: self.end],
                    self.graph_pattern[maker], label="%sx%s pixels" % image_size)
            maker += 1

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
        # fig.show()
        plt.close(fig)

    def build_memory_graph(self, image_size_results, key='Acquisition',
                           title="", fps=0):
        fig = plt.figure()
        fig.set_size_inches(18.5, 10.5)
        ax = fig.add_subplot(111)
        maker = 0

        for image_size in IMAGE_SIZES:
            results = image_size_results['%sx%s'%image_size]

            ax.plot([a['memory_used']/(10**6) for a in results[key]['results']][self.start: self.end],
                    self.graph_pattern[maker], label="%sx%s pixels" % image_size)
            maker += 1
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
        ax.set_ylabel("Memory usage (MB)", fontsize=fontsize)
        ax.set_title('Memory Usage of ' + title, fontsize=fontsize)
        plt.legend(prop={'size': fontsize})
        plt.tick_params(labelsize=fontsize)
        ax.grid(True)
        fig.savefig(self.output_path +
                    '/fig-%sfps-%s-memory.png' % (fps, key.replace(" ", "-")))
        # fig.show()
        plt.close(fig)

    def build(self, show):
        # aquisition

        for fps, image_size_results in self.results.items():

            # for processing motion acquisition
            print("process acquisition")
            print("process graph FPS:", fps)

            self.build_cpu_graph(image_size_results, 'Acquisition',
                                 'Image Acquisition', fps)
            self.build_memory_graph(image_size_results, 'Acquisition',
                                    'Image Acquisition', fps)

            # for processing motion detector
            print("process motion detector")
            self.build_cpu_graph(image_size_results, 'Motion Detector',
                                 'Motion Detector', fps)
            self.build_memory_graph(image_size_results, 'Motion Detector',
                                    'Motion Detector', fps)

            # for processing video recorder
            self.build_cpu_graph(image_size_results, 'Video Recorder',
                                 'Video Recorder', fps)
            self.build_memory_graph(image_size_results, 'Video Recorder',
                                    'Video Recorder', fps)

            # for processing video recorder
            self.build_cpu_graph(image_size_results, 'Motion Recorder',
                                 'Motion Recorder', fps)
            self.build_memory_graph(image_size_results, 'Motion Recorder',
                                    'Motion Recorder', fps)


class BenchmarkReport():
    def __init__(self, video_path, video_prefix, video_type, output_file):
        self.output_file = output_file
        self.video_path = video_path
        self.video_prefix = video_prefix
        self.video_type = video_type

    def do_benchmark(self, cameras, process_period=2):

        results = dict()
        attributes = {"image_processors": [{"name": "None Processor"}],
                      "cameras": cameras
                      }

        camera = cameras[0]

        bm = benchmark.Benchmark('test_benchmark_aquisition_%sfps_%sx%s'%(camera['fps'], camera['width'], camera['height']), process_period)
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

        bm = benchmark.Benchmark('test_benchmark_motion_detector_%sfps_%sx%s'%(camera['fps'], camera['width'], camera['height']), process_period)
        bm.start(attributes)
        result = bm.wait()
        results['Motion Detector'] = result.to_dict()

        attributes = {"image_processors": [{"name": "Video Recorder",
                                            "fps": cameras[0]['fps'],
                                            "height": cameras[0]['height'],
                                            "width": cameras[0]['width'],
                                            "directory": "/tmp/nokkhum-records/test_benchmark"
                                            }],
                      "cameras": cameras
                      }

        bm = benchmark.Benchmark('test_benchmark_video_recorder_%sfps_%sx%s'%(camera['fps'], camera['width'], camera['height']), process_period)
        bm.start(attributes)
        result = bm.wait()
        results['Video Recorder'] = result.to_dict()

        attributes = {"image_processors": [{"name": "Motion Detector",
                                            "wait_motion_time": 5,
                                            "interval": 3,
                                            "sensitive": 95,
                                            "image_processors":[
                                                {"name": "Video Recorder",
                                                    "fps": cameras[0]['fps'],
                                                    "record_motion": True,
                                                    "height": cameras[0]['height'],
                                                    "width": cameras[0]['width'],
                                                    "directory": "/tmp/nokkhum-records/test_benchmark"
                                                    }
                                                ]}],
                      "cameras": cameras
                      }

        bm = benchmark.Benchmark('test_benchmark_motion_recorder_%sfps_%sx%s'%(camera['fps'], camera['width'], camera['height']), process_period)
        bm.start(attributes)
        result = bm.wait()
        results['Motion Recorder'] = result.to_dict()

        return results

    def benchmark(self):
        cameras = [{"width": 0,
                    "name": "camera-02",
                    "height": 0,
                    "fps": 10,
                    "image_uri": "",
                    "username": "",
                    "password": "",
                    "model": "",
                    "audio_uri": "",
                    "video_uri": "",
                    "id": "527836e024b5b108ba95a1a0",
                    }]

        results = dict()

        for fps in FPSS:
            print("Test fps:", fps)
            result_dict = dict()
            for image_size in IMAGE_SIZES:
                print("fps %s image size: %sx%s " % (fps, image_size[0],
                                                     image_size[1]))
                cameras[0]["height"] = image_size[1]
                cameras[0]["width"] = image_size[0]
                cameras[0]["fps"] = fps
                cameras[0]["video_uri"] = "%s/%s-%sx%s-%sfps.%s"\
                    % (self.video_path, self.video_prefix, image_size[0],
                       image_size[1], fps, self.video_type)
                result = self.do_benchmark(cameras, 2)
                result_dict['%sx%s' % (image_size[0], image_size[1])] = result

            results[fps] = result_dict

        ms = machine_specification.MachineSpecification("/home")
        report = dict(
            results=results,
            reported_date=datetime.datetime.now(),
            machine_specification=ms.get_specification()
        )

        with open(self.output_file, 'w') as f:
            print("dump to json")
            json.dump(report, f, cls=DateTimeJSONEncoder)

        print('finish benchmark')

    def graph(self, results, output_path, show=False):
        graph = GraphBuilder(results, output_path)
        graph.build()

        if show:
            plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', choices=['analyze', 'graph'],
                        help='cmd help')

    parser.add_argument('-c', '--ia_config',
                        help='nokkhum compute configuration file')
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
    if args.cmd == 'analyze':

        configurator = config.Configurator(args.ia_config)

        directory = configurator.settings.get('nokkhum.log_dir')
        if not os.path.exists(directory):
            os.makedirs(directory)

        record_directory = configurator.settings.get('nokkhum.processor.record_path')
        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

        br = BenchmarkReport(args.video_path, args.video_prefix,
                             args.video_type, args.output)
        br.benchmark()

    if args.cmd == 'graph':
        with open(args.input, "r") as f:
            results = json.load(f)
            gb = GraphBuilder(results, args.graph_output)
            gb.build(args.show_graph)
