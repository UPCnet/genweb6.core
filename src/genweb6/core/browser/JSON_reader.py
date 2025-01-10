from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.dexterity.utils import createContentInContainer
from bs4 import BeautifulSoup, Comment
import re
from plone.app.textfield.value import RichTextValue
import logging
import datetime
import json
import xmltodict

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
            file = form['jsonfile']
            self.read_file(file)
    
    def read_file(self,file):
        if file.filename != '' and file.filename.endswith('.xml'):
            xmlparsed = xmltodict.parse(file)
            container = self.context
            rows = [x for x in xmlparsed['RESULTS']['ROW']]
            finalDict = {}
            for row in rows:
                finalDict['title'] = [x for x in row['COLUMN'] if x['@NAME'] == 'TITOL'][0]['#text']
                finalDict['text'] = [x for x in row['COLUMN'] if x['@NAME'] == 'CONTEN'][0]['#text']
                finalDict['text'] = RichTextValue(finalDict["text"], 'text/html', 'text/x-html-safe')
                finalDict['date'] = [x for x in row['COLUMN'] if x['@NAME'] == 'DATACT'][0]['#text']
                finalDict['subject'] = [[x for x in row['COLUMN'] if x['@NAME'] == 'ESPAI'][0]['#text']]
                finalDict["table_of_contents"] = True
                soup = BeautifulSoup(finalDict["text"].raw, 'html.parser')
                tags = soup.find_all(class_="minus")
                for tag in tags:
                    tag.name = 'h2'
                idBoxTags = soup.find_all('div', id=re.compile('box'))
                for tag in idBoxTags:
                    tag.unwrap()
                allTags = soup.find_all()
                invalid_tags = ['span']
                for tag in allTags:
                    del tag['class']
                    del tag['style']
                    if tag.name in invalid_tags:
                        tag.unwrap()
                    del tag['id']
                    if tag.name == 'a' and tag.get('href') and 'http' not in tag.get('href') or tag.name == 'a' and not tag.get('href'):
                        for content in tag.contents:
                            if isinstance(content, str):
                                content.replaceWith(content + ' [enllaçtrencat]')
                comments = soup.findAll(text=lambda text:isinstance(text, Comment))
                [comment.extract() for comment in comments]
                finalDict["text"] = RichTextValue(str(soup), 'text/html', 'text/x-html-safe')
                addedDate = RichTextValue('<div class="card my-5"><div class="card-body"><p class="card-text">Darrera actualització: ' + finalDict['date'] + '</p></div></div>', 'text/html', 'text/x-html-safe')
                finalDict['text'] = RichTextValue(finalDict["text"].raw + addedDate.raw, 'text/html', 'text/x-html-safe')
                offer = createContentInContainer(container, "Document", **finalDict)
                offer.setEffectiveDate(datetime.datetime.today())
                offer.reindexObject()
        # elif file.filename != '' and file.filename.endswith('.json'):
            # data = json.load(file, strict=False)
            # if self.base_JSON.keys() != data.keys():
            #     logging.info("The JSON file is not valid")
            # else:
            #     logging.info("The JSON file is valid")
            #     container = self.context
            #     data["text"] = RichTextValue(data["text"], 'text/html', 'text/x-html-safe')
            #     data["table_of_contents"] = True
            #     soup = BeautifulSoup(data["text"].raw, 'html.parser')
            #     tags = soup.find_all(class_="minus")
            #     for tag in tags:
            #         tag.name = 'h2'
            #     allTags = soup.find_all()
            #     for tag in allTags:
            #         del tag['class']
            #         if tag.name in invalid_tags:
            #             tag.unwrap()
            #         del tag['style']
            #         del tag['id']
            #         if tag.name == 'a' and tag.get('href') and 'http' not in tag.get('href') or tag.name == 'a' and not tag.get('href'):
            #             for content in tag.contents:
            #                 if isinstance(content, str):
            #                     content.replaceWith(content + ' [enllaçtrencat]')
            #     comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            #     [comment.extract() for comment in comments]
            #     data["text"] = RichTextValue(str(soup), 'text/html', 'text/x-html-safe')
            #     offer = createContentInContainer(container, "Document", **data)
            #     offer.setEffectiveDate(datetime.datetime.today())
            #     offer.reindexObject()
        else:
            logging.info("The file is not a JSON file or an xml file")