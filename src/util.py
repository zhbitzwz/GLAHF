import os
import sys
import time
import hashlib

from common import *
from functools import wraps
try:
    import cPickle as pickle
except ImportError:
    import pickle


def init_config():
    if os.path.exists(SETTING_FILE) == False:
        file = open(SETTING_FILE,'w')
        savedir = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\','\\\\')+'\\\image'
        d = '''{"lockeyes": true, "savedir": \"%s\",
                            "vposcount": "60", "hposcount": "80"}''' %savedir
        file.write(d)
        file.close()

def db_array():
    arr = []
    with open(DATA_FILE,'rb') as db:
        try:
            arr = pickle.load(db)
        except IOError:
            print "database does not exists!"
    return arr

def direct_write_db(arr):
    try:
        with open(DATA_FILE,'wb') as db:
            pickle.dump(arr,db)
    except IOError:
        print "writing is failed"

def insert_to_db(dict_):
    arr = db_array()
    arr.append(dict_)
    direct_write_db(arr)

def update_db():
    arr = []
    if os.path.exists(DATA_FILE) == False:
        with open(DATA_FILE,'w') as db:
            pickle.dump([],db)
    else:
        arr = db_array()
    if arr is not None:
        for d in arr:
            if os.path.exists(d.get('path')) == False:
                arr.remove(d)
    direct_write_db(arr)

def get_memory():
    try:
        with open(STUDY_FILE,'rb') as memory_file:
            m_linesArr = pickle.load(memory_file)[0]
        return m_linesArr
    except IOError:
        return None

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print "Total time running <%s>: %s seconds" %(function.func_name, str(t1-t0))
        return result
    return function_timer

def memory_study(function):
    @wraps(function)
    def _memory_study(*args, **kw):
        result = function(*args,**kw)
        linesArr = result[0]
        status = result[1]
        if status is False:
            return result
        try:
            if os.path.exists(STUDY_FILE) == False:
                with open(STUDY_FILE,'wb') as pkl:
                    pickle.dump((linesArr,1),pkl)
            else:
                with open(STUDY_FILE,'rb') as memory_file:
                    m_linesArr,count = pickle.load(memory_file)
                    VLines = sorted([i for i in linesArr if i.get('y')==0],key=lambda x:x.get('x'))
                    HLines = sorted([i for i in linesArr if i.get('x')==0],key=lambda x:x.get('y'))
                    m_VLines = sorted([i for i in m_linesArr if i.get('y')==0],key=lambda x:x.get('x'))
                    m_HLines = sorted([i for i in m_linesArr if i.get('x')==0],key=lambda x:x.get('y'))
                for now, memory in zip(VLines, m_VLines):
                    memory['x'] = (now.get('x')+memory.get('x')*count)/(count+1)
                for now, memory in zip(HLines, m_HLines):
                    memory['y'] = (now.get('y')+memory.get('y')*count)/(count+1)
                m_linesArr = m_VLines+m_HLines
                with open(STUDY_FILE,'wb') as memory_file:
                    pickle.dump((m_linesArr,count+1), memory_file)
        finally:
            return result
    return _memory_study

cache = {}

def is_obsolete(entry, duration):
    return time.time() - entry['time'] > duration

def compute_key(function, args, kw):
    key = pickle.dumps((function.func_name, args, kw))
    return hashlib.sha1(key).hexdigest()

def memorize(duration=10):
    def _memorize(function):
        def __memorize(*args, **kw):
            key = compute_key(function,args,kw)
            if (key in cache and
                not is_obsolete(cache[key], duration)):
                if os.path.exists(cache[key]['value']['path']) == False:
                    return function(*args,**kw)
                return cache[key]['value']
            result = function(*args,**kw)
            cache[key] = {'value': result,
                            'time': time.time()}
            return result
        return __memorize
    return _memorize