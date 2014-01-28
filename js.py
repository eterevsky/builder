from . import action, File


@action
def concatenate(source_files):
  res = ''
  for f in source_file:
    res += f.read() + '\n'
  return res


@action
def compile(source_files, target_path, method='concatenate'):
  if method == 'concatenate':
    out = File(target_path)
    out.write(concatentae(source_files))
    return out
  raise Exception()
