'''
Created on Oct 2, 2014

@author: boatkrap
'''

from .processors import processors

import time
import datetime

import psutil


class BenchmarkResult:
    def __init__(self,
                 started_date=datetime.datetime.now(),
                 endded_date=datetime.datetime.now(),
                 results=[],
                 process_period=0,
                 attributes=None,
                 stdout=[],
                 stderr=[]):
        self.results = results
        self.started_date = datetime.datetime.now()
        self.ended_date = datetime.datetime.now()
        self.stdout = stdout
        self.stderr = stderr
        self.process_period = process_period
        self.attributes = attributes

    def to_dict(self):
        benchmark_result = dict(started_date=self.started_date.isoformat(),
                                ended_date=self.ended_date.isoformat(),
                                results=self.results,
                                attributes=self.attributes,
                                stdout=self.stdout,
                                stderr=self.stderr,
                                process_period=self.process_period)
        return benchmark_result


class Benchmark:
    def __init__(self, benchmarke_id, process_period=5):
        self.benchmark_id = benchmarke_id
        self.processor = processors.ImageProcessor(self.benchmark_id)
        self.process_period = process_period
        self.started_date = None
        self.ended_date = None
        self.attributes = None

    def start(self, attributes):
        surveillance_attibutes = attributes
        self.processor.start(surveillance_attibutes)
        self.started_date = datetime.datetime.now()
        self.attributes = attributes
        print(self.benchmark_id)
        print("start: ", self.started_date)

        print("get pid:", self.processor.get_pid())

    def wait(self):

        process = psutil.Process(self.processor.get_pid())
        results = []
        while self.processor.is_running():
            time.sleep(1)

            result = dict(reported_date=datetime.datetime.now(),
                          cpu_used=process.get_cpu_percent(),
                          memory_used=process.get_memory_info().rss,
                          )

            results.append(result)

            if datetime.datetime.now() - self.started_date > datetime.timedelta(minutes=self.process_period):
                self.processor.stop()
                break

        self.ended_date = datetime.datetime.now()

        stdout = []
        stderr = []
        for line in self.processor.process.stdout:
            stdout.append(line.decode('utf-8'))

        for line in self.processor.process.stderr:
            stderr.append(line.decode('utf-8'))

        b_result = BenchmarkResult(started_date=self.started_date,
                                   endded_date=self.ended_date,
                                   results=results,
                                   attributes=self.attributes,
                                   process_period=self.process_period,
                                   stdout=stdout,
                                   stderr=stderr)

        return b_result
