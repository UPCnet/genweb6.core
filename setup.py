# -*- coding: utf-8 -*-
"""Installer for the genweb6.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='genweb6.core',
    version='1.0a1',
    description="Genweb 6 Core package",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Plone Team',
    author_email='ploneteam@upcnet.es',
    url='https://github.com/collective/genweb6.core',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/genweb6.core',
        'Source': 'https://github.com/collective/genweb6.core',
        'Tracker': 'https://github.com/collective/genweb6.core/issues',
        # 'Documentation': 'https://genweb6.core.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['genweb6'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api',
        'plone.restapi',
        'plone.app.dexterity',
        'ipdb',
        'souper.plone',
        'Products.PloneLDAP',
        'Products.LDAPUserFolder',
        'Products.LDAPMultiPlugins',
        'dataflake.fakeldap',
        'pyquery',
        'plone.app.form',
        'plone.formwidget.contenttree',
        'pdfkit',
        'plone.formwidget.recaptcha',
        'collective.easyform',
        'ftw.casauth',
        'collective.exportimport',
        'collective.siteimprove',
    ],

    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = genweb6.core.locales.update:update_locale
    """,
)
