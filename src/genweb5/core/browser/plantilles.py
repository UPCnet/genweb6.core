# -*- coding: utf-8 -*-


def get_plantilles():
    """
    Declaració de les pàgines que es faràn servir com plantilles
    """
    plantilles = []
    titol = u"Llistat índex"
    resum = u"Índex de continguts."
    cos = u"""<h2>Sed ultricies cursus lectus</h2>
<ul class="list list-index">
<li><a href="#">Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros.</a></li>
<li><a href="#">Mauris vestibulum, felis et egestas ullamcorper, purus nibh vehicula sem, eu egestas ante nisl non justo.</a></li>
<li><a href="#">Fusce tincidunt, lorem nec dapibus consectetuer, leo orci mollis ipsum, eget suscipit eros purus in ante.</a></li>
<li><a href="#">At ipsum vitae est lacinia tincidunt. Maecenas elit orci, gravida ut, molestie non, venenatis vel, lorem.</a></li>
</ul><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Llistat enllaços"
    resum = u"Per afegir un llistat d'enllaços relacionats."
    cos = u"""<h2>Enllaços relacionats</h2>
<ul class="list list-links">
<li><a href="#">JDuis tellus</a></li>
<li><a href="#">Maecenas elit orci</a></li>
<li><a href="#">At ipsum vitae est lacinia tincidunt</a></li>
</ul><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Llistat destacat"
    resum = u"Per afegir un llistat d'enllaços destacats."
    cos = u"""  <h2>Llistat destacat</h2>
<ul class="list list-highlighted">
<li><a href="#">JDuis tellus</a></li>
<li><a href="#">Maecenas elit orci</a></li>
<li><a href="#">At ipsum vitae est lacinia tincidunt</a></li>
</ul><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Text amb tots els titulars"
    resum = u"Com utilitzar la jerarquia de títols. És important respectar aquesta jerarquia si volem ser accessibles i millorar el nostre posicionament a Internet."
    cos = u"""<h2>In aliquam rhoncus sem</h2>
<p>Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p>
<h3>In aliquam rhoncus sem</h3>
<p>Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p>
<h4>In aliquam rhoncus sem</h4>
<p>Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p>
<h5>In aliquam rhoncus sem</h5>
<p>Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p>
<h6>In hac habitasse platea dictumst</h6>
<p>Nulla non orci. In egestas porttitor quam. Duis nec diam eget nibh mattis tempus. Curabitur accumsan pede id odio. Nunc vitae libero. Aenean condimentum diam et turpis. Vestibulum non risus. Ut consectetuer gravida elit. Aenean est nunc, varius sed, aliquam eu, feugiat sit amet, metus. Sed venenatis odio id eros. Phasellus placerat purus vel mi. In hac habitasse platea dictumst. Donec aliquam porta odio. Ut facilisis. Donec ornare ipsum ut massa.</p>
<p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"2 columnes de text"
    resum = u"A cada columna s'hi poden afegir altres plantilles."
    cos = u"""<h2>2 columnes de text</h2>
<div class="row-fluid">
<div class="span6">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span6">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"3 columnes de text"
    resum = u"A cada columna s'hi poden afegir altres plantilles."
    cos = u"""<h2>3 columnes de text</h2>
<div class="row-fluid">
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"4 columnes de text"
    resum = u"A cada columna s'hi poden afegir altres plantilles."
    cos = u"""<h2>4 columnes de text</h2>
<div class="row-fluid">
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"2/3 vs 1/3 columnes de text"
    resum = u"A cada columna s'hi poden afegir altres plantilles."
    cos = u"""<h2>2/3 vs 1/3 columnes de text</h2>
<div class="row-fluid">
<div class="span8">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"3/4 vs 1/4 columnes de text"
    resum = u"A cada columna s'hi poden afegir altres plantilles."
    cos = u"""<h2>3/4 vs 1/4 columnes de text</h2>
<div class="row-fluid">
<div class="span9">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Combinacions de columnes"
    resum = u"Podeu fer d'1 a 4 columnes i fusionar-les entre elles. Elimineu les combinacions que no us interessin i treballeu amb el columnat que us agradi més."
    cos = u"""<h2>Columnat 4 columnes</h2>
<div class="row-fluid">
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
</div>
<h2>Columnat de 4 columnes amb 2 i 3 fusionades</h2>
<div class="row-fluid">
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span6">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
</div>
<h2>Columnat de 3 columnes</h2>
<div class="row-fluid">
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
<div class="span4">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
</div>
<h2>Columnat de 2 columnes amb 1, 2 i 3 fusionades</h2>
<div class="row-fluid">
<div class="span9">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type book.</div>
<div class="span3">Lorem Ipsum is simply dummy text of the printing and typesetting industry.</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Columna de suport"
    resum = u"Afegiu enllaços i contingut de suport a la columna de la dreta."
    cos = u"""<h2>Titular del bloc de text</h2>
<div class="row-fluid">
<div class="span8">
<p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. Lorem Ipsum is simply dummy text of the printing and typesetting industry.</p>
<p>Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled.</p>
</div>
<div class="span4">
<div class="box pull-right">
<h3 class="xic gris">Enllaços relacionats</h3>
<ul class="list list-links">
<li><a href="#">JDuis tellus</a></li>
<li><a href="#">Maecenas elit orci</a></li>
<li><a href="#">At ipsum vitae est lacinia tincidunt</a></li>
</ul>
<h3 class="xic gris">Bàners</h3>
<a href="#"><img alt="mostra" src="++genweb++static/example-images/banerMostra1linia_gw3.png" /></a> <a href="#"><img alt="mostra" src="++genweb++static/example-images/banerMostra1linia_gw3.png" /></a></div>
</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Destacat"
    resum = u"Text destacat."
    cos = u"""<p class="lead">In aliquam rhoncus sem. Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Destacat color"
    resum = u"Destacat amb text més gran i color."
    cos = u"""<div class="destacatBandejat">
<p>In aliquam rhoncus sem. Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue.</p>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Destacat contorn"
    resum = u"Destacat amb text petit."
    cos = u"""<div class="destacatQuadres">
<div class="destacatQuadresDins">
<p>In aliquam rhoncus sem. Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus.</p>
</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Pou"
    resum = u"Contenidor de pou per encabir elements i limitar-los visualment."
    cos = u"""<div class="well">
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, <a href="javascript: ;">purus nibh vehicula sem</a>, eu egestas ante nisl non justo. Fusce tincidunt, lorem nec dapibus consectetuer, leo orci mollis ipsum, eget suscipit eros purus in ante.</p>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Pou degradat"
    resum = u"Contenidor de pou per encabir elements i limitar-los visualment amb fons degradat."
    cos = u"""<div class="well well-gradient">
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, <a href="javascript: ;">purus nibh vehicula sem</a>, eu egestas ante nisl non justo. Fusce tincidunt, lorem nec dapibus consectetuer, leo orci mollis ipsum, eget suscipit eros purus in ante.</p>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Caixa"
    resum = u"Contenidor de caixa per encabir elements i limitar-los visualment."
    cos = u"""<div class="box">
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, <a href="javascript: ;">purus nibh vehicula sem</a>, eu egestas ante nisl non justo. Fusce tincidunt, lorem nec dapibus consectetuer, leo orci mollis ipsum, eget suscipit eros purus in ante.</p>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Caixa degradat"
    resum = u"Contenidor de caixa per encabir elements i limitar-los visualment amb fons degradat."
    cos = u"""<div class="box box-gradient">
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, <a href="javascript: ;">purus nibh vehicula sem</a>, eu egestas ante nisl non justo. Fusce tincidunt, lorem nec dapibus consectetuer, leo orci mollis ipsum, eget suscipit eros purus in ante.</p>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Taula"
    resum = u"Taula sense estils."
    cos = u"""<h3><span>Taula Table</span></h3>
<table class="table">
<thead>
<tr><th>#</th><th>Columna 1</th><th>Columna 2</th><th>Columna 3</th><th>Columna 4</th></tr>
</thead>
<tfoot>
<tr>
<td colspan="5">Peu de la taula</td>
</tr>
</tfoot>
<tbody>
<tr>
<td>Lorem ipsum</td>
<td>Dolor sum</td>
<td>Consecuteur est</td>
<td>Sit amet</td>
<td>Lorem ipsum</td>
</tr>
<tr>
<td>Consecuteur est</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
<td>Dolor sum</td>
<td>Sit amet</td>
</tr>
<tr>
<td>Sit amet</td>
<td>Consecuteur est</td>
<td>Dolor sum</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
</tr>
</tbody>
</table><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Taula colors destacats"
    resum = u"Taula amb colors destacats."
    cos = u"""<h3><span>Taula amb colors destacats</span></h3>
<table class="table">
<thead>
<tr><th>#</th><th>Columna 1</th><th class="error">Columna 2</th><th>Columna 3</th><th>Columna 4</th></tr>
</thead>
<tfoot>
<tr>
<td colspan="5">Peu de la taula</td>
</tr>
</tfoot>
<tbody>
<tr>
<td>Lorem ipsum</td>
<td>Dolor sum</td>
<td>Consecuteur est</td>
<td>Sit amet</td>
<td>Lorem ipsum</td>
</tr>
<tr>
<td class="warning">Consecuteur est</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
<td class="success">Dolor sum</td>
<td>Sit amet</td>
</tr>
<tr>
<td>Sit amet</td>
<td>Consecuteur est</td>
<td>Dolor sum</td>
<td class="info">Lorem ipsum</td>
<td>Sit amet</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Taula de registres per files"
    resum = u"Per definir una taula de registres estructurada per columnes. Es pot ampliar en files i columnes."
    cos = u"""<h3>Taula registres</h3>
<table class="taulaRegistres" summary="Detall d'estructura de la taula de registres"><caption>Subtítol taula</caption>
<tbody>
<tr class="cap">
<td></td>
<td>Item A</td>
<td>Item B</td>
<td>Item C</td>
<td>Item D</td>
<td>Total</td>
</tr>
<tr>
<td class="fonsDestacat1">DL</td>
<td>34</td>
<td>43</td>
<td>34</td>
<td>43</td>
<td>77</td>
</tr>
<tr>
<td class="fonsDestacat1">DT</td>
<td>34</td>
<td>43</td>
<td>34</td>
<td>43</td>
<td>77</td>
</tr>
<tr>
<td class="fonsDestacat1">DC</td>
<td>34</td>
<td>43</td>
<td>34</td>
<td>43</td>
<td>77</td>
</tr>
<tr>
<td class="fonsDestacat1">DJ</td>
<td>34</td>
<td>43</td>
<td>34</td>
<td>43</td>
<td>77</td>
</tr>
<tr>
<td class="fonsDestacat1">DV</td>
<td>34</td>
<td>43</td>
<td>34</td>
<td>43</td>
<td>77</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Taula amb estils"
    resum = u"Una taula amb vora, destacat ombrejat en passar per sobre amb el ratolí i diferenciació de columnes en diferents colors."
    cos = u"""<h3><span>Taula amb estils</span></h3>
<table class="table table-bordered table-striped table-hover">
<thead>
<tr><th>#</th><th>Columna 1</th><th>Columna 2</th><th>Columna 3</th><th>Columna 4</th></tr>
</thead>
<tfoot>
<tr>
<td colspan="5">Peu de la taula</td>
</tr>
</tfoot>
<tbody>
<tr>
<td>Lorem ipsum</td>
<td>Dolor sum</td>
<td>Consecuteur est</td>
<td>Sit amet</td>
<td>Lorem ipsum</td>
</tr>
<tr>
<td>Consecuteur est</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
<td>Dolor sum</td>
<td>Sit amet</td>
</tr>
<tr>
<td>Sit amet</td>
<td>Consecuteur est</td>
<td>Dolor sum</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Taula amb files destacades"
    resum = u"Una taula amb vora, diferenciació de primera fila i columna."
    cos = u"""<h3><span>Taula amb files destacades </span></h3>
<table class="table table-no-heading-border">
<thead>
<tr><th>#</th><th>Columna 1</th><th>Columna 2</th><th>Columna 3</th><th>Columna 4</th></tr>
</thead>
<tfoot>
<tr>
<td colspan="5">Peu de la taula</td>
</tr>
</tfoot>
<tbody>
<tr><th>Fila 1</th>
<td>Dolor sum</td>
<td>Consecuteur est</td>
<td>Sit amet</td>
<td>Lorem ipsum</td>
</tr>
<tr><th>Fila 2</th>
<td>Lorem ipsum</td>
<td>Sit amet</td>
<td>Dolor sum</td>
<td>Sit amet</td>
</tr>
<tr><th>Fila 3</th>
<td>Consecuteur est</td>
<td>Dolor sum</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
</tr>
<tr><th>Fila 4</th>
<td>Consecuteur est</td>
<td>Dolor sum</td>
<td>Lorem ipsum</td>
<td>Sit amet</td>
</tr>
</tbody>
</table><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Calendari"
    resum = u"Per representar gràficament els esdeveniments o activitats d'un mes determinat. Es pot representar tot un any afegint successivament un mes darrera l'altre."
    cos = u"""<table class="table table-bordered table-hover"><caption>Calendari de febrer</caption>
<thead>
<tr><th scope="col"><abbr title="Dilluns" data-placement="top">DL</abbr></th><th scope="col"><abbr title="Dimarts" data-placement="top">DT</abbr></th><th scope="col"><abbr title="Dimecres" data-placement="top">DC</abbr></th><th scope="col"><abbr title="Dijous" data-placement="top">DJ</abbr></th><th scope="col"><abbr title="Divendres" data-placement="top">DV</abbr></th><th scope="col"><abbr title="Dissabte" data-placement="top">DS</abbr></th><th scope="col"><abbr title="Diumenge" data-placement="top">DG</abbr></th></tr>
</thead>
<tfoot>
<tr><th colspan="7">Peu de la taula</th></tr>
</tfoot>
<tbody>
<tr>
<td> </td>
<td>1</td>
<td>2</td>
<td>3</td>
<td>4</td>
<td>5</td>
<td>6</td>
</tr>
<tr>
<td>7</td>
<td>8</td>
<td>9</td>
<td>10</td>
<td>11</td>
<td>12</td>
<td>13</td>
</tr>
<tr>
<td>14</td>
<td>15</td>
<td>16</td>
<td>17</td>
<td>18</td>
<td>19</td>
<td>20</td>
</tr>
<tr>
<td>21</td>
<td>22</td>
<td>23</td>
<td>24</td>
<td>25</td>
<td>26</td>
<td>27</td>
</tr>
<tr>
<td>28</td>
<td>29</td>
<td>30</td>
<td>31</td>
<td> </td>
<td> </td>
<td> </td>
</tr>
</tbody>
</table><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Fitxa"
    resum = u"Contenidor de fitxa."
    cos = u"""<div class="sheet">
<h2>Títol de la fitxa</h2>
<h3>At ipsum vitae est lacinia tincidunt</h3>
<img alt="" class="pull-right img-polaroid" src="++genweb++static/example-images/mostra.jpg" />
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, purus nibh vehicula sem, eu egestas ante nisl non justo.</p>
<h3>At ipsum vitae est lacinia tincidunt</h3>
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, purus nibh vehicula sem, eu egestas ante nisl non justo.</p>
<h3>At ipsum vitae est lacinia tincidunt</h3>
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec ante dolor, iaculis nec, gravida ac, cursus in, eros. Mauris vestibulum, felis et egestas ullamcorper, purus nibh vehicula sem, eu egestas ante nisl non justo.</p>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Àlbum de fotografies"
    resum = u"Crea un àlbum amb les miniatures de fotografies."
    cos = u"""<h2>Àlbum de Fotografies</h2>
<div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg1.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg1.jpg" class="estilImgPhotoAlbum3" src="++genweb++static/example-images/sampleimg1.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg1.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg2.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg2.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg2.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg2.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg3.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg3.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg3.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg3.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg4.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg4.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg4.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg4.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg5.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg5.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg5.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg5.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg6.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg6.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg6.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg6.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg7.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg7.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg7.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg7.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg8.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg8.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg8.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg8.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg9.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg9.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg9.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg9.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg10.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg10.jpg" class="estilImgPhotoAlbum2" src="++genweb++static/example-images/sampleimg10.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg10.jpg</span> </a></div>
<div class="photoAlbumEntry"><a href="++genweb++static/example-images/sampleimg11.jpg"> <span class="photoAlbumEntryWrapper"> <img alt="sampleimg11.jpg" class="estilImgPhotoAlbum1" src="++genweb++static/example-images/sampleimg11.jpg" /> </span> <span class="photoAlbumEntryTitle">sampleimg11.jpg</span> </a></div>
<div class="visualClear"></div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Imatge alineada a l'esquerra amb text "
    resum = u"Imatge alineada a l'esquerra amb text."
    cos = u"""<h2>Imatge alineada a l'esquerra amb text</h2>
<div>
<img alt="" class="image-left" src="++genweb++static/example-images/mostra.jpg" />
Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus. Nulla non orci. In egestas porttitor quam. Duis nec diam eget nibh mattis tempus. Curabitur accumsan pede id odio. Nunc vitae libero. Aenean condimentum diam et turpis. Vestibulum non risus. Ut consectetuer gravida elit. Aenean est nunc, varius sed, aliquam eu, feugiat sit amet, metus. Sed venenatis odio id eros. Phasellus placerat purus vel mi. In hac habitasse platea dictumst. Donec aliquam porta odio. Ut facilisis. Donec ornare ipsum ut massa.
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Imatge alineada a la dreta amb text "
    resum = u"Imatge alineada a la dreta amb text."
    cos = u"""<h2>Imatge alineada a la dreta amb text</h2>
<div>
<img alt="" class="image-right" src="++genweb++static/example-images/mostra.jpg" />
Morbi dictum. Vestibulum adipiscing pulvinar quam. In aliquam rhoncus sem. In mi erat, sodales eget, pretium interdum, malesuada ac, augue. Aliquam sollicitudin, massa ut vestibulum posuere, massa arcu elementum purus, eget vehicula lorem metus vel libero. Sed in dui id lectus commodo elementum. Etiam rhoncus tortor. Proin a lorem. Ut nec velit. Quisque varius. Proin nonummy justo dictum sapien tincidunt iaculis. Duis lobortis pellentesque risus. Nulla non orci. In egestas porttitor quam. Duis nec diam eget nibh mattis tempus. Curabitur accumsan pede id odio. Nunc vitae libero. Aenean condimentum diam et turpis. Vestibulum non risus. Ut consectetuer gravida elit. Aenean est nunc, varius sed, aliquam eu, feugiat sit amet, metus. Sed venenatis odio id eros. Phasellus placerat purus vel mi. In hac habitasse platea dictumst. Donec aliquam porta odio. Ut facilisis. Donec ornare ipsum ut massa.
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Imatge amb text lateral superposat"
    resum = u"Imatge damunt la qual hi apareix un text superposat."
    cos = u"""<h2>Títol [opcional]</h2>
<div id="FCKTdiv1imatgedamunttext"><img alt="foto mostra" src="++genweb++static/example-images/sampleimg9.jpg" />
<div id="FCKTdiv2imatgedamunttext">
<div id="FCKTdiv3imatgedamunttext">Lorem ipsum dolor sit amet consectetuer Vestibulum neque dolor felis malesuada. Id dolor magna enim pellentesque condimentum ante ullamcorper urna tellus id. At non Ut commodo consequat gravida sem vel tempus metus eleifend. Ridiculus pretium sit mauris pellentesque interdum tellus at id ante see interdum tellus at id ante semper.</div>
</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Assenyalar enllaços"
    resum = u"Classes que es poden afegir als enllaços per indicar el tipus d'element enllaçat."
    cos = u"""<h2>Classes especials per assenyalar enllaços</h2>
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore <a class="pdf" href="#">magna</a> aliquam erat volutpat. Ut wisi enim ad minim veniam, ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse <a class="doc" href="#">molestie</a> consequat, vel illum dolore eu te feugait nulla facilisi. Nam liber tempor nihil imperdiet doming id quod mazim placerat facer possim assum. Typi non <a class="ppt" href="#">habent claritatem</a> insitam; est usus legentis in iis qui. Investigationes demonstraverunt lectores legere me lius <a class="xlsdf" href="#">quod ii</a> legunt saepius. Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. <a class="down" href="#">Mirum est notare</a> quam littera gothica, parum claram, anteposuerit litterarum formas humanitatis <a class="txt" href="#">per seacula</a> quarta decima et quinta decima. <a class="https" href="#"> Eodem modo typi</a>, qui nunc nobis <a class="vid" href="#">videntur</a> parum clari, fiant <a class="img" href="#">sollemnes</a> in futurum.</p>
<p><strong>Les classes són:  pdf, doc, ppt, xls, down, txt, https, down, vid, img.</strong></p><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Carousel d'imatges"
    resum = u"Carousel d'imatges navegables."
    cos = u"""<div class="carousel slide" id="myCarousel"><!-- Carousel items -->
<div class="carousel-inner"><!--active item vol dir que és el que surt per defecte, el primer item-->
<div class="active item"><img alt="" src="++genweb++static/example-images/car1.jpg" />
<div class="carousel-caption">
<h4>Títol de la imatge 1</h4>
<p>Descripció de la imatge 1.</p>
</div>
</div>
<!--fi de active item --> <!--item-->
<div class="item"><img alt="" src="++genweb++static/example-images/car2.jpg" />
<div class="carousel-caption">
<h4>Títol de la imatge 2</h4>
<p>Descripció de la imatge 2.</p>
</div>
</div>
<!--fi item--> <!--item-->
<div class="item"><img alt="" src="++genweb++static/example-images/car1.jpg" />
<div class="carousel-caption">
<h4>Títol de la imatge 3</h4>
<p>Descripció de la imatge 3.</p>
</div>
</div>
<!--fi de active item --> <!--item-->
<div class="item"><img alt="" src="++genweb++static/example-images/car2.jpg" />
<div class="carousel-caption">
<h4>Títol de la imatge 4</h4>
<p>Descripció de la imatge 4.</p>
</div>
</div>
<!--fi de active item --></div>
<!-- Carousel nav --> <a class="carousel-control left" href="#myCarousel" data-slide="prev">‹</a> <a class="carousel-control right" href="#myCarousel" data-slide="next">›</a></div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Pestanyes"
    resum = u"Contingut segmentat per pestanyes amb un altre estil."
    cos = u"""<ul class="nav nav-tabs" id="myTab">
<li class="active"><a href="#primera" data-toggle="tab">Primera</a></li>
<li><a href="#segona" data-toggle="tab">Segona</a></li>
<li><a href="#tercera" data-toggle="tab">Tercera</a></li>
<li><a href="#quarta" data-toggle="tab">Quarta</a></li>
</ul>
<div class="tab-content">
<div class="tab-pane active" id="primera">Contingut de la primera pestanya...</div>
<div class="tab-pane" id="segona">Contingut de la segona pestanya...</div>
<div class="tab-pane" id="tercera">Contingut de la tercera pestanya...</div>
<div class="tab-pane" id="quarta">Contingut de la quarta pestanya...</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Pestanyes caixa"
    resum = u"Contingut segmentat per pestanyes."
    cos = u"""<div class="beautytab">
<ul id="myTab">
<li class="formTab firstFormTab active"><a href="#primera" data-toggle="tab">Primera</a></li>
<li class="formTab"><a href="#segona" data-toggle="tab">Segona</a></li>
<li class="formTab"><a href="#tercera" data-toggle="tab">Tercera</a></li>
<li class="formTab lastFormTab "><a href="#quarta" data-toggle="tab">Quarta</a></li>
</ul>
<div class="tab-content beautytab-content">
<div class="tab-pane active" id="primera">Contingut de la<br /><br /><br /><br /><br /> primera pestanya...</div>
<div class="tab-pane" id="segona">Contingut de la <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />segona pestanya...</div>
<div class="tab-pane" id="tercera">Contingut de la tercera pestanya...</div>
<div class="tab-pane" id="quarta">Contingut <br /><br /><br /><br /><br />de la quarta pestanya...</div>
</div>
</div><p>&nbsp;</p>"""
    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Acordió"
    resum = u"Acordió d'opcions."
    cos = u"""<div class="accordion" id="accordion2">
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle collapsed" href="#collapseOne" data-toggle="collapse" data-parent="#accordion2"> Collapsible Group Item #1 </a></div>
<div class="accordion-body collapse" id="collapseOne">
<div class="accordion-inner">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce volutpat ac neque hendrerit varius. Etiam a viverra dolor. Duis vitae ex sed tortor elementum egestas. Proin efficitur lacus ac porttitor condimentum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus velit magna, accumsan id arcu quis, laoreet maximus est. Nullam suscipit augue eget posuere convallis. Morbi cursus sagittis nisl at varius. Vestibulum lacinia sem consectetur, accumsan est et, feugiat urna. Vivamus sit amet eros a diam sodales vestibulum.</div>
</div>
</div>
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" href="#collapseTwo" data-toggle="collapse" data-parent="#accordion2"> Collapsible Group Item #2 </a></div>
<div class="accordion-body collapse" id="collapseTwo">
<div class="accordion-inner">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce volutpat ac neque hendrerit varius. Etiam a viverra dolor. Duis vitae ex sed tortor elementum egestas. Proin efficitur lacus ac porttitor condimentum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus velit magna, accumsan id arcu quis, laoreet maximus est. Nullam suscipit augue eget posuere convallis. Morbi cursus sagittis nisl at varius. Vestibulum lacinia sem consectetur, accumsan est et, feugiat urna. Vivamus sit amet eros a diam sodales vestibulum.</div>
</div>
</div>
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" href="#collapseThree" data-toggle="collapse" data-parent="#accordion2"> Collapsible Group Item #3 </a></div>
<div class="accordion-body collapse" id="collapseThree">
<div class="accordion-inner">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce volutpat ac neque hendrerit varius. Etiam a viverra dolor. Duis vitae ex sed tortor elementum egestas. Proin efficitur lacus ac porttitor condimentum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus velit magna, accumsan id arcu quis, laoreet maximus est. Nullam suscipit augue eget posuere convallis. Morbi cursus sagittis nisl at varius. Vestibulum lacinia sem consectetur, accumsan est et, feugiat urna. Vivamus sit amet eros a diam sodales vestibulum.</div>
</div>
</div>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Zoom imatge"
    resum = u"Imatge que s'amplia."
    cos = u"""<!-- Botó -->
<p><a href="#myModal" data-toggle="modal"><img class="image-inline" src="++genweb++static/example-images/anecs-petit.jpeg" /></a></p>
<!-- Modal -->
<div class="modal hide fade" id="myModal">
<div class="modal-header"><a class="close" data-dismiss="modal">×</a>
<h3 id="myModalLabel">Títol de la imatge</h3>
<img src="++genweb++static/example-images/anecs-gran.jpg" /></div>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Text amb video"
    resum = u"Per inserir-hi el vostre vídeo heu d'accedir al codi html de la pàgina i substituir l'enllaç al vídeo."
    cos = u"""<div>Donec in accumsan ex, eget facilisis risus. In id molestie erat. Sed congue ipsum ac consectetur posuere. Vestibulum posuere metus iaculis iaculis suscipit. Praesent pharetra massa eu ullamcorper blandit. Suspendisse consectetur porttitor eros, sed finibus mi posuere a. Donec quis massa eu enim maximus porttitor.</div>
<p>&nbsp;</p>
<div><video width="576" height="324" style="" poster="https://tv.upc.edu/contenidos/upc-la-universitat-enginyeria-arquitectura-ciencies-i-tecnologia/miniature_image" controls="controls"><source src="http://tv.upc.es/vod/Video_Grau_UPC_Cast-higher.mp4" type="video/mp4" /></video></div>
<p>&nbsp;</p>
<div>Vestibulum laoreet quis erat sed condimentum. Quisque faucibus et risus a gravida. Aliquam diam velit, mattis convallis eleifend sed, iaculis eget tellus. Donec et quam vel libero interdum mollis. Aenean nulla felis, vehicula eget metus eu, cursus scelerisque felis. Duis sem magna, bibendum eu sodales et, dapibus ac mi. Sed ut erat a tortor dictum fringilla sed blandit tortor.</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Botó ample blau"
    resum = u"Botó standard blau que ocupa el 100% de l'ample del contenidor"
    cos = u"""<a class="btn btn-block btn-large btn-primary" href="#">Lorem ipsum</a><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Botó ample gris"
    resum = u"Botó standard gris que ocupa el 100% de l'ample del contenidor"
    cos = u"""<a class="btn btn-block btn-large" href="#">Lorem ipsum</a><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Botó blau"
    resum = u"Botó standard blau"
    cos = u"""<a class="btn btn-large btn-primary" href="#">Button</a><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Botó"
    resum = u"Botó standard gris"
    cos = u"""<a class="btn btn-large" href="#">Button</a><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Imatge amb text superposat fosc"
    resum = u"Imatge amb text superposat en un bloc inferior fosc amb text blanc"
    cos = u"""<div class="text-over-image">
<img alt="" src="++genweb++static/example-images/car2.jpg" alt="" style="width:100%;" />
<div class="content dark-background">
    <div class="caption">
        <h4>Títol</h4>
        <p>Descripció</p>
    </div>
  </div>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    titol = u"Imatge amb text superposat clar"
    resum = u"Imatge amb text superposat en un bloc inferior clar amb text fosc"
    cos = u"""<div class="text-over-image">
<img alt="" src="++genweb++static/example-images/car2.jpg" alt="" style="width:100%;" />
<div class="content light-background">
    <div class="caption">
        <h4>Títol</h4>
        <p>Descripció</p>
    </div>
  </div>
</div><p>&nbsp;</p>"""

    plantilles.append({'titol': titol, 'resum': resum, 'cos': cos})

    return plantilles
