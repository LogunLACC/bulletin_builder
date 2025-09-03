import sys
import importlib
import os
print('cwd', os.getcwd())
print('sys.path[0]', sys.path[0])
spec = importlib.util.find_spec('test_theme_modes')
print('spec', spec)
for root, dirs, files in os.walk('.'):
    for f in files:
        if f == 'test_theme_modes.py':
            print('found', os.path.join(root,f))
