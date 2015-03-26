#!/usr/bin/env python
#
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import jinja2
import os
import webapp2
import logging

from google.appengine.api import memcache


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        greetings = memcache.get('entries')
        if greetings is None:
            greetings = []
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(entries=greetings))
    def post(self):
        greeting = self.request.get('entry')
        greetings = memcache.get('entries')
        if greetings is not None:
            greetings.append(greeting)
            if not memcache.replace('entries', greetings):
                logging.error('Memcache replace failed.')
        else:
            greetings = [greeting]
            if not memcache.set('entries', greetings):
                logging.error('Memcache set failed.')
        self.redirect('/')


class Clear(webapp2.RequestHandler):
    def post(self):
        if not memcache.delete('entries'):
            logging.error("Memcache failed to delete entries")
        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/clear', Clear)
], debug=True)
