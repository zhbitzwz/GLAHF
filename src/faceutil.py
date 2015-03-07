#-*- coding:utf-8 -*-

import json
import numpy as np
import threading
import math
from matplotlib import pyplot as plt
from enlarge import enlargeimage
import cv2
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

H = 50
V = 40
LOCK = False
DENOISE = False

# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
nose_cascade = cv2.CascadeClassifier('haarcascade_mcs_nose.xml')
mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')


def loadconfig():
	global H
	global V
	global LOCK
	global DENOISE
	with open('settings.json') as jsonfile:
	    config = json.load(jsonfile)
	    H = int(config['hposcount'])
	    V = int(config['vposcount'])
	    LOCK = config['lockeyes']
	    DENOISE = config['denoise']
	return H,V,LOCK,DENOISE

def fixsize(img,size):
	h,w = size
	return cv2.resize(img,(w,h),interpolation=cv2.INTER_LINEAR)

def drawlines(img
		,color=(0,0,0),px=0.5):
	global ARR
	vis = img.copy()
	height,width = vis.shape[:2]
	offheight,offwidth = float(height)/V,float(width)/H
	font = cv2.FONT_HERSHEY_PLAIN

	for i in range(1,V+1):
		cv2.line(vis,(0,int(i*offheight)),(width,int(i*offheight)),color,px)
	for i in range(1,H+1):
		cv2.line(vis,(int(i*offwidth),0),(int(i*offwidth),height),color,px)
	return vis

def splice_image(img,startpoint,endpoint,
			units=None):
	beginX = int(startpoint[0])
	beginY = int(startpoint[1])
	endX = int(endpoint[0])
	endY = int(endpoint[1])
	height,width = img.shape[:2]
	if units is not None:
		H = int(units[0])
		V = int(units[1])
		offheight,offwidth = float(height)/V,float(width)/H
	else:
		H,V = loadconfig()[:2]
		offheight,offwidth = float(height)/V,float(width)/H
		
	CanvasH = int(endY*offheight)-int(beginY*offheight)
	CanvasW = int(endX*offwidth)-int(beginX*offwidth)
	spliced_img = np.zeros((CanvasH,CanvasW),np.uint8)
	spliced_img[:] = img[int(beginY*offheight):int(endY*offheight),
								int(beginX*offwidth):int(endX*offwidth)]
	return spliced_img

def mergeImages(l,f,r,
			path='./',scale_dict=None):
	if l==None or f==None or r==None:
		return False
	leftImage = cv2.imread(l,0)
	H,V,LOCK,DENOISE = loadconfig()
	if LOCK is True:
		frontalImage = adjustface(f)
	else:
		frontalImage = cv2.imread(f,0)
	rightImage = cv2.imread(r,0)
	if leftImage is None or frontalImage is None or rightImage is None:
		return False

	if scale_dict is not None:
		from enlarge import enlargeimage
		if scale_dict["LSCALE"] > 0:
			leftImage = enlargeimage(leftImage, scale_dict["LSCALE"])
		if scale_dict["FSCALE"] > 0:
			frontalImage = enlargeimage(frontalImage, scale_dict["FSCALE"])
		if scale_dict["RSCALE"] > 0:
			rightImage = enlargeimage(rightImage, scale_dict["RSCALE"])

	if DENOISE is True:
		leftImage = cv2.GaussianBlur(leftImage,(5,5),0)
		frontalImage = cv2.GaussianBlur(frontalImage,(5,5),0)
		rightImage = cv2.GaussianBlur(rightImage,(5,5),0)
	size = frontalImage.shape[:2]
	leftImage = fixsize(leftImage,size)
	rightImage = fixsize(rightImage,size)
	vis = np.concatenate((leftImage, frontalImage, rightImage), axis=1)
	try:
	    import cPickle as pickle
	except ImportError:
	    import pickle
	id = 0
	with open('db.pkl','rb') as pkl:
	    try:
	        d = pickle.load(pkl)
	        id = len(d)
	    except:
	        pass
	import time
	import os
	today = str(time.strftime("%Y-%m-%d", time.localtime()))
	date = str(time.strftime("%Y-%m-%d %H:%M %p", time.localtime()))
	tardir = path+'\\'+today
	if os.path.exists(tardir) is False:
		os.mkdir(tardir)
	savepath = tardir+'\\'+str(int(time.time()))+'.jpg'
	cv2.imwrite(savepath,vis)
	vis2 = drawlines(vis,(0,0,0),1)
	cv2.imwrite(savepath[:-4]+'_preview.jpg',vis2)
	return dict(id=str(id+1),date=date,path=savepath,units=(H,V))

def getavggrayvalue(path,startpoint,endpoint
				,units=None):
	vis = cv2.imread(path,0)
	if vis is None:
		return
	if units is not None:
		spliced_img = splice_image(vis, startpoint, endpoint, units)
	else:
		spliced_img = splice_image(vis, startpoint, endpoint, None)
	return vis,spliced_img,round(spliced_img.mean(),5)

def roi_grayvalue(path,start_x,end_x,start_y,end_y):
	vis = cv2.imread(path,0)
	if vis is None:
		return
	height, width = vis.shape[:2]
	start_x = int(start_x*width)
	end_x = int(end_x*width)
	start_y = int(start_y*height)
	end_y = int(end_y*height)
	roi_img = np.zeros((end_y-start_y,end_x-start_x),np.uint8)
	roi_img[:] = vis[start_y:end_y, start_x:end_x]
	return round(roi_img.mean(),5)

def showplt(vis,spliced_img):
	from matplotlib.font_manager import FontProperties
	font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14)
	hist_full = cv2.calcHist([spliced_img],[0],None,[256],[0,256])
	plt.subplot(211),plt.imshow(spliced_img,'gray'),plt.title(u'结果', fontproperties=font)
	plt.subplot(212),plt.plot(hist_full,'gray'),plt.xlim([0,256])
	plt.xlabel(u'灰度范围', fontproperties=font)
	plt.ylabel(u'像素数量', fontproperties=font)
	plt.show()

def adjustface(face):
	FACTOR = 0.4

	if face is None or face=='':
		return None

	eyepos = []
	img = cv2.imread(face)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	height,width = img.shape[:2]

	# faces = face_cascade.detectMultiScale(gray, 1.3, 5)

	# for (x,y,w,h) in faces:
	# 	# cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
	# 	roi_gray = gray[y:y+h, x:x+w]
	# 	roi_color = img[y:y+h, x:x+w]
	# 	eyes = eye_cascade.detectMultiScale(roi_gray)
	# 	for(ex,ey,ew,eh) in eyes:
	# 		if ey < h/2:
	# 			eyepos.append(((2*(ex+x)+ew)/2,(2*(ey+y)+eh)/2))
	# 			# cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)


	eyes = eye_cascade.detectMultiScale(img)
	eyes = [item for item in eyes if item[1] > height/4 \
	                            and (2*item[1]+item[3])/2 < height*2/3]
	eyes = sorted(eyes,key=lambda item:item[1])[:2]
	eyes = sorted(eyes,key=lambda item:item[0])
	print "eyes counts:",len(eyes)

	if len(eyes) != 0:
		for index,(ex,ey,ew,eh) in enumerate(eyes):
			eyepos.append((ex+ew/2,ey+eh/2))

	if len(eyepos)==2:
		eyepos = sorted(eyepos,key=lambda item:item[0])
		leye = eyepos[0]
		reye = eyepos[1]
		# cv2.line(img,(leye[0],leye[1]),(reye[0],reye[1]),(0,0,255),2)

		yy = math.fabs(leye[1] - reye[1])
		xx = math.fabs(leye[0] - reye[0])
		degree = math.degrees(math.atan(yy/xx))

		if degree > 5:
			if reye[1] > leye[1]:
				M = cv2.getRotationMatrix2D((width/2,height/2),degree,1)
			else:
				M = cv2.getRotationMatrix2D((width/2,height/2),-degree,1)
		else:
			M = cv2.getRotationMatrix2D((width/2,height/2),0,1)

		dst = cv2.warpAffine(img,M,(width,height))

		real = cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY)

		distance = leye[0]-reye[0] if leye[0] > reye[0] else reye[0] - leye[0]
		proportion = float(distance)/width

		if FACTOR > proportion:
			scale = (width-distance/FACTOR)/(2*width)
			real = enlargeimage(real,scale)

		return real
	else:
		print "can not match the eyes."
	return gray

def markdetect(face):
	global face_cascade
	global eye_cascade
	global nose_cascade
	global mouth_cascade

	DARWEIGHT = 1

	linesArr = []

	real_height, real_width = face.shape[:2]

	noses = nose_cascade.detectMultiScale(face)
	noses = [item for item in noses if real_width*2/3 > (2*item[0]+item[2])/2 > real_width*1/3 \
	                            and real_width/3 > item[2] > real_width/8 \
	                            and real_height/4 < (2*item[1]+item[3])/2 < real_height*3/4]
	noses_count = len(noses)

	mouths = mouth_cascade.detectMultiScale(face)
	mouths = [item for item in mouths if item[2] > real_width/8 \
	                            and real_width/4 < (item[0]+item[2])/2 < real_width*3/4]
	mouths = sorted(mouths,key=lambda item:item[1])[-1:]
	mouths_count = len(mouths)

	eyes = eye_cascade.detectMultiScale(face)
	eyes = [item for item in eyes if item[1] > real_height/4 \
	                            and (2*item[1]+item[3])/2 < real_height*2/3]
	eyes = sorted(eyes,key=lambda item:item[1])[:2]
	eyes = sorted(eyes,key=lambda item:item[0])
	eyes_count = len(eyes)

	if len(eyes) != 0:
		for index,(ex,ey,ew,eh) in enumerate(eyes):
			# cv2.rectangle(face,(ex,ey),(ex+ew,ey+eh),(0,255,0),DARWEIGHT)
			if index == 0:
				linesArr.append(dict(x=0,y=round((ey-eh/5)/float(real_height),3)))
				linesArr.append(dict(x=0,y=round((ey+eh/10)/float(real_height),3)))

				# cv2.line(face,(0,ey-eh/5),(real_width,ey-eh/5),(255,0,0),DARWEIGHT)
				# cv2.line(face,(0,ey+eh/10),(real_width,ey+eh/10),(255,0,0),DARWEIGHT)
		else:
			linesArr.append(dict(x=0,y=round((ey+eh*3/4)/float(real_height),3)))
			linesArr.append(dict(x=0,y=round((ey+eh/4)/float(real_height),3)))
			linesArr.append(dict(x=round((ex+ew*3/4)/float(real_width),3),y=0))

			# cv2.line(face,(0,ey+eh/4),(real_width,ey+eh/4),(255,0,0),DARWEIGHT)
			# cv2.line(face,(0,ey+eh*3/4),(real_width,ey+eh*3/4),(255,0,0),DARWEIGHT)
			# cv2.line(face,(ex+ew*3/4,0),(ex+ew*3/4,real_height),(255,0,0),DARWEIGHT)

	if len(noses) != 0:
		for(nx,ny,nw,nh) in noses:
			linesArr.append(dict(x=round((nx+nw*1/3)/float(real_width),3),y=0))
			linesArr.append(dict(x=round((nx+nw*2/3)/float(real_width),3),y=0))
			linesArr.append(dict(x=round((nx+nw*3/4)/float(real_width),3),y=0))
			linesArr.append(dict(x=round((nx+nw)/float(real_width),3),y=0))

			linesArr.append(dict(x=0,y=round((ny+nh/4)/float(real_height),3)))
			linesArr.append(dict(x=0,y=round((ny+nh*3/4)/float(real_height),3)))
			# vertical
			# cv2.rectangle(face,(nx,ny),(nx+nw,ny+nh),(0,255,0),DARWEIGHT)
			# cv2.line(face,(nx+nw*1/3,0),(nx+nw*1/3,real_height),(255,0,0),DARWEIGHT)
			# cv2.line(face,(nx+nw*2/3,0),(nx+nw*2/3,real_height),(255,0,0),DARWEIGHT)
			# cv2.line(face,(nx+nw*3/4,0),(nx+nw*3/4,real_height),(255,0,0),DARWEIGHT)
			# cv2.line(face,(nx+nw,0),(nx+nw,real_height),(255,0,0),DARWEIGHT)
			# # horizental
			# cv2.line(face,(0,ny+nh*3/4),(real_width,ny+nh*3/4),(255,0,0),DARWEIGHT)
			# cv2.line(face,(0,ny+nh/4),(real_width,ny+nh/4),(255,0,0),DARWEIGHT)

	if len(mouths) != 0:
		for(mx,my,mw,mh) in mouths:
			# cv2.rectangle(face,(mx,my),(mx+mw,my+mh),(0,255,0),DARWEIGHT)
			pass
		else:
			linesArr.append(dict(x=0,y=round(my/float(real_height),3)))
			linesArr.append(dict(x=0,y=round((my+mh*3/5)/float(real_height),3)))

			# cv2.line(face,(0,my),(real_width,my),(255,0,0),DARWEIGHT)
			# cv2.line(face,(0,my+mh*3/5),(real_width,my+mh*3/5),(255,0,0),DARWEIGHT)

	return linesArr,dict(eyes_count=eyes_count, noses_count=noses_count, mouths_count=mouths_count)