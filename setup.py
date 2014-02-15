from setuptools import setup

with open('README.md') as file:
    # Try my best to have at least the intro in Markdown/reST.
    long_description = file.read().partition('<!-- END long_description -->')[0]

with open('requirements.txt') as file:
    # Keep a requirements file to make it easy to use pip and Travis.
    requires = file.read().splitlines()

setup(name='caniusepython3',
      version='1.0',
      description='Determine what projects are blocking you from porting to Python 3',
      long_description=long_description,
      author='Brett Cannon',
      author_email='brett@python.org',
      url='https://github.com/brettcannon/caniusepython3',
      py_modules=['caniusepython3'],
      install_requires=requires,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': [
              'caniusepython3=caniusepython3:main',
          ]
      },
)
