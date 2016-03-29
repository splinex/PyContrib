from setuptools import setup

setup(name = 'pycontrib',
      version = '1.0',
      install_requires = ['psutil'],
      packages = ['pycontrib', 
                  'pycontrib.service', 
                  'pycontrib.misc', 
                  'pycontrib.tornado',
                  'pycontrib.tornado.platform',
                  ],
      )