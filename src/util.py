import os
import sys
import time
from functools import wraps
try:
    import cPickle as pickle
except ImportError:
    import pickle


def init_config():
	if os.path.exists('settings.json') == False:
		file = open('settings.json','w')
		savedir = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\','\\\\')+'\\\image'
		d = '''{"lockeyes": true, "denoise": false, "savedir": \"%s\",
							"vposcount": "40", "hposcount": "50"}''' %savedir
		file.write(d)
		file.close()

def db_array():
	arr = []
	with open('db.pkl','rb') as db:
		try:
			arr = pickle.load(db)
		except IOError:
			print "database does not exists!"
	return arr

def direct_write_db(arr):
	try:
		with open('db.pkl','wb') as db:
			pickle.dump(arr,db)
	except IOError:
		print "writing is failed"

def insert_to_db(dict_):
	arr = db_array()
	arr.append(dict_)
	direct_write_db(arr)

def update_db():
	arr = []
	if os.path.exists('db.pkl') == False:
		with open('db.pkl','w') as db:
			pickle.dump([],db)
	else:
		arr = db_array()
	if arr is not None:
		for d in arr:
			if os.path.exists(d.get('path')) == False:
				arr.remove(d)
	direct_write_db(arr)

def get_memory():
	with open('memory.pkl','rb') as memory_file:
		m_linesArr = pickle.load(memory_file)
	return m_linesArr

def fn_timer(function):
	@wraps(function)
	def function_timer(*args, **kwargs):
		t0 = time.time()
		result = function(*args, **kwargs)
		t1 = time.time()
		print "Total time running %s: %s seconds" %(function.func_name, str(t1-t0))
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

		if os.path.exists('memory.pkl') == False:
			with open('memory.pkl','wb') as pkl:
				pickle.dump(linesArr,pkl)
		else:
			with open('memory.pkl','rb') as memory_file:
				m_linesArr = pickle.load(memory_file)
				VLines = sorted([i for i in linesArr if i.get('y')==0],key=lambda x:x.get('x'))
				HLines = sorted([i for i in linesArr if i.get('x')==0],key=lambda x:x.get('y'))
				m_VLines = sorted([i for i in m_linesArr if i.get('y')==0],key=lambda x:x.get('x'))
				m_HLines = sorted([i for i in m_linesArr if i.get('x')==0],key=lambda x:x.get('y'))
			for now, memory in zip(VLines, m_VLines):
				memory['x'] = (now.get('x')+memory.get('x'))/2
			for now, memory in zip(HLines, m_HLines):
				memory['y'] = (now.get('y')+memory.get('y'))/2
			m_linesArr = m_VLines+m_HLines
			with open('memory.pkl','wb') as memory_file:
				pickle.dump(m_linesArr, memory_file)
		return result
	return _memory_study
