Changelog
=========

1.83 (unreleased)
-----------------

- Nothing changed yet.


1.82 (2025-11-18)
-----------------

* [FIX] Traduccion Imatge [Iago López]

1.81 (2025-11-14)
-----------------

* [UPD] URLs que pueden hacer login [Iago López]

1.80 (2025-11-14)
-----------------

* [FIX] Add .DS_Store a gitignore [Pilar Marinas]
* [PENTEST] Solucionar vulnerabilidades password reset [Pilar Marinas]
* [PENTEST] Que no puedan subir codigo malicioso en el portrait del usuario solo permitir jpg, png y webp [Pilar Marinas]
* refactor: mover imports de validación junto a changeMemberPortrait [Pilar Marinas]
*  [Pilar Marinas]
* - Imports específicos movidos justo antes de la función [Pilar Marinas]
* - Facilita eliminación futura si se remueve la función [Pilar Marinas]
* - Mantiene convención de patches.py [Pilar Marinas]
* feat: añadir prints informativos a tests de portrait validation [Pilar Marinas]
*  [Pilar Marinas]
* - Prints con emojis (✅/❌/🔒) para mejor visibilidad [Pilar Marinas]
* - Estructura jerárquica descriptiva en cada test [Pilar Marinas]
* - Test resumen (test_zzz_summary) con estadísticas completas [Pilar Marinas]
* - 18 tests totales con seguimiento visual del progreso [Pilar Marinas]
* - Conforme a las convenciones de plone6-testing.mdc [Pilar Marinas]
* test(security): añade tests unitarios e integración para portrait validation [Pilar Marinas]
*  [Pilar Marinas]
* - 14 tests unitarios de validación por magic bytes [Pilar Marinas]
* - 3 tests de integración con el sistema completo [Pilar Marinas]
* - Tests de escenarios de seguridad reales [Pilar Marinas]
* - Verifica rechazo de PHP, shell scripts y otros maliciosos [Pilar Marinas]
* - Verifica aceptación solo de JPG, PNG, WEBP [Pilar Marinas]
*  [Pilar Marinas]
* Todos los tests pasaron: 17/17 ✓ [Pilar Marinas]
* fix(security): validación robusta de portrait upload por contenido real [Pilar Marinas]
*  [Pilar Marinas]
* Implementa validación de seguridad para prevenir subida de archivos maliciosos [Pilar Marinas]
* en el campo portrait del perfil de usuario. [Pilar Marinas]
*  [Pilar Marinas]
* Cambios: [Pilar Marinas]
* - Añade validación por magic bytes en validations.py [Pilar Marinas]
* - Actualiza PortraitUploadAdapter para validar antes de procesar [Pilar Marinas]
* - Mejora manejo de errores en changeMemberPortrait patch [Pilar Marinas]
* - Añade mensajes de error traducidos (ca, es, en) [Pilar Marinas]
* - Implementa whitelist estricta: solo JPG, PNG, WEBP [Pilar Marinas]
*  [Pilar Marinas]
* Seguridad: [Pilar Marinas]
* - Valida contenido real del archivo (magic bytes), no extensión [Pilar Marinas]
* - Rechaza archivos antes de guardarlos [Pilar Marinas]
* - Añade logs de auditoría para intentos maliciosos [Pilar Marinas]
* - Previene upload de PHP, scripts y otros archivos peligrosos [Pilar Marinas]
*  [Pilar Marinas]
* Closes: Vulnerabilidad de upload de shell.php en portrait [Pilar Marinas]
* [UPD] purge_varnish_paths - Comprobar que esta marcado purgingEnabled [Iago López]
* [FIX] Que se vea siempre la descripción del campo en edición aunque lo tengas en readonly [Pilar Marinas]
* [UPD] purge_varnish_paths - obtener request de otra forma si no lo tiene [Iago López]
* [FIX] footer translation [Iago López]

1.80 (unreleased)
-----------------

- Nothing changed yet.


1.79 (2025-10-14)
-----------------

* [FIX] *.po [Iago López]

1.78 (2025-10-14)
-----------------

* [FIX] translations [Clàudia Andreu]
* [UPD] Mejorar visualizacion vista album con filtros [Iago López]

1.77 (2025-09-23)
-----------------

* [UPD] Metadades API variable name [Clàudia Andreu]
* [UPD] Mejorar vista filtered_contents_search_album [Iago López]
* [ADD] helper reinstall_all_genweb_products [Iago López]
* [ADD] helper fix_cas_controlpanel [Iago López]
* [FIX] CAS setup [Iago López]

1.76 (2025-09-15)
-----------------

* [DEL] ipdb [Iago López]

1.75 (2025-09-15)
-----------------

* [UPD] Mover controlpanel de metadades + [ADD] Toucher para cargar datos al controlpanel de metadades [Iago López]
* [UPD] control panel description [Clàudia Andreu]
* Merge branch 'api-test' into develop [Clàudia Andreu]
* [ADD] indicadors to Portal Neteja de Metadades [Clàudia Andreu]

1.74 (2025-09-10)
-----------------

* [FIX] Solve merge [Iago López]
* [UPD] Portal Metadades description [Clàudia Andreu]
* Merge branch 'api-test' of github.com:UPCnet/genweb6.core into api-test [Clàudia Andreu]
* [UPD] Portal Metadades view [Clàudia Andreu]
* [UPD] Add governpre.upc.edu normal login [Iago López]
* Merge branch 'api-test' of github.com:UPCnet/genweb6.core into api-test [Clàudia Andreu]
* [UPD] netejar metadades [Clàudia Andreu]
* [ADD] PyPDF2 package required [Iago López]
* [UPD] metadades xmls [Clàudia Andreu]
* [UPD] metadades control panel [Clàudia Andreu]
* [ADD] first version of Neteja de Metadades [Clàudia Andreu]
* [UPD] Nueva vista: filtered_contents_search_album_view [Iago López]
* [ADD] Nueva vista: filtered_contents_search_album_view [Iago López]

1.73 (2025-07-01)
-----------------

* [FIX] socialtoolsViewlet - eventos recurrentes [«Iago]
* [UPD] No cambiar valores de CAS si ya estan configurados [«Iago]
* [UPD] Modificar portlet banners para que pille solo los portlets de la carpeta banners-ca/es/en [«Iago]
* [FIX] Modificar version artifact para que no de error ci [Pilar Marinas]
* [FIX] Modificar versions paquete para que no de error ci [Pilar Marinas]

1.72 (2025-06-18)
-----------------

* [UPD] Subir timeout de 2 a 5 en los contenidos existentes [«Iago]

1.71 (2025-06-03)
-----------------

* [FIX] plone.app.event.browser.event_listing.pt - Cerrar bien span [«Iago]
* [FIX] Continguts existents - donde llamamos el BeautifulSoup [«Iago]
* [FIX] logger query_index [«Iago]
* [FIX] Arreglar cuando no carga bien el menu de cabecera porque el contenido no tiene bien puesto el idioma [«Iago]
* [UPD] Traducciones contenido existente [«Iago]
* [UPD] Content rules: Manage rules - Añadir webmaster al permiso [«Iago]
* [UPD] reduced timeout and [ADD] user feedback for empty response [Clàudia Andreu]
* [FIX] Sobreescribir query_index para que no de error si no hay record.keys in range max [pilar.marinas]

1.70 (2025-05-20)
-----------------



1.69 (2025-05-20)
-----------------

* [UPD] monkey patches for album views [«Iago]
* [DEL] unused function [Clàudia Andreu]
* [ADD] monkey patches for album views [Clàudia Andreu]

1.68 (2025-05-20)
-----------------

* [UPD] Modificar template correo formularios [Iago López Fernández]
* [UPD] Cambiar como llamamos a las macros [«Iago]
* [FIX] macro calls when it cannot be found on the context [Alberto Durán]
* [ADD] new template for mail body [Clàudia Andreu]
* [FIX] Quitar llamada a js no existente - document_image.min.js [Iago López]
* [FIX] social tools concurrent events bug [Clàudia Andreu]
* [FIX] events leadimage [Clàudia Andreu]
* [FIX] show lead image [Iago López]
* [FIX] show lead image [Clàudia Andreu]
* [UPD] carousel template [Clàudia Andreu]
* [ADD] Patch - Sobreescribir cal_data para que funcione el portlet de calendario con colecciones [Iago López]
* [UPD] Action Documentacion - Cambiar permisos [Iago López]
* [ADD] new button linked to genweb documentation [Clàudia Andreu]

1.67 (2025-04-09)
-----------------

* [UPD] new event collection portlet [Iago López]
* [ADD] new carousel with links [Clàudia Andreu]
* [FIX] new events collection portlet [Clàudia Andreu]
* [UPD] new event collection portlet [Iago López]
* [ADD] new event collection portlet [Clàudia Andreu]
* [FIX] SEO title y description [Iago López]

1.66 (2025-03-26)
-----------------

* [UPD] Cambio literal [Iago López]

1.65 (2025-03-25)
-----------------

* [ADD] links to default view [Clàudia Andreu]
* [ADD] Añadir campos de SEO - titulo y descripcion | Añadirlo behavior SEO a LRF [Iago López]

1.64 (2025-03-10)
-----------------

* [FIX] Solucionar error TOO_MANY_REDIRECTS SSO in portlet [Iago López]
* [FIX] Solucionar error TOO_MANY_REDIRECTS SSO [Iago López]
* [UPD] Cambio de literal Title line [Iago López]
* [FIX] Header viewlet [Iago López]

1.63 (2025-03-07)
-----------------

* [UPD] Añadir icono al nuevo contenido existing content [Iago López]
* [FIX] Solucionar error TOO_MANY_REDIRECTS SSO [Pilar Marinas]
* [UPD] Añadir nuevos directorios en el robots.txt [Iago López]
* [UPD] Cambios controlpanel cabecera [Iago López]
* [UPD] Quitar collective.behavior.seo [Iago López]
* [UPD] Cambios controlpanel cabecera [Iago López]
* [ADD] new tiny format for headers [Clàudia Andreu]
* Merge branch 'develop' of github.com:UPCnet/genweb6.core into develop [Clàudia Andreu]
* [UPD] fields in header-controlpanel [Clàudia Andreu]
* [UPD] Quitar collective.behavior.seo y traer funcionalidad necesaria en el paquete [Iago López]
* [UPD] Quitar twitter del compartir [Iago López]
* [FIX] way of scan paths in linkchecker_intranet [Alberto Durán]
* [FIX] linkchecker intranet view to be more verbose [Alberto Durán]
* Merge branch 'develop' of github.com:UPCnet/genweb6.core into develop [Clàudia Andreu]
* [ADD] New content type- existing content [Clàudia Andreu]

1.62 (2025-02-18)
-----------------

* [FIX] linkchecker_intranet - Quitar salto de linea que provoca error [Iago López Fernández]
* [UPD] linkchecker intranet objects view [Alberto Durán]

1.61 (2025-02-18)
-----------------

* [ADD] linkchecker intranet objects view [Alberto Durán]
* [FIX] monkey patch get_base_path [Clàudia Andreu]
* [ADD] new inline format for tiny [Clàudia Andreu]
* [UPD] removed author from search template [Clàudia Andreu]
* [UPD] monkey patch for get_base_path [Clàudia Andreu]

1.60 (2025-02-10)
-----------------

* [UPD] monkey patch for x-default hreflang [Alberto Durán]
* [UPD] format logger to get more info about instance [Alberto Durán]
* [WIP] x-default hreflang [Clàudia Andreu]

1.59 (2025-02-03)
-----------------

* REMOVE oidc and use cas [ruben.padilla.mateu]

1.58 (2025-02-03)
-----------------

* [FIX] hreflang default [Clàudia Andreu]
* [ADD] override hreflang x-default [Clàudia Andreu]
* [FIX] Portlet new_existing_content - Revisar correctamente si podemos ver el contenido [Iago López]
* [UPD] Controlpanel resources - Mostrar error si los css puestos no son correctos [Iago López]
* [FIX] way of load Document(Page) in existing content - INTERNAL [root]
* [FIX] way of calculate customize_tab [root]
* [UPD] Comparteix - afegir bluesky [Iago López]
* TEST OIDC in replacement of CAS [ruben.padilla.mateu]
* Merge branch 'master' of github.com:UPCnet/genweb6.core [ruben.padilla.mateu]
* TEST OIDC addition in replacement of CAS [ruben.padilla.mateu]
* [FIX] Field image not required [Iago López]

1.57 (2024-12-11)
-----------------

* [UPD] Añadir opciones para el SEO [Iago López]

1.56 (2024-12-10)
-----------------

* [ADD] Behavior imagen para los enlaces [Iago López]
* [ADD] SEO behavior [Iago López]
* [UPD] Portlet banner - Aumentar limite a 10 y personalizar mensaje de error [Iago López]
* [UPD] Añadir nueva vista a las colecciones - event_listing [Iago López]
* [UPD] Literal etiquetas del buscador [Iago López]

1.55 (2024-10-08)
-----------------

* [ADD] toucher fix_icon_field_banners [Iago López]
* [UPD] No abrir login en modal [Iago López]

1.54 (2024-09-26)
-----------------

* [UPD] Cambios en el login [Iago López]

1.53 (2024-09-25)
-----------------

* Merge remote-tracking branch 'origin/feature/build_from_JSON' [Iago López]

1.52 (2024-09-25)
-----------------

* [FIX] Solucionar error que no genera bien el menu de cabecera [Iago López]
* [UPD] Literal [Iago López]
* [UPD] Literal [Iago López]
* [FIX] SSO login en ficheros o imagenes [Iago López]
* [UPD] news_listing - No mostrar expirados [Iago López]
* [FIX] Solucionar error que no genera bien el menu de cabecera [Iago López]

1.51 (2024-07-30)
-----------------

* [ADD] Depedency package xmltodict [Iago López]
* Merge remote-tracking branch 'origin/feature/build_from_JSON' [Iago López]

1.50 (2024-07-30)
-----------------

* Make max_size field as int field [ruben.padilla.mateu]
* Added easyform max size behavior and validator [ruben.padilla.mateu]

1.49 (2024-07-17)
-----------------

* [Deshacer] 1ab94e [Iago López]
* [UPD] Añadir Linkedin en las redes sociales para compartir [Iago López]
* [UPD] TinyMCE quitar autosave [Iago López]
* [UPD] Webmaster tambien puede editar el campo de esconder el login de la cabecera [Iago López]
* [UPDATE] agregar permisos al editor para administrar portlets [Clàudia Andreu]
* Added editors permission to purge cache [ruben.padilla.mateu]

1.48 (2024-06-19)
-----------------

* [UPD] TinyMCE añadir autosave [Iago López]
* Merge branch 'master' of github.com:UPCnet/genweb6.core [ruben.padilla.mateu]
* Added inline style colors for tinymce [ruben.padilla.mateu]
* [ADD] Añadir documento con imagen como vista por defecto de las carpetas [Iago López]
* FIX hero estandar image showing alt message [ruben.padilla.mateu]
* [UPD] Quitar text-truncate-2 de los titulares de los elementos de los portlets [Iago López]
* [ADD] Indexer searchabletext para documentimage [Iago López]
* [UPD] Añadir timeout de 12 horas en el setup [Iago López]

1.47 (2024-05-29)
-----------------

* [ADD] Helper update_session_timeout [Iago López]
* [UPD] Viewlet genweb.newsdate - Que lo vea todo el mundo [Iago López]
* [ADD] Comentario [Iago López]

1.46 (2024-05-15)
-----------------

* [FIX] Portlet navegación, problema con los enlaces [Iago López]
* [UPD] Permitir a Editor ver contenido caducado en el folder_contents [Iago López]
* Merge branch 'master' of github.com:UPCnet/genweb6.core [ruben.padilla.mateu]
* FIX disconnect translations - added modify_translations override [ruben.padilla.mateu]

1.45 (2024-05-07)
-----------------

* [UPD] linters and dependencies for tests [Alberto Durán]
* [FIX] genweb_stats view for sites with huge amount of users [Alberto Durán]
* [UPD] Patches RelationChoice y RelationList permitir buscar contenidos en cualquier idioma [Iago López]
* [ADD] Update last login time in memberdata tool after login [Alberto Durán]
* [UPD] Permitir a Webmaster ver contenido caducado en el folder_contents [Iago López]

1.44 (2024-04-23)
-----------------

* Arreglar colecciones rotas criterios migrador [Pilar Marinas]

1.43 (2024-04-18)
-----------------

* [FIX] Error cuando no hay css personalizado al entrar dentro del tiny [Iago López]

1.42 (2024-04-08)
-----------------

* [ADD] Añadir packet a plone.default_page_types [Iago López]

1.41 (2024-04-02)
-----------------

* [UPD] Traducciones [Iago López]
* [UPD] viewlet socialtools, añadir literal de compartir [Iago López]
* [UPD] Cambios cabecera [Iago López]

1.40 (2024-04-02)
-----------------

* [UPD] Traducciones [Iago López]
* [UPD] Nuevos estilos de cabecera [Iago López]
* [FIX] Portlet fullnews y multiviewcollection [Iago López]
* [UPD] Mostrar contenidos en Esborrany y otros estados si realmente puedes verlos con permisos [Iago López]
* [ADD] Permitir que la vista author funcione sobre un idioma [Iago López]
* [FIX] Actions URL [Iago López]
* [ADD] Añadir configuracion treu_icones_xarxes_socials [Iago López]

1.39 (2024-03-18)
-----------------

* [UPD] Tocador configure_urls_site_cache [Iago López]
* [ADD] Helper disable_easyform_fieldsets_view_mode - Deshabilita les pestañes en mode visualització [Iago López]

1.38 (2024-03-13)
-----------------

* [UPD] Hacer generico el JS del carousel pause [Iago López]
* [ADD] Añadir estilos custom del GW al tiny [Iago López]
* [UPD] robots.txt añadir */plantilles/* [Iago López]
* [FIX] Portlet new_existing_content - No pillaba bien el elemento seleccionado [Iago López]
* [Add] Añadir tocadores exclude_from_nav_images y exclude_from_nav_files [Iago López]
* [ADD] Añadir behaviors plone.locking y plone.translatable [Iago López]
* [FIX] EasyForm - corregir los campos de tipo richtext en el envio del mensaje [Iago López]
* [FIX] login_URL con came_from [Iago López]
* [UPD] Portlets esdeveniments, añadir descripcion [Iago López]
* [ADD] Traducciones varias [Iago López]

1.37 (2024-03-07)
-----------------

* [ADD] Permission WebMaster Manage Keywords [Pilar Marinas]
* [ADD] Products.PloneKeywordManager [Pilar Marinas]

1.36 (2024-03-07)
-----------------

* Moficada tile formulari existent para que solo permita seleccionar formularios [Pilar Marinas]
* [UPD] Hacer que toda la tile de destacat principal sea clicable [Iago López]
* [ADD] Añadir posibilidad de buscar por las etiquetas en la vista de search [Iago López]
* [ADD] Permisos para gestionar el borrado de fieldsets del EasyForm [Iago López]
* [ADD] Traducciones nombres de vista [Iago López]
* [UPD] Mostrar contenidos File y Image en la navegación [Iago López]
* [FIX] Quitar ticket de la url del login del CAS [Iago López]
* [UPD] Añadir selectores permitidos iconos tiny [Iago López]
* [UPD] Añadir mejora a los css compilados [Iago López]
* Que a webmaster le aparezca error si ha borrado el contenido interno en un portlet [Pilar Marinas]
* [UPD] Añadir permisos al Editor sobre el Easyform [Iago López]
* Solucionar bugs portlet new_existing_content solo lo muestra si lo puedes ver [Pilar Marinas]
* [UPD] Cambiar posicion contentleadimage + nuevo diseño [Iago López]
* [UPD] Añadir descripcion campo carousel [Iago López]
* [UPD] Carousel pause [Iago López]
* [ADD] Traducción not_show_image [Iago López]

1.35 (2024-02-21)
-----------------

* Borrado parche No mostrar excluidos de la navegación en colecciones [Pilar Marinas]

1.34 (2024-02-20)
-----------------

* [ADD] helper disable_viewlet [Iago López]
* [ADD] helper enable_viewlet [Iago López]

1.33 (2024-02-20)
-----------------

* [UPD] genweb.get.dxdocument.text.tinymce - Añadir salto de línea al final [Iago López]
* [FIX] genweb.get.dxdocument.text.tinymce - Que no pete si dejan una página vacía [Iago López]
* [UPD] Mejorar gestión plantillas propias del tinymce [Iago López]
* [FIX] migrationfixtemplates add  div class=mceTmpl in templates [Pilar Marinas]

1.32 (2024-02-19)
-----------------

* [FIX] configure_urls_site_cache [Iago López]
* configure_urls_site_cache [Pilar Marinas]
* configure_urls_site_cache [Pilar Marinas]
* [UPD] Eliminar opciones de vistas en contenido LRF [Iago López]
* [UPD] Carousel 4 imagenes añadir enlace en las imagenes [Iago López]
* Remove tile twitter [Pilar Marinas]
* [UPD] Add valid tags and attributes [Iago López]

1.31 (2024-02-13)
-----------------

* [FIX] Document.xml add mosaic properties [Iago López]
* [FIX] ADD marmoset para no eliminar imagenes data:... [Iago López]
* [FIX] No se podia subir imagenes al perfil [Iago López]
* [UPD] Añadir restriccion de carpetas shared en el robots.txt [Iago López]
* Traducciones [Iago López]

1.30 (2024-02-07)
-----------------

* [FIX] purge_all de todos los dominis visibles externamente [Pilar Marinas]

1.29 (2024-02-05)
-----------------

* [ADD] Enlaces en nueva pestaña en portlet de navegación [Iago López]

1.28 (2024-02-02)
-----------------

* [FIX] Link: Generar correctamente el enlace [Iago López]

1.27 (2024-01-31)
-----------------

* [FIX] Solucionar error que no genera bien el menu de cabecera [Iago López]
* [FIX] Open link in new window [Alberto Durán]
* [UPD] Añadir permisos al WebMaster par las acciones del EasyForm [Iago López]
* [UPD] Añadir permisos al WebMaster par las acciones del EasyForm [Iago López]
* [ADD] Patches RelationChoice y RelationList permitir buscar contenidos en cualquier idioma [Iago López]
* [UPD] Modificar visualización del portlet de agenda [Iago López]
* [ADD] Traducciones vista tabular [Iago López]
* [FIX] Tradiccoón portlet multi vista [Iago López]

1.26 (2024-01-15)
-----------------

* [FIX] Error viewlet socialtools not filename [Iago López]

1.25 (2024-01-12)
-----------------

* Traducciones workflows [Iago López]
* Add IDexteritySchema a nuestros contenidos para que si hay imagen haga del plone.app.caching.purge.py el purge class ScalesPurgePaths [Pilar Marinas]
* [FIX] Solve URL in domain UPC [Iago López]
* [UPD] registry purge false [Iago López]
* [DEL] ipdb [Iago López]

1.24 (2024-01-09)
-----------------

* Añadir nuevos estilos al tinymce [Iago López]
* [FIX] Bug permission sharing [Pilar Marinas]

1.23 (2023-12-15)
-----------------

* Modificar traducció purge [Pilar Marinas]

1.22 (2023-12-14)
-----------------

* [UPD] Recaptcha setup [Iago López]
* Traduccions purge [Pilar Marinas]
* Button purge varnish [Pilar Marinas]
* [ADD] No mostrar elementos excluidos de la navegación en colecciones [Iago López]
* [ADD] No mostrar elementos excluidos de la navegación en carpetas [Iago López]
* [FIX] setuphandlers.py, no cambiar logo si ya esta puesto [Iago López]
* [ADD] marmoset fix events_listing view [Iago López]
* [UPD] Traducciones [Iago López]
* [UPD] Traducciones [Iago López]

1.21 (2023-12-05)
-----------------

* [UPD] Evitar que peten los contenidos existentes mal configurados [Iago López]
* [UPD] Helper change_modify_view_template_permission_news_events parte de los eventos [Iago López]

1.20 (2023-12-04)
-----------------

* Comentar ram.cache porque la hace por zcX y el resto tiene datos incorrectos y añadir purge_all varnish [Pilar Marinas]

1.19 (2023-12-01)
-----------------

* Purge [Pilar Marinas]

1.18 (2023-11-30)
-----------------

* purge cache varnish si esta configurado [Pilar Marinas]
* [DEL] gw-css [Iago López]
* [UPD] View news_listing [Iago López]
* Purge varnish resources controlpanel [Pilar Marinas]
* [UPD] Cambiar vista coleccion eventos por event_listing [Iago López]
* Purge varnish header controlpanel [Pilar Marinas]
* Purge varnish paths [Pilar Marinas]
* [UPD] Cambiar vista coleccion eventos por event_listing [Iago López]
* [UPD] Invertir orden colecciones aggregator [Iago López]
* [UPD] No permitir que los usuarios editen la vista de las noticias y eventos [Iago López]
* [FIX] Evitar error menu cabecera cuando tenemos un enlace interno apuntando a un objeto no publico [Iago López]
* Purge varnish [Pilar Marinas]
* Purge varnish header controlpanel [Pilar Marinas]
* Purge varnish [Pilar Marinas]
* Purge varnish [Pilar Marinas]
* Purge varnish [Pilar Marinas]
* Purge varnish controlpanel header [Pilar Marinas]

1.17 (2023-11-24)
-----------------

* [FIX] Mover bloque de analitycs en el head, plone lo tiene abajo dentro del body [Iago López]

1.16 (2023-11-23)
-----------------

* [ADD] Helper setup_defaultpage_aggregator [Iago López]
* [FIX] setup-view eliminacion carpeta recursos de plone [Iago López]
* [FIX] setup robots.txt [Iago López]
* [DEL] commit eee7924 [Iago López]
* [FIX] Permission controlpanel resources a webmaster [Iago López]

1.15 (2023-11-23)
-----------------

* [ADD] setup robots.txt [Iago López]
* [DEL] commit eee7924 [Iago López]

1.14 (2023-11-23)
-----------------

* [UPD] Traduccion event_listing [Iago López]
* [FIX] Template event_listing [Iago López]
* [UPD] Condición news_events_listing [Iago López]
* [UPD] Cambiar template event_listing [Iago López]
* [UPD] Revisión de las cache [Iago López]
* [FIX] Viewlet important - Los mensajes se mostraban con la condición al reves [Iago López]
* [FIX] Portlets fullnews cambiar orden [Iago López]
* Posición viewlet genweb.important [Iago López]

1.13 (2023-11-20)
-----------------

* Parches para solucionar problemas de formularios antiguos sin algun dato [Pilar Marinas]

1.12 (2023-11-13)
-----------------

* [ADD] Hide creators field in /++api++/ [Alberto Durán]
* Viewlet important [Iago López]

1.11 (2023-10-30)
-----------------

* RSS visible [Pilar Marinas]

1.10 (2023-10-27)
-----------------

* Activar viewlet plone.analytics [Pilar Marinas]

1.9 (2023-10-26)
----------------

* Añadir traducciones estándar [Ruben Padilla Mateu]
* Permiso webmaster [Iago López]
* [UPD] Quitar <p> sobrante en los contenidos de ejemplo del setup-view [Iago López]

1.8 (2023-10-19)
----------------

* [FIX] subhome [Iago López]

1.7 (2023-10-19)
----------------

* [FIX] Ver descripcion portlets fullnews y multiviewcollection [Iago López]
* Quitar imagenes por defecto [Iago López]

1.6 (2023-10-19)
----------------

* Desactivar menu del footer por defecto [Iago López]
* Remove old imports from gw4 and become fix_record helper view more userfriendly [Alberto Durán]
* [FIX] Que no pete si no se informa bien un enlace del pie [Iago López]
* Fix homepage [Iago López]
* Traducción [Iago López]

1.5 (2023-10-10)
----------------

* Permisos webmaster portlets [Iago López]
* Fix multiviewcollection [Iago López]
* Permisos workflows Webmaster [Iago López]
* Permisos Webmaster [Iago López]
* Modificar enlace setup [Iago López]
* En movil siempre se ve el menú de enlaces [Iago López]
* Fix traducción [Iago López]
* No mostrar link login por defecto [Iago López]
* Enable sitemap.xml.gz [Iago López]

1.4 (2023-09-21)
----------------

* setuphandlers [Iago López]
* Tile 4 destacats esdeveniments [Iago López]

1.3 (2023-09-20)
----------------

* [UPD] setuphandlers [Iago López]
* Dar soporte scss en los estilos personalizados [Iago López]

1.2 (2023-09-14)
----------------

* Añadir full como tamaño de imagen [Iago López]

1.1 (2023-09-14)
----------------

* Twitter X [Iago López]
* Si tenemos una url con resolveuid la cambiamos por la url del objeto [Iago López]
* Cambiar logo twitter a X [Iago López]

1.0 (2023-09-07)
----------------

* Twitter X [Iago López]
* Si tenemos una url con resolveuid la cambiamos por la url del objeto [Iago López]
* Cambiar logo twitter a X [Iago López]

1.0 (2023-09-07)
----------------

- Initial release.
  [pilar.marinas@upcnet.es]
