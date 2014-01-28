import json
import os

from . import action, File
from . import html
from . import util


@action
def parse_manifest(manifest_file):
  return json.loads(manifest_file.read())


def get_name_from_parsed_manifest(manifest):
  if 'short_name' in manifest:
    short_name = manifest['short_name']
  else:
    short_name = manifest['name'].replace(' ', '')

  return manifest['name'], short_name


def get_name_from_manifest(manifest_or_dir):
  if not isinstance(manifest_or_dir, File):
    return get_name_from_parsed_manifest(manifest_or_dir)

  if manifest_or_dir.isdir():
    manifest_or_dir = manifest_or_dir / 'manifest.json'

  manifest = parse_manifest(manifest_or_dir)
  return get_name_from_parsed_manifest(manifest)


def set_background_js(manifest, build_path, js_files):
  js_paths = [os.path.relpath(f.path, build_path) for f in js_files]
  if 'app' in manifest:
    manifest['app']['background']['scripts'] = js_paths
  else:
    manifest['background']['scripts'] = js_paths


@action
def build(source_dir, build_path, manifest, static_file_paths=None):
  build_files = []
  if static_file_paths is not None:
    build_files.extend(util.copy_files(source_dir, build_path,
                                       static_file_paths))

  build_manifest = File(os.path.join(build_path, 'manifest.json'))
  build_manifest.write(json.dumps(manifest))
  build_files.append(build_manifest)

  return util.delete_unlisted_files(build_path, build_files)


class Builder(object):
  def __init__(self, source_dir, build_path):
    self.source_dir = source_dir
    self.build_path = build_path
    self.static_file_paths = set()
    self.manifest = parse_manifest(source_dir / 'manifest.json')
    if 'icons' in self.manifest:
      self.add_static_files(self.manifest['icons'].values())

  def add_static_files(self, paths):
    self.static_file_paths |= set(paths)

  def add_static_file(self, path):
    self.static_file_paths.add(path)

  def add_html_file(self, html_path):
    html_file = File(html_path)
    self.add_static_file(html_path)
    html_dir = os.path.dirname(html_path)
    js_paths = html.extract_local_js(html_file)
    self.add_static_files(map(lambda p: os.path.join(html_dir, p), js_paths))

  def get_background_js(self):
    if 'app' in self.manifest:
      return self.manifest['app']['background']['scripts']
    else:
      return self.manifest['background']['scripts']

  def build(self):
    return build(self.source_dir, self.build_path, self.manifest,
                 self.static_file_paths)
