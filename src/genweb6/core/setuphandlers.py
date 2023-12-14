# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable

from plone import api
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.formwidget.namedfile.converter import b64encode_file
from plone.formwidget.recaptcha.interfaces import IReCaptchaSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer
from zope.ramcache import ram

from genweb6.core.controlpanels.header import IHeaderSettings

import logging
import pkg_resources
import transaction


PROFILE_ID = 'profile-genweb6.core:default'

INDEXES = (('open_link_in_new_window', 'BooleanIndex'),
           ('is_important', 'BooleanIndex'),
           ('exclude_from_nav', 'FieldIndex'),
           ('news_image_filename', 'FieldIndex'),
           ('gwuuid', 'UUIDIndex'))


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'genweb6.core:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


# Afegit creació d'indexos programàticament i controladament per:
# http://maurits.vanrees.org/weblog/archive/2009/12/catalog
def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger(__name__)

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = api.portal.get_tool(name='portal_catalog')
    indexes = catalog.indexes()

    indexables = []
    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
    if len(indexables) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('genweb6.core_various.txt') is None:
        return

    # Add additional setup code here
    portal = context.getSite()
    logger = logging.getLogger(__name__)

    # Setup settings Plone
    registry = getUtility(IRegistry)
    registry["plone.navigation_depth"] = 2
    registry["plone.exposeDCMetaTags"] = True

    # Para que guarde la configuracion de los idiomas al reinstalar paquete
    setupTool = SetupMultilingualSite()
    output = setupTool.setupSite(portal)

    # Setup logo + hero
    egglocation = pkg_resources.get_distribution('genweb6.theme').location
    ram.caches.clear()

    header_settings = registry.forInterface(IHeaderSettings)

    if not header_settings.logo:
        logo = open('{}/genweb6/theme/theme/img/logo.png'.format(egglocation), 'rb').read()
        encoded_data = b64encode_file(filename='logo.png', data=logo)
        header_settings.logo = encoded_data

        header_settings.logo_alt = "Universitat Politècnica de Catalunya"
        header_settings.logo_url = "https://www.upc.edu/ca"
        header_settings.logo_external_url = True

    if not header_settings.hero_image:
        hero = open('{}/genweb6/theme/theme/img/capcalera.jpg'.format(egglocation), 'rb').read()
        encoded_data = b64encode_file(filename='capcalera.jpg', data=hero)
        header_settings.hero_image = encoded_data

    recaptcha_settings = registry.forInterface(IReCaptchaSettings)

    if not recaptcha_settings.public_key:
        recaptcha_settings.public_key = '6LcEtjEUAAAAAHVmogdyohPkahy_0MrKsOjKlefn'

    if not recaptcha_settings.private_key:
        recaptcha_settings.private_key = '6LcEtjEUAAAAAFoR3rEORJQTzMdQE0y6prqaC0Ta'

    transaction.commit()

    # transforms = api.portal.get_tool(name='portal_transforms')
    # transform = getattr(transforms, 'safe_html')
    # valid = transform.get_parameter_value('valid_tags')
    # nasty = transform.get_parameter_value('nasty_tags')

    # # GW4 Valid tags
    # gw4_valid = ['script', 'object', 'embed', 'param', 'iframe', 'applet', 'button']
    # for tag in gw4_valid:
    #     # Acceptar a la llista de valides
    #     valid[tag] = 1
    #     # Eliminar de la llista no desitjades
    #     if tag in nasty:
    #         del nasty[tag]

    # stripped = transform.get_parameter_value('stripped_attributes')
    # # GW4 remove some stripped
    # for tag in ['cellspacing', 'cellpadding', 'valign']:
    #     if tag in stripped:
    #         stripped.remove(tag)

    # kwargs = {}
    # kwargs['valid_tags'] = valid
    # kwargs['nasty_tags'] = nasty
    # kwargs['stripped_attributes'] = stripped
    # for k in list(kwargs):
    #     if isinstance(kwargs[k], dict):
    #         v = kwargs[k]
    #         kwargs[k + '_key'] = v.keys()
    #         kwargs[k + '_value'] = [str(s) for s in v.values()]
    #         del kwargs[k]
    # transform.set_parameters(**kwargs)
    # transform._p_changed = True
    # transform.reload()

    # # deshabilitem inline editing
    # site_properties = ISiteSchema(portal)
    # site_properties.enable_inline_editing = False

    # # configurem els estats del calendari
    # pct = api.portal.get_tool(name='portal_calendar')
    # pct.calendar_states = ('published', 'intranet')
    # # Fixem el primer dia de la setamana com dilluns (0)
    # pct.firstweekday = 0


    # # Set mailhost
    # if portal.email_from_address in ('noreply@upc.edu', 'no-reply@upcnet.es'):
    #     mh = api.portal.get_tool(name='MailHost')
    #     mh.smtp_host = 'localhost'
    #     portal.email_from_name = 'Genweb Administrator'
    #     portal.email_from_address = 'no-reply@upcnet.es'

    # # Set default TimeZone (p.a.event)
    # api.portal.set_registry_record('plone.app.event.portal_timezone', 'Europe/Madrid')
    # api.portal.set_registry_record('plone.app.event.first_weekday', 0)

    # transaction.commit()

    add_catalog_indexes(portal, logger)
