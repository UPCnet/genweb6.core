cacheprofile = """
<registry>
    <record name="plone.app.caching.interfaces.IPloneCacheSettings.cacheStopRequestVariables" interface="plone.app.caching.interfaces.IPloneCacheSettings" field="cacheStopRequestVariables">
    <field type="plone.registry.field.Tuple">
      <default>
        <element>statusmessages</element>
        <element>SearchableText</element>
      </default>
      <description>Variables in the request that prevent caching if present</description>
      <title>Request variables that prevent caching</title>
      <value_type type="plone.registry.field.ASCIILine">
        <title>Request variables</title>
      </value_type>
    </field>
    <value>
      <element>statusmessages</element>
      <element>SearchableText</element>
    </value>
  </record>
  <record name="plone.app.caching.interfaces.IPloneCacheSettings.contentTypeRulesetMapping" interface="plone.app.caching.interfaces.IPloneCacheSettings" field="contentTypeRulesetMapping">
    <field type="plone.registry.field.Dict">
      <description>Maps content type names to ruleset names</description>
      <key_type type="plone.registry.field.ASCIILine">
        <title>Content type name</title>
      </key_type>
      <title>Content type/ruleset mapping</title>
      <value_type type="plone.registry.field.DottedName">
        <title>Ruleset name</title>
      </value_type>
    </field>
    <value/>
  </record>
  <record name="plone.app.caching.interfaces.IPloneCacheSettings.enableCompression" interface="plone.app.caching.interfaces.IPloneCacheSettings" field="enableCompression">
    <field type="plone.registry.field.Bool">
      <default>False</default>
      <description>Determine whether GZip compression should be enabled for standard responses</description>
      <title>Enable GZip compression</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.interfaces.IPloneCacheSettings.purgedContentTypes" interface="plone.app.caching.interfaces.IPloneCacheSettings" field="purgedContentTypes">
    <field type="plone.registry.field.Tuple">
      <default>
        <element>File</element>
        <element>Image</element>
        <element>News Item</element>
      </default>
      <description>List content types which should be purged when modified</description>
      <title>Content types to purge</title>
      <value_type type="plone.registry.field.ASCIILine">
        <title>Content type name</title>
      </value_type>
    </field>
    <value>
      <element>Banner</element>
      <element>BannerContainer</element>
      <element>Collection</element>
      <element>genweb.upc.documentimage</element>
      <element>EasyForm</element>
      <element>Event</element>
      <element>File</element>
      <element>Image</element>
      <element>Link</element>
      <element>Logos_Container</element>
      <element>Logos_Footer</element>
      <element>News Item</element>
      <element>Document</element>
      <element>Plone Site</element>
      <element>genweb.upc.subhome</element>
      <element>packet</element>
    </value>
  </record>
  <record name="plone.app.caching.interfaces.IPloneCacheSettings.templateRulesetMapping" interface="plone.app.caching.interfaces.IPloneCacheSettings" field="templateRulesetMapping">
    <field type="plone.registry.field.Dict">
      <description>Maps skin layer page template names to ruleset names</description>
      <key_type type="plone.registry.field.ASCIILine">
        <title>Page template name</title>
      </key_type>
      <title>Page template/ruleset mapping</title>
      <value_type type="plone.registry.field.DottedName">
        <title>Ruleset name</title>
      </value_type>
    </field>
    <value>
      <element key="RSS">plone.content.feed</element>
      <element key="accessibility-info">plone.content.itemView</element>
      <element key="atom.xml">plone.content.feed</element>
      <element key="file_view">plone.content.itemView</element>
      <element key="image_view">plone.content.itemView</element>
      <element key="image_view_fullscreen">plone.content.itemView</element>
      <element key="itunes.xml">plone.content.feed</element>
      <element key="rss.xml">plone.content.feed</element>
      <element key="search_rss">plone.content.feed</element>
      <element key="sitemap">plone.content.itemView</element>
    </value>
  </record>
  <record name="plone.app.caching.moderateCaching.anonOnly">
    <field type="plone.registry.field.Bool">
      <description>Ensure logging users always get a fresh page. Note that if you are caching pages in a proxy cache, you'll still need to use a Vary response header to keep anonymous and authenticated content separate.</description>
      <required>False</required>
      <title>Only cache for anonymous users</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.etags">
    <field type="plone.registry.field.Tuple">
      <description>A list of ETag component names to include</description>
      <required>False</required>
      <title>ETags</title>
      <value_type type="plone.registry.field.ASCIILine"/>
    </field>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.moderateCaching.lastModified">
    <field type="plone.registry.field.Bool">
      <description>Turn on Last-Modified headers</description>
      <required>False</required>
      <title>Last-modified validation</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.anonOnly">
    <field ref="plone.app.caching.moderateCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.etags">
    <field ref="plone.app.caching.moderateCaching.etags"/>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.lastModified">
    <field ref="plone.app.caching.moderateCaching.lastModified"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.ramCache">
    <field ref="plone.app.caching.moderateCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.smaxage">
    <field ref="plone.app.caching.moderateCaching.smaxage"/>
    <value>86400</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.file.vary">
    <field ref="plone.app.caching.moderateCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.anonOnly">
    <field ref="plone.app.caching.moderateCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.etags">
    <field ref="plone.app.caching.moderateCaching.etags"/>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.lastModified">
    <field ref="plone.app.caching.moderateCaching.lastModified"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.ramCache">
    <field ref="plone.app.caching.moderateCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.smaxage">
    <field ref="plone.app.caching.moderateCaching.smaxage"/>
    <value>86400</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.folderView.vary">
    <field ref="plone.app.caching.moderateCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.anonOnly">
    <field ref="plone.app.caching.moderateCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.etags">
    <field ref="plone.app.caching.moderateCaching.etags"/>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.lastModified">
    <field ref="plone.app.caching.moderateCaching.lastModified"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.ramCache">
    <field ref="plone.app.caching.moderateCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.smaxage">
    <field ref="plone.app.caching.moderateCaching.smaxage"/>
    <value>86400</value>
  </record>
  <record name="plone.app.caching.moderateCaching.plone.content.itemView.vary">
    <field ref="plone.app.caching.moderateCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.moderateCaching.ramCache">
    <field type="plone.registry.field.Bool">
      <description>Turn on caching in Zope memory</description>
      <required>False</required>
      <title>RAM cache</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.moderateCaching.smaxage">
    <field type="plone.registry.field.Int">
      <description>Time (in seconds) to cache the response in the caching proxy</description>
      <required>False</required>
      <title>Shared maximum age</title>
    </field>
    <value>86400</value>
  </record>
  <record name="plone.app.caching.moderateCaching.vary">
    <field type="plone.registry.field.ASCIILine">
      <description>Name(s) of HTTP headers that must match for the caching proxy to return a cached response</description>
      <required>False</required>
      <title>Vary</title>
    </field>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.strongCaching.anonOnly">
    <field type="plone.registry.field.Bool">
      <description>Ensure logging users always get a fresh page. Note that if you are caching pages in a proxy cache, you'll still need to use a Vary response header to keep anonymous and authenticated content separate.</description>
      <required>False</required>
      <title>Only cache for anonymous users</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.strongCaching.etags">
    <field type="plone.registry.field.Tuple">
      <description>A list of ETag component names to include</description>
      <required>False</required>
      <title>ETags</title>
      <value_type type="plone.registry.field.ASCIILine"/>
    </field>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.lastModified">
    <field type="plone.registry.field.Bool">
      <description>Turn on Last-Modified headers</description>
      <required>False</required>
      <title>Last-modified validation</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.maxage">
    <field type="plone.registry.field.Int">
      <description>Time (in seconds) to cache the response in the browser or caching proxy</description>
      <required>False</required>
      <title>Maximum age</title>
    </field>
    <value>2419200</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.anonOnly">
    <field ref="plone.app.caching.strongCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.etags">
    <field ref="plone.app.caching.strongCaching.etags"/>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.lastModified">
    <field ref="plone.app.caching.strongCaching.lastModified"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.maxage">
    <field ref="plone.app.caching.strongCaching.maxage"/>
    <value>2419200</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.ramCache">
    <field ref="plone.app.caching.strongCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.smaxage">
    <field ref="plone.app.caching.strongCaching.smaxage"/>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.plone.resource.vary">
    <field ref="plone.app.caching.strongCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.anonOnly">
    <field ref="plone.app.caching.strongCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.etags">
    <field ref="plone.app.caching.strongCaching.etags"/>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.lastModified">
    <field ref="plone.app.caching.strongCaching.lastModified"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.maxage">
    <field ref="plone.app.caching.strongCaching.maxage"/>
    <value>2419200</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.ramCache">
    <field ref="plone.app.caching.strongCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.smaxage">
    <field ref="plone.app.caching.strongCaching.smaxage"/>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.plone.stableResource.vary">
    <field ref="plone.app.caching.strongCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.strongCaching.ramCache">
    <field type="plone.registry.field.Bool">
      <description>Turn on caching in Zope memory</description>
      <required>False</required>
      <title>RAM cache</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.strongCaching.smaxage">
    <field type="plone.registry.field.Int">
      <description>Time (in seconds) to cache the response in the caching proxy. Leave blank to use value from "Maximum age" field.</description>
      <required>False</required>
      <title>Shared maximum age</title>
    </field>
    <value/>
  </record>
  <record name="plone.app.caching.strongCaching.vary">
    <field type="plone.registry.field.ASCIILine">
      <description>Name(s) of HTTP headers that must match for the caching proxy to return a cached response</description>
      <required>False</required>
      <title>Vary</title>
    </field>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.terseCaching.anonOnly">
    <field type="plone.registry.field.Bool">
      <description>Ensure logging users always get a fresh page. Note that if you are caching pages in a proxy cache, you'll still need to use a Vary response header to keep anonymous and authenticated content separate.</description>
      <required>False</required>
      <title>Only cache for anonymous users</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.terseCaching.etags">
    <field type="plone.registry.field.Tuple">
      <description>A list of ETag component names to include</description>
      <required>False</required>
      <title>ETags</title>
      <value_type type="plone.registry.field.ASCIILine"/>
    </field>
    <value/>
  </record>
  <record name="plone.app.caching.terseCaching.lastModified">
    <field type="plone.registry.field.Bool">
      <description>Turn on Last-Modified headers</description>
      <required>False</required>
      <title>Last-modified validation</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.terseCaching.maxage">
    <field type="plone.registry.field.Int">
      <description>Time (in seconds) to cache the response in the browser</description>
      <required>False</required>
      <title>Maximum age</title>
    </field>
    <value>10</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.anonOnly">
    <field ref="plone.app.caching.terseCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.etags">
    <field ref="plone.app.caching.terseCaching.etags"/>
    <value/>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.lastModified">
    <field ref="plone.app.caching.terseCaching.lastModified"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.maxage">
    <field ref="plone.app.caching.terseCaching.maxage"/>
    <value>10</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.ramCache">
    <field ref="plone.app.caching.terseCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.smaxage">
    <field ref="plone.app.caching.terseCaching.smaxage"/>
    <value>60</value>
  </record>
  <record name="plone.app.caching.terseCaching.plone.content.dynamic.vary">
    <field ref="plone.app.caching.terseCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.terseCaching.ramCache">
    <field type="plone.registry.field.Bool">
      <description>Turn on caching in Zope memory</description>
      <required>False</required>
      <title>RAM cache</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.terseCaching.smaxage">
    <field type="plone.registry.field.Int">
      <description>Time (in seconds) to cache the response in the caching proxy</description>
      <required>False</required>
      <title>Shared maximum age</title>
    </field>
    <value>60</value>
  </record>
  <record name="plone.app.caching.terseCaching.vary">
    <field type="plone.registry.field.ASCIILine">
      <description>Name(s) of HTTP headers that must match for the caching proxy to return a cached response</description>
      <required>False</required>
      <title>Vary</title>
    </field>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.weakCaching.anonOnly">
    <field type="plone.registry.field.Bool">
      <description>Ensure logging users always get a fresh page. Note that if you are caching pages in a proxy cache, you'll still need to use a Vary response header to keep anonymous and authenticated content separate.</description>
      <required>False</required>
      <title>Only cache for anonymous users</title>
    </field>
    <value>True</value>
  </record>
  <record name="plone.app.caching.weakCaching.etags">
    <field type="plone.registry.field.Tuple">
      <description>A list of ETag component names to include</description>
      <required>False</required>
      <title>ETags</title>
      <value_type type="plone.registry.field.ASCIILine"/>
    </field>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.weakCaching.lastModified">
    <field type="plone.registry.field.Bool">
      <description>Turn on Last-Modified headers</description>
      <required>False</required>
      <title>Last-modified validation</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.weakCaching.plone.content.folderView.anonOnly">
    <field ref="plone.app.caching.weakCaching.anonOnly"/>
    <value>True</value>
  </record>
  <record name="plone.app.caching.weakCaching.plone.content.folderView.etags">
    <field ref="plone.app.caching.weakCaching.etags"/>
    <value>
      <element>userid</element>
      <element>userLanguage</element>
      <element>locked</element>
      <element>resourceRegistries</element>
      <element>catalogCounter</element>
    </value>
  </record>
  <record name="plone.app.caching.weakCaching.plone.content.folderView.lastModified">
    <field ref="plone.app.caching.weakCaching.lastModified"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.weakCaching.plone.content.folderView.ramCache">
    <field ref="plone.app.caching.weakCaching.ramCache"/>
    <value>False</value>
  </record>
  <record name="plone.app.caching.weakCaching.plone.content.folderView.vary">
    <field ref="plone.app.caching.weakCaching.vary"/>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.app.caching.weakCaching.ramCache">
    <field type="plone.registry.field.Bool">
      <description>Turn on caching in Zope memory</description>
      <required>False</required>
      <title>RAM cache</title>
    </field>
    <value>False</value>
  </record>
  <record name="plone.app.caching.weakCaching.vary">
    <field type="plone.registry.field.ASCIILine">
      <description>Name(s) of HTTP headers that must match for the caching proxy to return a cached response</description>
      <required>False</required>
      <title>Vary</title>
    </field>
    <value>Accept-Encoding, User-Agent, X-Anonymous</value>
  </record>
  <record name="plone.caching.interfaces.ICacheSettings.operationMapping" interface="plone.caching.interfaces.ICacheSettings" field="operationMapping">
    <field type="plone.registry.field.Dict">
      <description>Maps rule set names to operation names</description>
      <key_type type="plone.registry.field.DottedName">
        <title>Rule set name</title>
      </key_type>
      <title>Rule set/operation mapping</title>
      <value_type type="plone.registry.field.DottedName">
        <title>Caching operation name</title>
      </value_type>
    </field>
    <value>
      <element key="plone.content.dynamic">plone.app.caching.terseCaching</element>
      <element key="plone.content.feed">plone.app.caching.noCaching</element>
      <element key="plone.content.file">plone.app.caching.moderateCaching</element>
      <element key="plone.content.folderView">plone.app.caching.moderateCaching</element>
      <element key="plone.content.itemView">plone.app.caching.moderateCaching</element>
      <element key="plone.resource">plone.app.caching.strongCaching</element>
      <element key="plone.stableResource">plone.app.caching.strongCaching</element>
    </value>
  </record>
  <record name="plone.caching.operations.chain.operations">
    <field type="plone.registry.field.List">
      <description>A list of operations to call, in order</description>
      <title>Operations</title>
      <value_type type="plone.registry.field.DottedName"/>
    </field>
    <value/>
  </record>
</registry>
"""
