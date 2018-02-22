# python3 setup.py sdist
# python3 setup.py bdist_wheel
# python3 setup.py bdist_egg
# twine upload dist/*.* [-r testpypi]
# -> automated in tools/make-dist.sh

from setuptools import setup
import os

setup(
	name="faasconverter",
	description="Function as a service converter",
	version="0.0.1",
	url="https://github.com/walter-bd/faas-converter",
	author="Walter Benitez",
	author_email="walterbenitez7@gmail.com",
	license="Apache 2.0",
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Environment :: Console",
		"Environment :: No Input/Output (Daemon)",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: Python :: 3",
		"Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware"
	],
	keywords="cloud faas serverless functions",
	packages=["faas-converter"],
	scripts=["faasconverter"]
)
