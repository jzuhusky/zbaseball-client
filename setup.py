from setuptools import find_packages, setup

package_name = 'zbaseball'

setup(name=package_name,
      version='0.0.1',
      description='A python client for the zBaseballData API',
      keywords='client python api zbaseball baseball data zbaseballdata',
      maintainer_email='joey@zbaseballdata.com',
      packages=find_packages(),
      install_requires=[
          'schematics==1.1.1',
          'requests>=2.13.0',
          'six>=1.11.0,<2',
      ],
    )
