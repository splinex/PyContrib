from setuptools import setup

setup(name='pycontrib',
      version='1.0',
      install_requires=['psutil',
                        'tornado>=4.3',
                        'motor>=0.6'],
      packages=['pycontrib',
                'pycontrib.service',
                'pycontrib.misc',
                'pycontrib.os',
                'pycontrib.monguo',
                'pycontrib.async'
                ],
      )
