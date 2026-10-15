from genweb6.core.interfaces import IGenweb6CoreLayer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.site import SerializeSiteRootToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter


@adapter(IPloneSiteRoot, IGenweb6CoreLayer)
class CustomSerializeSiteRootToJson(SerializeSiteRootToJson):

    def __call__(self, *args, **kwargs):
        # plone.restapi >= 9 llama con include_items / include_expansion:
        # se reenvian todos los argumentos al serializador original
        result = super(CustomSerializeSiteRootToJson, self).__call__(*args, **kwargs)
        # Eliminar el atributo "creators" de SiteRoot serializado
        result.pop('creators', None)

        return result


@adapter(IDexterityContainer, IGenweb6CoreLayer)
class CustomSerializeFolderToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(CustomSerializeFolderToJson, self).__call__(*args, **kwargs)
        # Eliminar el atributo "creators" de las folders serializadas
        result.pop('creators', None)

        return result


@adapter(IDexterityContent, IGenweb6CoreLayer)
class CustomSerializeToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(CustomSerializeToJson, self).__call__(*args, **kwargs)
        # Eliminar el atributo "creators" de las document, news,
        # events, links, etc. serializadas
        result.pop('creators', None)

        return result
