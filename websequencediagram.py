# -*- coding: utf-8 -*-

"""
    MoinMoin - websequencediagram
    Inspired by GoogleChart.py (http://moinmo.in/ParserMarket/GoogleChart)

    This parser creates a sequence diagram using a WebSequenceDiagram server, using
    the API described at http://www.websequencediagrams.com/embedding.html

    Configuration:
    - place in the data/plugin/parser directory of the moinmoin storage directory
    - restart server (if necessary, see http://moinmo.in/MoinDev/PluginConcept)

    Example usage:
    {{{
    #!websequencediagram
    Alice->Bob: password
    Bob->Alice: secret
    }}}

    Edit the variable wsd_url to point to the required server

    v0.1: 25-July-2011.  Basic implementation displaying PNG

    @license: GNU GPL
"""
import sys
import urllib
import re


Dependencies = ["page"]

wsd_url = "http://your_websequencediagrams_server_here:the_port/"

# from websequencediagrams documentation
def getSequenceDiagram( text, style = 'default' ):
    request = {}
    request["message"] = text
    request["style"] = style
    request["apiVersion"] = "1"

    url = urllib.urlencode(request)

    f = urllib.urlopen(wsd_url, url)
    line = f.readline()
    f.close()

    # line contains e.g.
    # {"img": "?png=mscKTO107", "errors": []}

    expr = re.compile("(\?(img|pdf|svg|png)=[a-zA-Z0-9]+)")
    m = expr.search(line)

    if m == None:
        print "Invalid response from server."
        return False

    # if re matched, then m.group(0) contains the filename of the image on the server
    return wsd_url + m.group(0)


class Parser:
    """ websequencediagrams parser """
    def __init__(self, raw, request, **kw):
        self.pagename      = request.page.page_name
        self.request       = request
        self.formatter     = request.formatter
        self.raw           = raw
        self.init_settings = True

        if 'debug' in kw['format_args']:
            self.debug = True

    def render(self, formatter):
        """ renders formular  """
        from MoinMoin.action import cache

        # checks if initializing of all attributes in __init__ was done
        if not self.init_settings:
            return

        # check if diagram on this page has been rendered before
        key = cache.key(self.request, itemname=self.pagename, content=self.raw)

        if not cache.exists(self.request, key):
            diagram_url = getSequenceDiagram(self.raw)
            image = urllib.urlopen(diagram_url)
            cache.put(self.request, key, image.read(), content_type="image/png")

        return formatter.image(src=cache.url(self.request, key), alt=self.raw)


    def format(self, formatter):
        """ parser output """
        # checks if initializing of all attributes in __init__ was done
        if self.init_settings:
            self.request.write(self.formatter.div(1, css_class="websequencediagram"))
            self.request.write(self.render(formatter))
            self.request.write(self.formatter.div(0))

if __name__ == "__main__":
    # debugging aid: run as script to check server is responding
    style = "qsd"
    text = "alice->bob: authentication request\nbob-->alice: response"

    diagram_url = getSequenceDiagram(text)

    print diagram_url # should print a json fragment containing a filename


