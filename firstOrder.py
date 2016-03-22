'''
Created on 14/03/2016

@author: romuere

Script to compute 1a order texture features
Entropy, energy, mean, variance, skewness, kurtosis, roughness
'''

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpy import reshape
from scipy.stats.mstats_basic import skew, kurtosis
from skimage.exposure import exposure
np.set_printoptions(threshold='nan')
import copy
from sklearn import preprocessing


def firstOrder(imagem, mask):
    imagem =exposure.equalize_hist(imagem)
    texture = np.zeros((14))
    mask = mask > 0
    im_mask = imagem[mask]
    t = im_mask.shape[0]
    hist,bin = np.histogram(im_mask,density=False,bins = 256) #compute the histogram
    hist = np.float16(hist)
    hist = hist/t
    hist_temp = copy.copy(hist)
    hist_temp[hist_temp==0] = 1
    
    ##Histogram Attributes
    #Entropy
    Entropy = -1*np.sum(hist_temp*np.log2(hist_temp))

    #Energy
    Energy = np.sum((hist/t)**2)
    
    #Mean
    Mean = np.mean(hist)
    
    #Variance
    Variance = np.var(hist)
    
    #Skewness
    Skewness = skew(hist)
    Skewness = Skewness.tolist()
    
    #Kurtosis
    Kurtosis = kurtosis(hist)
    Kurtosis = Kurtosis.tolist() 
    
    #Roughness
    R = 1 - (1/(1+Variance))
    
############################################################################################    
    ##Image Attributes
    #Entropy
    Entropy_im = -1*np.sum(im_mask*np.log2(im_mask))

    #Energy
    Energy_im = np.sum((im_mask/t)**2)
    
    #Mean
    Mean_im = np.mean(im_mask)
    
    #Variance
    Variance_im = np.var(im_mask)
    
    #Skewness
    Skewness_im = skew(im_mask)
    Skewness_im = Skewness_im.tolist()
    
    #Kurtosis
    Kurtosis_im = kurtosis(im_mask)
    Kurtosis_im = Kurtosis_im.tolist() 
    
    #Roughness
    R_im = 1 - (1/(1+Variance_im))
    
    texture = [Entropy, Energy, Mean, Variance, Skewness, Kurtosis, R, Entropy_im, Energy_im, Mean_im, Variance_im, Skewness_im, Kurtosis_im, R_im]
    return texture

#normalize values between 0-1
def posProcessing (data):
    min_max_scaler = preprocessing.MinMaxScaler()
    normalized = min_max_scaler.fit_transform(data)
    return normalized

print 'First Order Texture Descriptors'

path_read = " "
path_write = " " 

folders = ['carcinoma_in_situ', 'light_dysplastic', 'moderate_dysplastic', 'normal_columnar', 'normal_intermediate', 'normal_superficiel', 'severe_dysplastic']
label = [0,0,0,1,1,1,0]
mask_type = 'masc_junc'# {masc_nuc, masc_cyto, masc_junc}
number_of_features = 14
databaseSize = 917
feature_vector = np.zeros((917,number_of_features+1))
labelCont = 0
cont = 0
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
            texture = firstOrder(img, mask)
            feature_vector[cont,0:number_of_features] = texture
            feature_vector[cont,number_of_features] = label[labelCont]
            cont=cont+1
            contMask = contMask+1
    labelCont = labelCont+1
np.savetxt(path_write + "firstOrder_texture.csv",feature_vector, delimiter=",")