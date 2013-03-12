import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


CONTROLLER = True
COMPUTE_NODE = True

requires = [
    'mongoengine',
    'kombu',
    'psutil',
    'amqp',
    ]


scripts = ['bin/nokkhum-controller', 'bin/nokkhum-compute']
setup(name='nokkhum',
      version='0.0',
      description='Nokkhum Video Surveillance as a Service',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: nokkhum",
        ],
      author='Thanathip Limna',
      author_email='boatkrap@gmail.com',
      scripts = scripts,
      license = 'xxx License',
      packages = find_packages(),
      url='https://github.com/sdayu/nokkhum',
      keywords='VSaaS',
#      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
#      tests_require=requires,
#      test_suite="nokkhum-controller",
      )

