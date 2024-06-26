# -*- coding: utf-8 -*-
from plone.base.utils import get_installer

import logging

logger = logging.getLogger(__name__)


def upgrade_by_reinstall(context):
    qi = get_installer(context)
    qi.uninstall_product("genweb6.core")
    qi.install_product("genweb6.core")
    qi.uninstall_product("plone.app.mosaic")
    qi.install_product("plone.app.mosaic")
