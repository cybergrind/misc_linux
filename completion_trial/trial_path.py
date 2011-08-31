#!/usr/bin/env python2

import sys
import os
from os.path import exists, isdir, isfile, join
import glob
from unittest import TestCase


def comp_files(pth, curr=None, rest=None):
    print pth

PKG = 'package'
PYTHON_FILE = 'python_file'
PYTHON_CLS = 'python_class'
PART_PYTHON = 'partial_python'


def comp_dots_start(pth):
    '''
    initial start of comp_dots, when curr is None
    '''
    rest = pth.split('.')
    curr = rest.pop(0)
    curr_pth = curr
    if exists(curr_pth) and isdir(curr_pth) and exists('%s/__init__.py'%curr_pth):
        comp_dots(pth, curr, curr_pth, rest, _type=PKG)
        return
    elif not exists(curr_pth) and exists('%s.py'%curr_pth) and isfile('%s.py'%curr_pth):
        curr_pth = '%s.py'%curr_pth
        # hack for get module
        _m = __import__(curr)
        __builtins__.__dict__[curr] = _m
        _module = eval(curr)
        comp_dots(pth, curr, curr_pth, rest, PYTHON_FILE, _module)
    else:
        return

def comp_dots_package(pth, curr, curr_pth, rest):
    rest = filter(None, rest)
    if len(rest) == 0:
        # complete inner packages and python files
        acc = []
        files = []
        gl = glob.glob('%s/*'%curr_pth)
        if len(gl) == 0:
            gl = glob.glob('%s*'%curr_pth)
        for i in gl:
            if isdir(i) and exists('%s/__init__.py'%i):
                acc.append(i.replace('/', '.'))
            elif isfile(i) and i.endswith('.py'):
                acc.append(i[:-3].replace('/', '.'))
                files.append(i)
        if len(acc) == 1 and len(files) != 0:
            module_pth = acc[0]
            pth = module_pth
            new_curr = pth.split('.')[-1]
            _m = __import__(module_pth)
            __builtins__.__dict__[module_pth.split('.')[0]] = _m
            _module = eval(module_pth)
            comp_dots(pth, new_curr, _module.__file__, rest, PYTHON_FILE, _module)
            return
        for i in acc:
            print i
    elif len(rest) > 1:
        new_curr = rest.pop(0)
        new_pth = join(curr_pth, new_curr)
        if exists(new_pth) and isdir(new_pth) and exists('%s/__init__.py'%new_pth):
            comp_dots(pth, new_curr, new_pth, rest, _type=PKG)
            return
        file_pth = '%s.py'%new_pth
        if exists(file_pth):
            module_pth = new_pth.replace('/', '.')
            _m = __import__(module_pth)
            __builtins__.__dict__[module_pth.split('.')[0]] = _m
            _module = eval(module_pth)
            comp_dots(pth, new_curr, _module.__file__, rest, PYTHON_FILE, _module)
            return
    else:
        new_curr = rest.pop(0)
        if pth.endswith('.'):
            new_pth = join(curr_pth, new_curr)
            comp_dots(pth, new_curr, new_pth, rest, PKG)
            return
        gl = glob.glob('%s/%s*'%(curr_pth, new_curr))
        if len(gl) == 1:
            new_pth = gl[0]
            if isdir(new_pth) and exists('%s/__init__.py'%new_pth):
                pth = new_pth.replace('/', '.')
                new_curr = new_pth.split('/')[-1]
                
                comp_dots(pth, new_curr, new_pth, rest, PKG)
                return
            elif isfile(new_pth) and new_pth.endswith('.py'):
                module_pth = new_pth.replace('/', '.')
                _m = __import__(module_pth)
                __builtins__.__dict__[module_pth.split('.')[0]] = _m
                _module = eval(module_pth)
                comp_dots(pth, new_curr, _module.__file__, rest, PYTHON_FILE, _module)
                return
            else:
                raise Exception('strng')
        else:
            acc = []
            files = []
            for i in gl:
                if isdir(i) and exists('%s/__init__.py'%i):
                    acc.append(i.replace('/', '.'))
                elif isfile(i) and i.endswith('.py'):
                    file_name = i[:-3].replace('/', '.')
                    acc.append(file_name)
                    files.append(i)
            if len(acc) > 1:
                for i in acc:
                    print i
            elif len(acc) == 1:
                if len(files) == 0:
                    pth = acc[0]
                    comp_dots(pth, pth.split('.')[-1],
                              pth.replace('.', '/'), rest,
                              PKG)
                    return
                else:
                    module_pth = acc[0]
                    pth = module_pth
                    new_curr = pth.split('.')[-1]
                    _m = __import__(module_pth)
                    __builtins__.__dict__[module_pth.split('.')[0]] = _m
                    _module = eval(module_pth)
                    comp_dots(pth, new_curr, _module.__file__, rest, PYTHON_FILE, _module)
                    return
        
        

def comp_dots_file(pth, curr, rest, _module):
    mod_name = curr
    rest = filter(None, rest)
    if len(rest) == 0:
        acc = []
        for i in dir(_module):
            cls = getattr(_module, i)
            if isinstance(cls, type) and issubclass(cls, TestCase)\
               and len(filter(lambda x: x.startswith('test'), dir(cls)))>0:
                acc.append('%s.%s'%(pth, i))
        if len(acc) > 1:
            for i in acc:
                print i
        else:
            pth = acc[0]
            curr = pth.split('.')[-1]
            _element = getattr(_module, curr)
            comp_dots(pth, curr, curr_pth=_module.__file__,
                      rest=rest, _type=PYTHON_CLS,
                      element=_element)
    elif len(rest) == 1:
        curr = rest.pop(0)
        acc = []
        for i in dir(_module):
            cls = getattr(_module, i)
            # test that cls is subclass of TestCase
            # and have inner tests
            if isinstance(cls, type) and issubclass(cls, TestCase)\
                   and len(filter(lambda x: x.startswith('test'), dir(cls)))>0:
                if i == curr and pth.endswith('.'):
                    comp_dots(pth, curr, curr_pth=_module.__file__,
                              rest=rest, _type=PYTHON_CLS,
                              element=getattr(_module, i))
                    return
                elif i.startswith(curr):
                    acc.append(i)
        if len(acc) == 1:
            _element = getattr(_module, acc[0])
            new_pth = pth.split('.')[:-1]
            new_pth.append(acc[0])
            pth = '.'.join(new_pth)
            
            comp_dots(pth, curr, curr_pth=_module.__file__,
                      rest=rest, _type=PYTHON_CLS,
                      element=_element)
        else:
            for i in acc:
                print '%s%s.'%(pth, i)
        return
    else:
        curr = rest.pop(0)
        _element = getattr(_module, curr)
        comp_dots(pth, curr, curr_pth=_module.__file__,
                  rest=rest, _type=PYTHON_CLS,
                  element=_element)

def comp_dots_cls(pth, curr, rest, element):
    rest = filter(None, rest)
    if len(rest) == 0:
        for i in dir(element):
            if i.startswith('test'):
                _last = pth.split('.')[-1]
                if _last == element.__name__:
                    print '%s.%s'%(pth, i)
                else:
                    temp_pth = pth.split('.')[:-1]
                    cls_pth = '.'.join(temp_pth)
                    print '%s.%s'%(cls_pth, i)
    elif len(rest) == 1:
        temp_pth = pth.split('.')[:-1]
        cls_pth = '.'.join(temp_pth)
        new_curr = rest.pop(0)
        for i in dir(element):
            if i.startswith(new_curr):
                print '%s.%s'%(cls_pth, i)
        
def comp_dots(pth, curr=None, curr_pth=None,
               rest=None, _type=None, element=None):
    '''
    pth - current input string
    curr - current part of input
    curr_pth - current path to dir or file, without trailing slash
    rest - pth splited by dot rest
    _type - type of current element
    element - loaded module or class
    '''
    if not curr:
        comp_dots_start(pth)
        return
    elif _type == PKG:
        comp_dots_package(pth, curr, curr_pth, rest)
        return
    elif _type == PYTHON_FILE:
        comp_dots_file(pth, curr, rest, element)
        return
    elif _type == PYTHON_CLS:
        comp_dots_cls(pth, curr, rest, element)
        return
    raise Exception(_type)

def comp_initial(pth):
    if '/' in pth:
        comp_files(pth)
    elif '.' in pth and pth != '.':
        comp_dots(pth)
    else:
        acc = []
        for i in glob.glob('%s*'%pth):
            if isdir(i) and exists('%s/__init__.py'%i):
                acc.append(i)
            elif isfile(i) and i.endswith('.py'):
                print i[:-3]
        if len(acc) == 1:
            comp_dots(acc[0])
        else:
            for i in acc:
                print i
    return
    

def complete(pth):
    if pth == '.':
        comp_initial(pth)
    elif '.' in pth:
        comp_dots(pth)
    else:
        comp_initial(pth)



def main():
    #print sys.argv
    if len(sys.argv) > 1:
        pth = sys.argv[1]
        complete(pth)
    else:
        complete('')


if __name__ == '__main__':
    main()
