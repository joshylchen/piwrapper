import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="piwrapper",
    version="0.2.0",
    url="https://github.com/joshylchen/piwrapper",
    license='MIT',

    author="Josh Chen",
    author_email="jcpythonlib@gmail.com",

    description="Python connector access OSISOFT PI server via PI Web API.",
    long_description=read("README.rst"),

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        "numpy>=1.21.3",
        "pandas>=1.3.4",
        "python-dateutil>=2.8",
        "requests>=2.26",
        "requests-kerberos>=0.12",
        "tqdm>=4.32",
        "tzlocal>=1.5",
        "urllib3>=1.26.7",],
    python_requires=">=3.6.0",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',        
    ],
)
