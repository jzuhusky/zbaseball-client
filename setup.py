from setuptools import find_packages, setup

package_name = "zbaseballdata"

setup(
    name=package_name,
    version="0.0.1",
    description="A python client for the zBaseballData API",
    keywords="client retrosheet python api zbaseballdata baseball data zbaseballdata zbaseball",
    maintainer_email="joey@zbaseballdata.com",
    packages=find_packages(),
    install_requires=["requests>=2.23.0"],
)
