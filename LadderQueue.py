import sys

class LadderQueue:
    
    def __init__(self):
        pass

    def enqueue():
	if TS>=TopStart:
		# insert into tail of Top
		NTop+=1
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
			Nbot+=1


	def dequeue():
		if 1==1: # replace with Bottom not empty
			# return next event from Bottom
		    pass
		if NRung>0:
			bucket_k=recurse_rung()
			# if last bucket then NRung- #not sure what the - means?
			# sort from bucket_k to Bottom
			# return first event from Bottom
		else:
			Bucketwidth[1]=(MaxTS-MinTS)/NTop # - or --?
			TopStart=MaxTS
			RCur[1]=MinTS # check swap order a
			Rstart[1]=RCur[1] # check swap order b
			# transfer Top to rung 1 of Ladder
			bucket_k=recurse_rung()
			# sort events from bucket_k and copy to Bottom
			# return first event from Bottom


	def recurseRung():
		# Point A
		while (NBucket[NRung, k]==0):
			k+=1
			RCur[NRung]+=Bucketwidth[NRung]
		if NBucket[NRung, k]>THRES:
			create_new_rung(NBucket[NRung,k])
			# recopy events from bucket to new rung
			# goto Point A
		return k


	def createNewRung():
		NRung+=1
		Bucketwidth[NRung]=Bucketwidth[NRung-1]/NEvent
		RCur[NRung]=RCur[NRung-1] # check swap order c
		RStart[NRung]=RCur[NRung] # check swap order d
    