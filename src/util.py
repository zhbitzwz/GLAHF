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

def fn_timer(function):
	@wraps(function)
	def function_timer(*args, **kwargs):
		t0 = time.time()
		result = function(*args, **kwargs)
		t1 = time.time()
		print "Total time running %s: %s seconds" %(function.func_name, str(t1-t0))
		return result
	return function_timer
