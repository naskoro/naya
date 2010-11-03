"""
Naya
----

Naya is a microframework for Python based on Werkzeug.

See /examples.
"""
from setuptools import setup


setup(
    name='Naya',
    version='0.1',
    url='http://pusto.org/',
    license='BSD',
    author='Grisha aka naspeh',
    author_email='naspeh@ya.ru',
    description='A microframework based on Werkzeug',
    long_description=__doc__,
    packages=['naya'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug>=0.6.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite = 'nose.collector'
)
