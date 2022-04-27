# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import genweb5.core


class Genweb5CoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=genweb5.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'genweb5.core:default')


GENWEB_FIXTURE = Genweb5CoreLayer()


GENWEB_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENWEB5_CORE_FIXTURE,),
    name='Genweb5CoreLayer:IntegrationTesting',
)


GENWEB_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENWEB5_CORE_FIXTURE,),
    name='Genweb5CoreLayer:FunctionalTesting',
)


GENWEB_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        GENWEB5_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='Genweb5CoreLayer:AcceptanceTesting',
)
