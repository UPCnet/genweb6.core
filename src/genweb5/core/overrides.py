# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.app.contentmenu.menu import DisplaySubMenuItem
from plone.app.contentmenu.menu import FactoriesSubMenuItem
from plone.app.dexterity.behaviors.constrains import ConstrainTypesBehavior

from genweb5.core import GenwebMessageFactory as _


# constants for enableConstrain. Copied from AT
ACQUIRE = -1  # acquire locallyAllowedTypes from parent (default)
DISABLED = 0  # use default behavior of PortalFolder which uses the FTI info
ENABLED = 1  # allow types from locallyAllowedTypes only


class gwDisplaySubMenuItem(DisplaySubMenuItem):

    title = _(u'label_choose_template', default=u'Display')


class gwFactoriesSubMenuItem(FactoriesSubMenuItem):

    title = _(u'label_add_new_item', default=u'Add new\u2026')


class gwConstrainTypesBehavior(ConstrainTypesBehavior):

    def _filterByDefaults(self, types, context=None):
        """
        Filter the given types by the items which would also be allowed by
        default. Important, else users could circumvent security restritions
        """
        if context is None:
            context = self.context
        defaults = [
            fti.getId() for fti in self.getDefaultAddableTypes(context)
        ]
        return [x for x in types if x in defaults]

    def allowedContentTypes(self, context=None):
        """
        If constraints are enabled, return the locally allowed types.
        If the setting is ACQUIRE, acquire the locally allowed types according
        to the ACQUIRE rules, described in the interface.
        If constraints are disabled, use the default addable types

        This method returns the FTI, NOT the FTI id, like most other methods.
        """
        if context is None:
            context = self.context
        mode = self.getConstrainTypesMode()
        default_addable = self.getDefaultAddableTypes(context)

        if mode == DISABLED:
            return default_addable
        elif mode == ENABLED:
            if hasattr(self.context, 'locally_allowed_types'):
                return [t for t in default_addable if t.getId() in
                        self.context.locally_allowed_types]
            else:
                return default_addable
        elif mode == ACQUIRE:
            parent = self.context.__parent__
            parent_constrain_adapter = ISelectableConstrainTypes(parent, None)
            if not parent_constrain_adapter:
                return default_addable
            return_tids = self._filterByDefaults(
                parent_constrain_adapter.getLocallyAllowedTypes(
                    context), context)
            return [t for t in default_addable if t.getId() in return_tids]
        else:
            raise Exception(
                "Wrong constraint setting. %i is an invalid value",
                mode)

    def getImmediatelyAddableTypes(self, context=None):
        """
        If constraints are enabled, return the locally immediately
        addable tpes.
        If the setting is ACQUIRE, acquire the immediately addable types from
        the parent, according to the rules described in the interface.
        If constraints are disabled, use the default addable types
        """
        if context is None:
            context = self.context
        mode = self.getConstrainTypesMode()
        default_addable = [t.getId()
                           for t in self.getDefaultAddableTypes(context)]

        if mode == DISABLED:
            return default_addable
        elif mode == ENABLED:
            if hasattr(self.context, 'immediately_addable_types'):
                return self._filterByDefaults(
                    self.context.immediately_addable_types, context)
        elif mode == ACQUIRE:
            parent = self.context.__parent__
            parent_constrain_adapter = ISelectableConstrainTypes(parent, None)
            if not parent_constrain_adapter:
                return default_addable
            return self._filterByDefaults(
                parent_constrain_adapter.getImmediatelyAddableTypes(context), context)
        else:
            raise Exception(
                "Wrong constraint setting. %i is an invalid value",
                mode)
