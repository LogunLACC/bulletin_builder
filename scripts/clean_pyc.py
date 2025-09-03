import os
root = os.path.dirname(os.path.dirname(__file__))
removed = []
for dirpath, dirnames, filenames in os.walk(root):
    if os.path.basename(dirpath) == '__pycache__':
        for f in list(filenames):
            if f.endswith('.pyc') and 'test_' in f:
                path = os.path.join(dirpath, f)
                try:
                    os.remove(path)
                    removed.append(path)
                except Exception as e:
                    print('err', path, e)
print('removed', len(removed), 'files')
for p in removed:
    print(' -', p)
