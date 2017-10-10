from setuptools import setup

setup(name='testing_nt',
      version='0.1',
      description='ig2 testing for nt',
      url='http://github.com/scharczynski/testing_nt',
      author='scharczynski',
      author_email='scharczynski@gmail.com',
      packages=['testing_nt'],
      install_requires=[
          'hypothesis',
          'pytest',
          'pexpect',
          'pyepics',
          'numpy',
      ],
      zip_safe=False)