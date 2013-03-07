#/usr/bin/python

'''
Things you want to calculate:
    1. Mean connectivity:
        sum of connectivity of all voxels to one cortex
        divided by sum of connectivity of all voxels to all cortex
    2. Hard segmented subvolumes of thalamus:
'''

import pp
import os
import sys
import commands
import re
import glob
import pickle


class Data:
    '''
    for subject in subjects:
    subject=Data(subject)
    paYo.totalMC
    '''
    def __init__(self,folderName):
        self.subj=folderName


def main():
    #open a parallel server for faster processing
    parallel=pp.Server()

    #reading subject names for analysis from subjectList.txt
    with open('subjectList.txt','r') as subjectList:
    #cutting \n at the endsubjectList:
        subjects=[item.split('\n')[0] \
                for item in subjectList.readlines()]

    #add 'Mean connectivity calculation' jobs to jobList
    jobs = [(subject,parallel.submit(meanConnectivityCalculation,(subject,),(fslstats,getGroup,),("commands",))) for subject in subjects]

    for subject,job in jobs:
        print subject
        job()

   # for subject in 'NOR01_LSJ','NOR02_JIY':#subjects:
   #     print '\t\t\t***'+subject
   #     data=meanConnectivityCalculation(subject)

   #     #writing header to the log file
   #     #with open('../logs/meanConnectivity.txt','w') as text:
   #     #    text.write(''.join(data))

def getGroup(subject):
    if 'CHR' in subject:
        return 'CHR'
    else:
        return 'CON'


def meanConnectivityCalculation(subject):
    '''
    Over the threshold levels of
    10% ~ 90%,
    it calculates mean connectivity
    between thalamus and each cortex.
    '''
    subdirectory = 'segmentation/with_T1_freesurfer/segmentation'
    #list to return
    toReturn=[]

    #assign group
    group=getGroup(subject)

    #for left and right...
    for side,sside in [('left','lh'),('right','rh')]:


        imgSequence='LPFC','LTC','MPFC','MTC',\
                'OCC','OFC','PC','SMC'

        fullDirectory='../{group}/{subject}/{etc}/{side}'.format(
           group=group.lower(), subject=subject,
           etc=subdirectory,
           side=side)

        #for all thresholds and for all images
        for thr in range(10,90,10):
            print str(thr),
            toReturn.append(subject)
            toReturn.append(group)
            toReturn.append(side)
            toReturn.append(str(thr))
            eachTotalConnectivity=[]
            sumConnectivityForAll=0
            for layerNumber,img in zip(range(1,9),imgSequence):
                print '.',
                '''
                fslstats for each layer number from 1 to 8
                fslstats -V : output <voxels> <volume>
                (for nonzero voxels)
                '''
                num=str(layerNumber)


                #mean connectivity of the image
                img=fullDirectory+'/'+str(thr)+'thrP/'+\
                str(thr)+'_seeds_to_'+sside+'_'+img+'.nii.gz'
                #############
                #############
                meanInImage=fslstats(img,'-M')
                #volume of the image
                imageVolume=fslstats(img,'-V')
                #all connectivity values summed up
                totalConnectivity=meanInImage*imageVolume
                eachTotalConnectivity.append(totalConnectivity)
                sumConnectivityForAll+=totalConnectivity

            # Divide each total modality connection by
            # sum of connections
            toReturn.append('\t'.join([str(item/sumConnectivityForAll)\
                    for item in eachTotalConnectivity]))

            # Reset for loop
            sumConnectivityForAll=0
            eachTotalConnectivity=[]

    with open('../logs/meanConnectivity.txt','a') as text:
        text.write('\t'.join(data))
        text.write('\n')

def fslstats(inputs,option):
    output=commands.getoutput(
    'fslstats {inputs} {option}'.format(
                inputs=inputs,
                option=option))
    if option=='-V':
        return float(output.split(' ')[0])
    elif option=='-M':
        return float(output)

if __name__=='__main__':
    main()
