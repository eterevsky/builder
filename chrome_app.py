import json
import os

from . import action, File
from . import dist
from . import html


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


class Builder(object):
  def __init__(self, source_dir, build_path, add_js=False):
    self.dist_builder = dist.Builder(source_dir, build_path)
    self.manifest = parse_manifest(source_dir / 'manifest.json')
    if 'icons' in self.manifest:
      self.dist_builder.copy_files_same_path(self.manifest['icons'].values())
    if add_js:
      self.dist_builder.copy_files_same_path(self.get_background_js())

  def set_version(self, version):
    self.manifest['version'] = version

  def copy_file(self, src, dest_path):
    self.dist_builder.copy_file(src, dest_path)

  def add_static_files(self, paths):
    self.dist_builder.copy_files_same_path(paths)

  def add_html_file(self, html_file, path, add_js=False):
    self.dist_builder.copy_file(html_file, path)
    if add_js:
      html_dir = os.path.dirname(path)
      relative_js_paths = html.extract_local_js(html_file)
      js_paths = map(lambda p: os.path.join(html_dir, p), relative_js_paths)
      self.dist_builder.copy_files_same_path(js_paths)

  def get_background_js(self):
    if 'app' in self.manifest:
      return self.manifest['app']['background']['scripts']
    else:
      return self.manifest['background']['scripts']

  def replace_background_js(self, old_scripts, new_script):
    background_js = self.get_background_js()
    background_js[:] = filter(lambda p: p not in old_scripts, background_js)
    background_js.append(new_script)

  def build(self):
    self.dist_builder.write_file('manifest.json', json.dumps(self.manifest))
    return self.dist_builder.build()
