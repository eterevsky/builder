import html
import html.parser
from urllib.parse import urlparse

from . import action, File

class _ScriptsExtractor(html.parser.HTMLParser):
  def __init__(self):
    super(_ScriptsExtractor, self).__init__()
    self.script_uris = []

  def handle_starttag(self, tag, attrs):
    if tag != 'script':
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


class _ScriptsReplacer(html.parser.HTMLParser):
  def __init__(self, js_paths):
    super(_ScriptsReplacer, self).__init__()
    self._js_paths = set(js_paths)
    self.first_pos = None
    self.script_attr = None
    self.other_pos = []
    self._inside_replaced_script = False

  def handle_starttag(self, tag, attrs):
    if tag != 'script':
      self._inside_replaced_script = False
      return
    attr_dict = dict(attrs)
    if 'src' in attr_dict and attr_dict['src'] in self._js_paths:
      if self.first_pos is None:
        self.first_pos = self.getpos()
        self.script_attr = attrs
      else:
        self.other_pos.append((self.getpos(), None))
        self._inside_replaced_script = True

  def handle_endtag(self, tag):
    if tag != 'script':
      self._inside_replaced_script = False
      return
    if self._inside_replaced_script:
      assert len(self.other_pos) > 0
      start, finish = self.other_pos[-1]
      assert finish is None
      self.other_pos[-1] = (start, self.getpos())


def format_tag(tag, attr):
  attr_str = (n + '="' + html.escape(v, True) + '"' for n, v in attr)
  return '<' + tag + ' ' + ' '.join(attr_str) + '>'


@action
def replace_js(src, js_paths, new_js_path):
  """Replace the set of scripts in HTML by another 1 script.

  First <script> tag with url from js_paths is replaced by new_js_path. Others
  are simply removed.
  """
  replacer = _ScriptsReplacer(js_paths)
  data = src.read()
  replacer.feed(data)
  replacer.close()

  assert replacer.first_pos is not None
  attr = list(replacer.script_attr)
  for i in range(len(attr)):
    if attr[i][0] == 'src':
      attr[i] = ('src', new_js_path)

  out = File.create_temp()
  out.write(data[:replacer.first_pos])
  out.append(format_tag('script', attr))
  pos = data.find('>', replacer.first_pos) + 1

  for start, finish in replacer.other_pos:
    out.append(data[pos:start])
    pos = data.find('>', finish or start) + 1

  out.append(data[pos:])
  return out

