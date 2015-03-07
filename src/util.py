import sys
def init_config():
	import os
	if os.path.exists('settings.json') == False:
		file = open('settings.json','w')
		savedir = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\','\\\\')+'\\\image'
		d = '{"lockeyes": true, "denoise": false, "savedir": \"%s\","vposcount": "40", "hposcount": "50"}' %savedir
		file.write(d)
		file.close()

def updatedb():
	import os
	try:
	    import cPickle as pickle
	except ImportError:
	    import pickle
	
	if os.path.exists('db.pkl') == False:
		file = open('db.pkl','w')
		file.close()
	arr = []
	with open('db.pkl','rb') as pkl:
	    try:
	    	import os
	        arr = pickle.load(pkl)
	        for d in arr:
	        	if os.path.exists(d.get('path')) == False:
	        		arr.remove(d)
	    except:
	        pass
	with open('db.pkl','wb') as pkl:
	    pickle.dump(arr,pkl)