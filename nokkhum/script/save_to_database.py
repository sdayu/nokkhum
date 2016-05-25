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
import csv

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
    def __init__(self, data, output_path=None):
        self.data = data
        self.results = data['results']

        self.start = 5
        self.end = 150

        self.output_path = output_path
        if output_path:
            if not os.path.exists(output_path):
                os.mkdir(output_path)

        settings = {'mongodb.db_name': 'nokkhum', 'mongodb.host':'localhost'}
        models.initial(settings)

        # self.graph_pattern = ['-o', '-H', '-^', '-s', '-D', '-*', '-p',
        #                       '-v', '-8', '-<', '->']

    def process(self):
        print("ms:", self.data['machine_specification'])
        machine_specification = self.data['machine_specification']
        del machine_specification['ip']
        ms = models.MachineSpecification(**machine_specification)

        csvwriter = None

        fieldnames = ['name', 'system', 'machine', 'cpu_model', 'cpu_frequency',
                'cpu_count', 'total_memory', 'total_disk']
        fieldnames.extend([
                        'image_analysis',
                        'image_size',
                        'fps',
                        'avg_cpu',
                        'max_cpu',
                        'min_cpu',
                        'avg_max_cpu',
                        'avg_min_cpu',
                        'avg_memory',
                        'max_memory',
                        'min_memory',
                        'avg_max_memory',
                        'avg_min_memory',
                        'drop_image'])

        if self.output_path:
            csvfile = open(self.output_path+'/%s-%s-%s-result.csv'%(
                machine_specification['name'],
                machine_specification['cpu_frequency'],
                machine_specification['cpu_count']
                ), 'w', newline='')
            if csvfile:
                csvwriter = csv.DictWriter(csvfile, delimiter=' ',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                    fieldnames=fieldnames)
                csvwriter.writeheader()


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
                    avg_cpu = sum(cpu_used)/len(cpu_used)
                    avg_mem = sum(memory_used)/len(memory_used)

                    max_cpu = [c for c in cpu_used if c > avg_cpu]
                    max_mem = [m for m in memory_used if m > avg_mem]

                    min_cpu = [c for c in cpu_used if c < avg_cpu]
                    min_mem = [m for m in memory_used if m < avg_mem]

                    avg_max_cpu = avg_cpu
                    avg_max_mem = avg_mem
                    avg_min_cpu = avg_cpu
                    avg_min_mem = avg_mem

                    if len(max_cpu) > 0:
                        avg_max_cpu = sum(max_cpu)/len(max_cpu)
                    else:
                        print(image_analysis, image_size, 'cpu divided by zero:', avg_cpu)

                    if len(max_mem) > 0:
                        avg_max_mem = sum(max_mem)/len(max_mem)
                    else:
                        print(image_analysis, image_size, 'mem divided by zero:', avg_mem)

                    if len(min_cpu) > 0:
                        avg_min_cpu = sum(min_cpu)/len(min_cpu)
                    else:
                        print(image_analysis, image_size, 'cpu divided by zero:', avg_cpu)

                    if len(min_mem) > 0:
                        avg_min_mem = sum(min_mem)/len(min_mem)
                    else:
                        print(image_analysis, image_size, 'mem divided by zero:', avg_mem)



                    heuristic = dict(
                        max_cpu=max(cpu_used),
                        max_memory=max(memory_used),
                        min_cpu=min(cpu_used),
                        min_memory=min(memory_used),
                        avg_cpu=avg_cpu,
                        avg_memory=avg_mem,
                        avg_max_cpu=avg_max_cpu,
                        avg_max_memory=avg_max_mem,
                        avg_min_cpu=avg_min_cpu,
                        avg_min_memory=avg_min_mem,
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

                    if csvwriter:
                        result = machine_specification.copy()
                        result.update(heuristic)
                        result.update({
                                'image_analysis': image_analysis,
                                'image_size': image_size,
                                'fps': fps,
                            })
                        csvwriter.writerow(result)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input',
                        help='input result')
    parser.add_argument('-o', '--output',
                        help='output result')

    args = parser.parse_args()
    print('args:', args)

    with open(args.input, 'r') as f:
        results = json.load(f)
        a = DatabaseImporter(results, args.output)
        a.process()
        print("finish")
