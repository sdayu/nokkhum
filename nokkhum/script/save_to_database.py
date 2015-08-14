'''
Created on Oct 29, 2014

@author: boatkrap
'''


from nokkhum import config
from nokkhum import models
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


class DatabaseImporter:
    def __init__(self, data):
        self.data = data
        self.results = data['results']

        self.start = 5
        self.end = 150

        settings = {'mongodb.db_name': 'nokkhum', 'mongodb.host':'localhost'}
        models.initial(settings)

        # self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
        #                       '-v', '-8', '-<', '->']

    def process(self):
        print("xxx:", self.data['machine_specification'])
        machine_specification = self.data['machine_specification']
        del machine_specification['ip']
        ms = models.MachineSpecification(**machine_specification)

        for fps, image_size_results in self.results.items():
            for image_size, image_analysis_results in image_size_results.items():
                for image_analysis, results in image_analysis_results.items():
                    cpu_used = [result['cpu_used'] for result in results['results'][self.start: self.end]]
                    memory_used = [result['memory_used'] for result in results['results'][self.start: self.end]]

                    is_drop_image = False
                    if len(results['stderr']) > 0:
                        for stderr_re in results['stderr']:
                            try:
                                obj = json.loads(stderr_re)
                                if obj['method'] == 'drop_image_from_queue':
                                    is_drop_image = True
                                    break
                            except:
                                print("load error:", stderr_re)
                    # print('results:', results['stderr'])
                    heuristic = dict(max_cpu_used=max(cpu_used),
                        max_memory_used=max(memory_used),
                        drop_image=is_drop_image
                        )

                    ipe = models.ImageProcessingExperiment.objects(machine_specification=ms,
                        image_analysis=image_analysis,
                        video_size=map(int,image_size.split('x')),
                        fps=int(fps)).first()

                    if ipe:
                        ipe.results=results
                        ipe.heuristic=heuristic
                    else:
                        ipe = models.ImageProcessingExperiment(machine_specification=ms,
                                                   results=results,
                                                   image_analysis=image_analysis,
                                                   video_size=map(int,image_size.split('x')),
                                                   fps=int(fps),
                                                   heuristic=heuristic
                                                   )
                    ipe.save()

                    #print("ipe:", ipe.__dict__)
                    # print(', '.join([fps,
                    #                     image_size,
                    #                     image_analysis,
                    #                     str(max(cpu_used)),
                    #                     str(min(cpu_used)),
                    #                     str(sum(cpu_used)/len(cpu_used)),
                    #                     str(max(memory_used)),
                    #                     str(min(memory_used)),
                    #                     str(sum(memory_used)/len(memory_used)),
                    #                 ]))
                    # print(max([result['cpu_used'] for result in results['results']]))



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input',
                        help='input result')

    args = parser.parse_args()
    print('args:', args)

    with open(args.input, 'r') as f:
        results = json.load(f)
        a = DatabaseImporter(results)
        a.process()
        print("finish")
