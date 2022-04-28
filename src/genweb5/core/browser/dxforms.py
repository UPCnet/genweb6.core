# -*- coding: utf-8 -*-
from plone.dexterity.browser import edit
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.events import AddBegunEvent
from zope.event import notify


class EditForm(edit.DefaultEditForm):
    """ This hacks the default edit form for all dexterities and disables right
        column for all of them.
    """

    def update(self):
        super(EditForm, self).update()

        # Patched for all dexterity types, disable right column
        self.request.set('disable_plone.rightcolumn', True)


def update(self):
    super(DefaultAddForm, self).update()
    # fire the edit begun only if no action was executed
    if len(self.actions.executedActions) == 0:
        notify(AddBegunEvent(self.context))

    # Patched for all dexterity types, disable right column
    self.request.set('disable_plone.rightcolumn', True)
