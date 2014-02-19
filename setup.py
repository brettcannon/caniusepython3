from setuptools import setup

with open('README.md') as file:
    # Try my best to have at least the intro in Markdown/reST.
    long_description = file.read().partition('<!-- END long_description -->')[0]

setup(name='caniusepython3',
      version='1.0',
      description='Determine what projects are blocking you from porting to Python 3',
      long_description=long_description,
      author='Brett Cannon',
      author_email='brett@python.org',
      url='https://github.com/brettcannon/caniusepython3',
      py_modules=['caniusepython3'],
      setup_requires=['setuptools'],
      install_requires=['distlib', 'pip'],
      test_require=['mock'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
      ],
      entry_points={
          'console_scripts': [
              'caniusepython3=caniusepython3:main',
          ]
      },
      zip_safe=True,
)
