import sys
from Message import * 

class LadderQueue:
    
    def __init__(self):
        pass 

	MaxTS=0
	MinTS=999999
	x=0
	k=0
	NTop=0
	TopStart=0
	Bucketwidth=[]
	NBc=0
	NBucket=[]
	bucket_k=0
	NRung=0
	RCur=[]
	RStart=[]
	THRES=50
	NBot=0
	Top=[]
	Bottom=[]

	def enqueue(message):
		if TS>=TopStart:
			# insert into tail of Top
			Top.insert(len(Top),message)
			NTop+=1
			if message.timestamp>MaxTS:
				MaxTS=message.timestamp
			if message.timestamp<MinTS:
				MinTS=message.timestamp
			return
		while (TS<RCur[x] and x <= NRung):
			x+=1
			if x<=NRung:
				bucket_k=(TS - Rstart[x])/Bucketwidth[x] # - or --?
				# insert into tail of rung x, bucket_k
				NBucket[x, bucket_k]+=1
				return
			elif NBot>THRES:
				create_new_rung(NBot)
				# transfer Bottom to it
				bucket_k=(TS-RStart[NRung])/Bucketwidth(NRung) # - or --?
				# insert into tail of rung NRung, bucket_k
				NBucket[NRung, bucket_k]+=1
			else:
				# insert into Bottom using sequential search
				i=0
				while i<len(Bottom):
					if message.timestamp<Bottom(i):
						Bottom.insert(i,message)
						break
					i+=1
				Nbot+=1


	def dequeue():
		if len(Bottom)!=0:
			# return next message from Bottom
			Bottom.pop(0)
			return
		if NRung>0:
			bucket_k=recurse_rung()
			# if last bucket then NRung- #not sure what the - means?
			# sort from bucket_k to Bottom
			# return first message from Bottom
			Bottom.pop(0)
		else:
			Bucketwidth[1]=(MaxTS-MinTS)/NTop
			Bucketwidth[0]=Bucketwidth[1]
			TopStart=MaxTS+Bucketwidth[1] #p 179 disagrees with pseudo code, check
			RCur[1]=MinTS
			RStart[1]=MinTS
			# transfer Top to rung 1 of Ladder
			bucket_k=floor((TS-RStart[1])/Bucketwidth[1])

			bucket_k=recurse_rung()
			# sort messages from bucket_k and copy to Bottom
			# return first message from Bottom
			return Bottom.pop(0)


	def recurseRung():
		# Point A
		while (NBucket[NRung, k]==0):
			k+=1
			RCur[NRung]+=Bucketwidth[NRung]
		if NBucket[NRung, k]>THRES:
			createNewRung(NBucket[NRung,k])
			# recopy messages from bucket to new rung
			# goto Point A
		return k


	def createNewRung():
		NRung+=1
		Bucketwidth[NRung]=Bucketwidth[NRung-1]/THRES
		RCur[NRung]=RCur[NRung-1] 
		RStart[NRung]=RCur[NRung-1]
		#11RCur[NRung-1]+=Bucketwidth[NRung-1]
    