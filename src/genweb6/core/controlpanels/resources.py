# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.widget import NamedFileFieldWidget
from plone.memoize import ram
from plone.namedfile.file import NamedFile
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from time import time
from z3c.form import button
from z3c.form.browser.text import TextWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import implementer_only
from zope.ramcache import ram as ramcache
from zope.schema.interfaces import IField

from genweb6.core import _
from genweb6.core import utils


class IResourcesControlpanelJSWidget(ITextWidget):
    pass


@implementer_only(IResourcesControlpanelJSWidget)
class ResourcesControlpanelJSWidget(TextWidget):

    klass = u'resources_controlpanel-js-widget'

    def update(self):
        super(TextWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def ResourcesControlpanelJSFieldWidget(field, request):
    return FieldWidget(field, ResourcesControlpanelJSWidget(request))


class IResourcesSettings(model.Schema):

    upload_files = schema.Bool(
        title=_(u'Selecciona per pujar els recursos des de fitxers i no utilitzar els camps de text pla'),
        required=False,
        default=False
    )

    text_css = schema.Text(
        title=_(u"Recurs CSS"),
        description=_(u"<a href='https://codebeautify.org/cssvalidate' target='_blank'>Validar</a>"),
        required=False,
    )

    text_js = schema.Text(
        title=_(u"Recurs JS"),
        description=_(u"<a href='https://codebeautify.org/jsvalidate' target='_blank'>Validar</a>"),
        required=False,
    )

    directives.widget('file_css', NamedFileFieldWidget)
    file_css = schema.Bytes(
        title=_(u"Recurs CSS"),
        required=False,
    )

    directives.widget('file_js', NamedFileFieldWidget)
    file_js = schema.Bytes(
        title=_(u"Recurs JS"),
        required=False,
    )

    directives.widget('js', ResourcesControlpanelJSFieldWidget)
    js = schema.Text(title=_(u""), required=False)


class ResourcesSettingsForm(controlpanel.RegistryEditForm):

    schema = IResourcesSettings
    label = _(u'Resources Settings')

    def updateFields(self):
        super(ResourcesSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(ResourcesSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        ramcache.caches.clear()
        self.applyChanges(data)

        paths = []
        paths.append('/@@gw-js')
        paths.append('/_purge_all')

        utils.purge_varnish_paths(self, paths)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class ResourcesSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ResourcesSettingsForm


class GWJS(BrowserView):

    def __call__(self):
        return self.generate()

    @ram.cache(lambda *args: time() // (24 * 60 * 60))
    def generate(self):
        registry = queryUtility(IRegistry)
        resources_config = registry.forInterface(IResourcesSettings)

        if getattr(resources_config, 'file_js', False):
            filename, data = b64decode_file(resources_config.file_js)
            data = NamedFile(data=data, filename=filename)
            return data._data._data
        return None
