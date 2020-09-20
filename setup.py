from setuptools import find_packages, setup

package_name = "zbaseballdata"

setup(
    name=package_name,
    version="0.2.0",
    description="A python client for the zBaseballData API",
    url="https://github.com/jzuhusky/zbaseball-client",
    keywords="client retrosheet python api zbaseballdata baseball data zbaseballdata zbaseball",
    maintainer_email="joey@zbaseballdata.com",
    packages=find_packages(),
    install_requires=["requests>=2.23.0"],
)
