from setuptools import setup, find_packages
import os

version = '1.0b4'

setup(name='collective.sugarcrm',
      version=version,
      description="SugarCRM components for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='JeanMichel FRANCOIS aka toutpt',
      author_email='toutpt@makina-corpus.org',
      url='http://svn.plone.org/svn/collective/collective.sugarcrm',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'suds',
          'z3c.suds'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
