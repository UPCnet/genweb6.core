from genweb6.core.interfaces import IGenweb6CoreLayer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.site import SerializeSiteRootToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter


@adapter(IPloneSiteRoot, IGenweb6CoreLayer)
class CustomSerializeSiteRootToJson(SerializeSiteRootToJson):

    def __call__(self, version=None):
        result = super(CustomSerializeSiteRootToJson, self).__call__()
        # Eliminar el atributo "creators" de SiteRoot serializado
        result.pop('creators', None)

        return result


@adapter(IDexterityContainer, IGenweb6CoreLayer)
class CustomSerializeFolderToJson(SerializeToJson):

    def __call__(self, version=None, include_items=True):
        result = super(CustomSerializeFolderToJson, self).__call__()
        # Eliminar el atributo "creators" de las folders serializadas
        result.pop('creators', None)

        return result


@adapter(IDexterityContent, IGenweb6CoreLayer)
class CustomSerializeToJson(SerializeToJson):

    def __call__(self, version=None, include_items=True):
        result = super(CustomSerializeToJson, self).__call__()
        # Eliminar el atributo "creators" de las document, news,
        # events, links, etc. serializadas
        result.pop('creators', None)

        return result
