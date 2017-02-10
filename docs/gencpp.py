#!/usr/bin/env python3
#
# The C++ extension cannot be easily built on RTD, so instead periodically
# the documentation gets automatically generated using this and then it is
# checked into git.
#
# From http://stackoverflow.com/questions/2668187/make-sphinx-generate-rst-class-documentation-from-pydoc
#

import inspect
import os
from os.path import abspath, exists, dirname, join
import shutil

root = abspath(dirname(__file__))
gendir = join(root, '..', '_docgen')
if exists(gendir):
    shutil.rmtree(gendir)

os.makedirs(gendir)
shutil.copy('conf.py', gendir)
shutil.copy('gensidebar.py', gendir)

os.chdir(gendir)

from cscore import _cscore

fns = []
clss = []

for n in dir(_cscore):
    if n.startswith('_'):
        continue
    o = getattr(_cscore, n)
    if inspect.isclass(o):
        clss.append(n)
    elif inspect.isfunction(o) or inspect.isbuiltin(o):
        fns.append(n)
    else:
        raise ValueError("Unknown thing: %s (%s)" % (n, o))

def _writeheader(fp):
    print(".. THIS FILE IS AUTOGENERATED, DO NOT MODIFY\n", file=fp)
    print("Objects", file=fp)
    print("=======", file=fp)
    fp.write('\n')

with open(join(gendir, 'index.rst'), 'w') as fp:
    _writeheader(fp)
    
    for cls in sorted(clss):
        print('.. autoclass:: cscore.%s' % cls, file=fp)
        print('   :members:', file=fp)
        print('   :undoc-members:', file=fp)
        fp.write('\n')
        
    for fn in sorted(fns):
        print('.. autofunction:: cscore.%s\n' % fn, file=fp)

import sphinx.ext.autodoc
rst = []
def add_line(self, line, source, *lineno):
    """Append one line of generated reST to the output."""
    rst.append(line)
    self.directive.result.append(self.indent + line, source, *lineno)
sphinx.ext.autodoc.Documenter.add_line = add_line
try:
    os.environ['GENERATING_CPP'] = '1'
    sphinx.main(['sphinx-build', '-b', 'html', '-d', '_build/doctrees', '.', '_build/html', 'index.rst'])
except SystemExit:
    with open(join(root, 'objects.rst'), 'w') as fp:
        _writeheader(fp)
        
        # Format the output a bit..
        for l in rst:
            l = l.replace('cscore._cscore', 'cscore')
            if l.startswith('.. py:class:: '):
                e = l.find('(') 
                if e == -1:
                    e = len(l)
                name = l[14:e]
                if '.' not in name:
                    print(name, file=fp)
                    print('-'*len(name), file=fp)
                    print('', file=fp)
            
            print(l, file=fp)

if exists(gendir):
    shutil.rmtree(gendir)