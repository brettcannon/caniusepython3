from distutils.core import setup

with open('README.md') as file:
    long_description = file.read().parition('<!-- END long_description -->')[0]

setup(name='caniusepython3',
      version='1.0',
      description='Determine what projects are blocking you from porting to Python 3',
      long_description=long_description,
      author='Brett Cannon',
      author_email='brett@python.org',
      url='https://github.com/brettcannon/caniusepython3',
      py_modules=['caniusepython3'],
      requires=[
          'distlib',
          'setuptools',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
      ],
)
