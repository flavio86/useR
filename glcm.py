'''
Created on 4 de mar de 2016
Compute the GLCM features with or without mask
@author: romue
'''
import numpy as np
from skimage.feature import greycomatrix,greycoprops
import cv2
import glob
import os
from blaze.expr.core import path
from cv2 import threshold
from skimage.exposure import exposure

np.set_printoptions(threshold='nan')

def glcm(imagem,mask,grayLevels,d):
    imagem = cv2.equalizeHist(imagem)
    imagem = categorizar(imagem,8)
    imagem = cv2.bitwise_and(imagem,mask)
    matrix0 = greycomatrix(imagem, [d], [0], levels=grayLevels)
    matrix1 = greycomatrix(imagem, [d], [np.pi/4], levels=grayLevels)
    matrix2 = greycomatrix(imagem, [d], [np.pi/2], levels=grayLevels)
    matrix3 = greycomatrix(imagem, [d], [3*np.pi/4], levels=grayLevels)
    matrix = (matrix0+matrix1+matrix2+matrix3)/4 #isotropic glcm
    if mask != []:
        matrix[0,0,0,0] = 0 #remove 0->0 (mask)
    props = np.zeros((5))
    props[0] = greycoprops(matrix,'contrast')
    props[1] = greycoprops(matrix,'dissimilarity')
    props[2] = greycoprops(matrix,'homogeneity')
    props[3] = greycoprops(matrix,'energy')
    props[4] = greycoprops(matrix,'ASM')
    return props

#function to change the number of gray scale values 
def categorizar(imagem,nbits=8):
    L,C = imagem.shape;
    limites = np.arange(0,256,256/nbits)
    for z in range(0,len(limites)-1):
        aux = ((imagem >= limites[z]) & (imagem < limites[z+1]))
        imagem[aux==True] = z
    aux = (imagem >= limites[nbits-1])
    imagem[aux==True] = nbits-1
    return imagem

print 'GLCM'

path_read = " "
path_write = " " 

folders = ['carcinoma_in_situ', 'light_dysplastic', 'moderate_dysplastic', 'normal_columnar', 'normal_intermediate', 'normal_superficiel', 'severe_dysplastic']
label = [0,0,0,1,1,1,0]
mask_type = 'masc_nuc'# {masc_nuc, masc_cyto, masc_junc}
number_of_features = 5
databaseSize = 917
feature_vector = np.zeros((917,number_of_features+1))
grayLevel = 64
labelCont = 0
cont = 0
D = range(1,12,2) #distance of GLCM 1..11
for d in D:
    print d
    for x in folders:
        arquivos_img = os.listdir(path_read+x)
        arquivos_mask = os.listdir(path_read+x+'_masc//'+mask_type)
        contMask = 0
        for y in arquivos_img:
            if (y[-3:] == 'bmp') | (y[-3:] == 'BMP'):
                #read and preprocessing original image
                img = cv2.imread(path_read+x+'//'+y)
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  
                
                #read and preprocessing mask image    
                mask = cv2.imread(path_read+x+'_masc//'+mask_type+'//'+arquivos_mask[contMask])
                mask = mask[:,:,0]
                
                grey = glcm(img,mask,grayLevel,d)
                feature_vector[cont,0:number_of_features] = grey
                feature_vector[cont,number_of_features] = label[labelCont]
                cont=cont+1
                contMask = contMask+1
        labelCont = labelCont+1
    labelCont = 0
    cont = 0
    file = path_write + "glcm_isotropic_grays_"+str(grayLevel)+'_dist_'+str(d)+'_nuc.csv'
    np.savetxt(file,feature_vector, delimiter=",")