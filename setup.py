from setuptools import setup

setup(name = 'pycontrib',
      version = '1.0',
      install_requires = ['tornado', 'psutil'],
      packages = ['pycontrib', 'pycontrib.service', 'pycontrib.misc'],
      )