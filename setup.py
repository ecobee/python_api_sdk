from setuptools import setup, find_packages

REQUIREMENTS = [ 
          'numpy',
          'pandas',
          'sqlalchemy',
          'pymysql']

setup(
    name="ebapi",
    version="0.1.0",
    author="ecobee datascience team",
    author_email="benm@ecobee.com",
    description="A Python SDK for the ecobee API",
    license="TBD",
    classifiers=[
        'Private :: Do Not Upload to pypi server',
    ],  
    packages=find_packages(),
    install_requires=REQUIREMENTS,
)
