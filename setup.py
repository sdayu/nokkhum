import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'mongoengine',
    'kombu',
    ]

SCRIPT_NAME = 'nokkhum-controller'
setup(name='nokkhum-controller',
      version='0.0',
      description='nokkhum-controller',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: nokkhum",
        ],
      author='Thanathip Limna',
      author_email='boatkrap@gmail.com',
      scripts = ['bin/%s' % SCRIPT_NAME],
      license = 'xxx License',
      packages = find_packages(),
      url='https://github.com/sdayu/nokkhum-controller',
      keywords='VSaaS',
#      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
#      tests_require=requires,
#      test_suite="nokkhum-controller",
      )

