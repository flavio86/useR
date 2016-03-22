'''
Created on 4/03/2016
Script to compute shape features

Area and perimeter of nucleus, nucleus/cytoplasm ratio, distance between the centroid of nucleus 
and cytoplasm, minimum and maximum distance between the centroid of nucleus and its edge, 
difference between the diameter of the minimum enclosing circle of nucleus and the diameter of the 
circle with the same area of nucleus

@author: Flavio Araujo
'''

import numpy as np
import cv2 as cv
from scipy import ndimage
import os
from skimage import measure

'''
Input: binary image 
Output: binary image with only the largest region of im
'''
def removeRegion(im):
    labels, number = ndimage.measurements.label(im)
    if number == 1:
        labels = labels * 255
        labels = cv.convertScaleAbs(labels)
        return labels
    
    aux = np.zeros((number+1),dtype = float)
    for i in range(labels.shape[0]):
        for j in range(labels.shape[1]):
            if (labels[i,j] != 0):
                aux[labels[i,j]] = aux[labels[i,j]] + 1
    
    mx = np.max(aux)
    for i in range(number+1):
        if (aux[i] == mx):
            labelMaxRegion = i
            break
    
    for i in range(labels.shape[0]):
        for j in range(labels.shape[1]):
            if (labels[i,j] != labelMaxRegion):
                labels[i,j] = 0
            else:
                labels[i,j] = 255;
    
    labels = cv.convertScaleAbs(labels)
    _, labels = cv.threshold(labels,127,255,0)
    
    return labels

''' 
Input: binary image
Output: area of the regions within im
'''
def area(im): 
    return (np.sum(im)/255)
    
'''
Input: binary image
Output: a scalar that specifies the diameter of a circle with the same area as the region
'''
def equivalentDiameter(im):
    im = im/255
    props = measure.regionprops(im)
    return props[0]['equivalent_diameter']

'''
Input: binary image
Output: a scalar that specifies the diameter of a minimum enclosing circle which completely covers the object with minimum area
'''
def minEnclosingCircle(im):
    canny = im * 255
    canny = cv.Canny(canny,100,200)
    canny = canny/255
    quant = np.sum(canny)
    
    cont = 0
    coords = np.zeros((quant,2))
    for i in range(canny.shape[0]):
        for j in range(canny.shape[1]):
            if canny[i,j] != 0:
                coords[cont,0] = i
                coords[cont,1] = j
                cont = cont + 1
            
    maxi = 0
    for i in range(coords.shape[0]):
        for j in range(coords.shape[0]):
            dist = ((coords[i,0] - coords[j,0])**2 + (coords[i,1] - coords[j,1])**2)**0.5
            if dist > maxi:
                maxi = dist     
    return maxi
    
'''
Input: binary image
Output: array containing Min and Max distance between the centroid of region and its edge
'''
def MinMaxDistanciaCentroidEdge(im, centroid):    
    canny = im * 255
    canny = cv.Canny(canny,100,200)
    canny = canny/255
    
    listAux = np.zeros((np.sum(canny),2))
    cont = 0
    for i in range(im.shape[0]):
        for j in range(im.shape[1]):
            if canny[i,j] > 0:
                listAux[cont,0] = i
                listAux[cont,1] = j
                cont = cont + 1
    
    dist = np.zeros((2))
    dist[0] = 10000
    dist[1] = -1
    for i in range(listAux.shape[0]):
        auxD = ( (centroid[0]-listAux[i,0])**2 + (centroid[1]-listAux[i,1])**2)**(0.5)
        if auxD < dist[0]:
            dist[0] = auxD
        if auxD > dist[1]:
            dist[1] = auxD 
    
    return dist
    
'''
Input
maskNucl: binary image containing nucleus mask 
maskCyto: binary image containing cytoplasm mask
numberFeatures: number of features
Output: array containing the features 
'''
def calculateFeatures(maskNucl,maskCyto,numberFeatures):
    features = np.zeros(numberFeatures)
    
    aNucl = area(maskNucl)
    aCyto = area(maskCyto)
    
    maskNucl = removeRegion(maskNucl)
    maskCyto = removeRegion(maskCyto)
    
    maskNucl = maskNucl/255
    maskCyto = maskCyto/255
    
    propsNucl = measure.regionprops(maskNucl)
    propsCyto = measure.regionprops(maskCyto)
    
    centroidNucl = propsNucl[0]['centroid']
    centroidCyto = propsCyto[0]['centroid']

    perim = propsNucl[0]['perimeter']
    
    equivalentDiam = propsNucl[0]['equivalent_diameter']
    
    distCentroid = ((centroidNucl[0]-centroidCyto[0])**2 + (centroidNucl[1]-centroidCyto[1])**2)**(0.5)
        
    MinMaxDist = MinMaxDistanciaCentroidEdge(maskNucl, centroidNucl)
            
    minEnclosingCir = minEnclosingCircle(maskNucl)

    features[0] = float(aNucl)/float(aCyto)
    features[1] = distCentroid 
    features[2] = aNucl
    features[3] = MinMaxDist[0]
    features[4] = MinMaxDist[1]
    features[5] = perim
    features[6] = minEnclosingCir - equivalentDiam
    
    return features

################################### Main ###############################################################
print 'Shape features'

path_read = " "
path_write = " " 

folders = ['carcinoma_in_situ', 'light_dysplastic', 'moderate_dysplastic', 'normal_columnar', 'normal_intermediate', 'normal_superficiel', 'severe_dysplastic']
label = [0,0,0,1,1,1,0]
mask_nucl = 'masc_nuc'
mask_cyto = 'masc_junc'
number_of_features = 7
databaseSize = 917
feature_vector = np.zeros((917,number_of_features+1))

labelCont = 0
cont = 0
for x in folders:
    arquivos_maskCyto = os.listdir(path_read+x+'_masc//'+mask_cyto)
    arquivos_maskNucl = os.listdir(path_read+x+'_masc//'+mask_nucl)
    contMask = 0
    print x
    for y in arquivos_maskCyto:
        if (y[-3:] == 'bmp') | (y[-3:] == 'BMP'):
            
            maskCyto = cv.imread(path_read+x+'_masc//'+mask_cyto+'//'+arquivos_maskCyto[contMask])
            maskCyto = cv.cvtColor(maskCyto,cv.COLOR_BGR2GRAY)
            
            maskNucl = cv.imread(path_read+x+'_masc//'+mask_nucl+'//'+arquivos_maskNucl[contMask])
            maskNucl = maskNucl[:,:,0]
            
            shapeFeatures = calculateFeatures(maskNucl,maskCyto,number_of_features)
            
            feature_vector[cont,0:number_of_features] = shapeFeatures
            feature_vector[cont,number_of_features] = label[labelCont]
            cont=cont+1
            contMask = contMask+1
    labelCont = labelCont+1
np.savetxt(path_write + "shape_features.csv",feature_vector, delimiter=",")