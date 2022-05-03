# -*- coding: utf-8 -*-
"""Installer for the genweb5.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='genweb5.core',
    version='1.0a1',
    description="Genweb 5 core package",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Plone Team',
    author_email='plone.team@upcnet.es',
    url='https://github.com/collective/genweb5.core',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/genweb5.core',
        'Source': 'https://github.com/collective/genweb5.core',
        'Tracker': 'https://github.com/collective/genweb5.core/issues',
        # 'Documentation': 'https://genweb5.core.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['genweb5'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi < 8.0.0',
        'plone.app.dexterity',
        'ipdb',
        'souper.plone',
        'Products.LDAPUserFolder',
        'Products.LDAPMultiPlugins',
        'pyquery',
        'plone.app.form',
        'plone.formwidget.contenttree',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = genweb5.core.locales.update:update_locale
    """,
)
