import html.parser
from urllib.parse import urlparse

from . import action

class _ScriptsExtractor(html.parser.HTMLParser):
  def __init__(self):
    super(_ScriptsExtractor, self).__init__()
    self.script_uris = []

  def handle_starttag(self, tag, attrs):
    if tag.lower() != 'script':
      return
    attr_dict = dict(attrs)
    if 'src' in attr_dict and ('type' not in attr_dict or
                               attr_dict['type'] == 'text/javascript'):
      self.script_uris.append(attr_dict['src'])

@action
def extract_local_js(html_file):
  extractor = _ScriptsExtractor()
  extractor.feed(html_file.read())
  extractor.close()
  uris = extractor.script_uris
  paths = []
  for uri in uris:
    parts = urlparse(uri)
    if not parts.netloc and not parts.params and not parts.query:
      paths.append(parts.path)
  return paths



