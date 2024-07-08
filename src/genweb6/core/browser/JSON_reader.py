from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.dexterity.utils import createContentInContainer
from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue
import logging
import datetime
import json

class read(BrowserView):

    render = ViewPageTemplateFile("views_templates/JSON_template.pt")
    base_JSON = {
            "title": "title",
            "description": "description",
            "text": """<div>
            <p>Texto de prueba</p>
            <div>"""
        }
    def __call__(self):
        # import ipdb; ipdb.set_trace()
        logging.info("I entered the class read")
        form = self.request.form
        if not form:
            return self.render()
        else:
            JSON_file = form['jsonfile']
            self.read_JSON(JSON_file)
    
    def read_JSON(self,JSON_file):
        if JSON_file.filename != '' and JSON_file.filename.endswith('.json'):
            data = json.load(JSON_file, strict=False)
            if self.base_JSON.keys() != data.keys():
                logging.info("The JSON file is not valid")
            else:
                logging.info("The JSON file is valid")
                container = self.context
                data["text"] = RichTextValue(data["text"], 'text/html', 'text/x-html-safe')
                data["table_of_contents"] = True
                soup = BeautifulSoup(data["text"].raw, 'html.parser')
                tags = soup.find_all(class_="minus")
                for tag in tags:
                    tag.name = 'h2'
                allTags = soup.find_all()
                for tag in allTags:
                    tag['class'] = ''
                    tag['style'] = ''
                    if tag.name == 'a' and tag.get('href') and 'http' not in tag.get('href') or tag.name == 'a' and not tag.get('href'):
                        for content in tag.contents:
                            if isinstance(content, str):
                                content.replaceWith(content + ' [enllaçtrencat]')
                data["text"] = RichTextValue(str(soup), 'text/html', 'text/x-html-safe')
                offer = createContentInContainer(container, "Document", **data)
                offer.setEffectiveDate(dt_start_of_day(datetime.datetime.today() + datetime.timedelta(1)))
                offer.setExpirationDate(dt_end_of_day(datetime.datetime.today() + datetime.timedelta(365)))
                offer.reindexObject()
        else:
            logging.info("The file is not a JSON file")