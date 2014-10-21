'''
Created on Oct 3, 2014

@author: boatkrap
'''

import unittest
from nokkhum import config
import os
from nokkhum.compute.benchmark import Benchmark


class TestBenchmark(unittest.TestCase):
    def setUp(self):
        configurator = config.Configurator('/home/boatkrap/VSaaS/nokkhum/compute-config.ini')

        directory = configurator.settings.get('nokkhum.log_dir')
        if not os.path.exists(directory):
            os.makedirs(directory)

        record_directory = configurator.settings.get('nokkhum.processor.record_path')
        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

    def tearDown(self):
        pass
    

    def test_benchmark(self):
        from nokkhum.compute import benchmark
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
        
        def do_benchmark(cameras, process_period=2):
        
            attributes = {"image_processors": [{"name": "None Processor"}],
                          "cameras": cameras
                          }
            
            bm = benchmark.Benchmark('test_benchmark_aquisition', process_period)
            bm.start(attributes)
            bm.wait()
            
            attributes = {"image_processors": [{"name": "Motion Detector",
                                                "wait_motion_time": 5,
                                                "interval": 3,
                                                "sensitive": 95,
                                                "image_processors":[{"name": "None Processor"}]}],
                          "cameras": cameras
                          }
    
            bm = benchmark.Benchmark('test_benchmark_motion_detector')
            bm.start(attributes)
            bm.wait()
            
            attributes = {"image_processors": [{"name": "Video Recorder",
                                                "fps": 10,
                                                "height": cameras[0]['height'],
                                                "width": cameras[0]['width'],
                                                "directory": "/tmp/nokkhum-records/test_benchmark"
                                                }],
                          "cameras": cameras
                          }
    
            bm = benchmark.Benchmark('test_benchmark_video_recorder')
            bm.start(attributes)
            return bm.wait()
        
        
        print("image size: 320x240")
        result = do_benchmark(cameras, 2)
        jresult = result.to_json()
        self.assertIn('results', jresult)
        self.assertGreater(len(jresult), 0)
        
        print("image size: 640x480")
        cameras[0]["height"] = 480
        cameras[0]["width"] = 640
        result = do_benchmark(cameras, 2)
        jresult = result.to_json()
        self.assertIn('results', jresult)
        self.assertGreater(len(jresult), 0)
        
        print("image size: 960x720")
        cameras[0]["height"] = 720
        cameras[0]["width"] = 960
        result = do_benchmark(cameras, 2)
        jresult = result.to_json()
        self.assertIn('results', jresult)
        self.assertGreater(len(jresult), 0)
