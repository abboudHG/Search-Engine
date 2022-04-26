from array import ArrayType
from ast import Str
from ctypes import Array
from importlib.metadata import Distribution
import math
from posixpath import split
from tokenize import String
from numpy import array
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import time
import xml.etree.ElementTree as ET
from indexingTables import indexingContentStructure
app = Flask(__name__) 
CORS(app)


tree=ET.parse("./XMLDOCS/D1.xml")
root=tree.getroot()

arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml","./XMLDOCS/D6.xml","./XMLDOCS/D7.xml" ]
N=len(arrayDocs)

@app.route('/contentStructure', methods=['POST', 'GET'])
def contentStructure():
    t1=time.time()
    t2=time.time()
    arr=[]
    mode2=request.json['mode']
    query=request.json[ 'query']
    if(mode2=="xml"):
        root=ET.fromstring(query)
        arr=similarityRankingTree(root,0.01,0.01,"TF-IDF","cosine")
        t2=time.time()
    if(mode2=="keywords"):
        arr=similarityRankingStr(query,0.001,0.001)
        t2=time.time()
    return {'arrDoc': arr, 'time': t2-t1, 'results': len(arr)}














#---------------------------------------------------
def getRoot(doc):
    tree=ET.parse(doc)
    return tree.getroot()

def getArrayRoots(arr1):
    arr=[]
    for i in range(len(arr1)):
        tree=ET.parse(arr1[i])
        root=tree.getroot()
        arr.append(root)
    return arr
def contextStructure(arr: ArrayType,sequence,root : ET.Element):
    arr1 = [root.tag,sequence] 
    arr.append(arr1)
    sequence = sequence.__add__(root.tag + "/")
    arr2=[]
    if(root.text != None):
        arr3=root.text.split()
        for i in range (len(arr3)):
            arr2 = [arr3[i],sequence]
            arr.append(arr2)
    for child in root:
        contextStructure(arr,sequence,child)
    return arr


def preprocess(arr):
    count = len(arr)
    i = 0
    while(i < count):
        arr[i][1] = arr[i][1][:len(arr[i][1]) -1 ]
        i = i+1
    return arr
def pre(root:ET.Element):
    arr = []
    sequence = ""
    count = 0
    return  preprocess(contextStructure(arr,sequence,root))

def TF(arr, arr1): # arr hiye l big array w  arr1 hiye one node maa l context
    count=0
    for i in range(len(arr)):
        if(arr[i]== arr1):
            count+=1
    return count

def dict_TF(root):
    dictTF={}
    arr=pre(root)
    for i in range (len(arr)): 
        dictTF[arr[i][0] + ","+ arr[i][1]]=TF(arr,arr[i])
    return dictTF

def DF(nodeArr,arr1): # all docs we have is arr1
    count=0
    for i in range (len(arr1)):
        longDF= pre(arr1[i])
        if(TF(longDF,nodeArr) >=1):
            count+=1
    return count


def IDF(nodeArr):
    return abs(math.log(N/DF(nodeArr,getArrayRoots(arrayDocs)),10))

def dict_IDF(root):
    arr=pre(root)
    dictIDF={}
    for i in range (len(arr)):
        dictIDF[arr[i][0] + ","+ arr[i][1]]=IDF(arr[i])
    return dictIDF

def dict_TF_IDF(root):
    arr=pre(root)
    dictTF_IDF={}
    for i in range (len(arr)): 
        dictTF_IDF[arr[i][0] + ","+ arr[i][1]]=IDF(arr[i])*TF(arr,arr[i])
    return dictTF_IDF

def costUpdate(str1,str2):
    if(str1==str2):
        return 0
    else: return 1

def costED(str1 :str, str2 : str):
    arr1= str1.split('/')
    arr2=str2.split('/')
   
    len1 = len(arr1)
    len2 = len(arr2)
    dist=[[0 for x in range (len2+1)] for y in range (len1+1)]
    dist[0][0]=0
    for i in range (1,len1+1):
        dist[i][0] = dist[i-1][0]+1
    for j in range (1,len2+1):
        dist[0][j] = dist[0][j-1]+1
    
    for i in range (1,len1+1):
        for j in range (1,len2+1):
            a=dist[i-1][j-1]+costUpdate(arr1[i-1], arr2[j-1])
            b=dist[i-1][j]+1
            c=dist[i][j-1]+1
            dist[i][j]= min(a,b,c)
            
    return 1/(1+float(dist[len1-1][len2-1]))

def extend_dict(dict1,dict2):
    arr1=[]
    dict11={}   
    for key in dict1:
        if key not in dict2.keys():
            arr1.append(key)
    for i in range (len(arr1)): 
        dict11[arr1[i]]=0
    dict2.update(dict11)
    return dict2

def cosine_sim(dict3,dict4):
    num=0
    dict1=extend_dict(dict4,dict3)
    dict2=extend_dict(dict3,dict4)
    for key in dict1:
        arr=key.split(',')
        term=arr[0]
        context=arr[1]
       
        for key1 in dict2:
            arr1=key1.split(',')
            term1=arr1[0]
            context1=arr1[1]
            
            if(term1==term):
         

                num+= float(dict1[key])*float(dict2[key1])*costED(context,context1)
                
    
    den1=0 #stands for Asquare
    den2=0 #stands for Bsquare
    for key in dict1:
        den1+=(float(dict1[key])**2)
    for key in dict2:
        den2+=(float(dict2[key])**2)
    den3=den1*den2
    denominator=math.sqrt(den3)
    return num/denominator

def euclidian_measure(dict3,dict4):
    dict2=extend_dict(dict3,dict4)
    dict1=extend_dict(dict4,dict3)
    numerator=1
    den1=0
    for key in dict1:
        den1+=(float(dict1[key])-float(dict2.__getitem__(key)))**2
    den2=math.sqrt(den1)
    denominator=1+den2
    return numerator/denominator


def AllPath_AllDocuments(arr):
    #arr=[]
    arrfinal = [0 for i in range(len(arr))]
    for i in range (len(arr)):
        roott=getArrayRoots(arr)[i]
        arrfinal[i]=pre(roott)
    return arrfinal

def AllPath_AllDocuments_unique(arr):
    arr_unique=[]
    for i in range (len(arr)):
        for j in range(len(arr[i])):
            if(not arr_unique.__contains__(arr[i][j])):
                arr_unique.append(arr[i][j])
    return arr_unique

def dict_docs_roots(arrayDocs):
    dict_D_docs={}
    for i in range(len(arrayDocs)):
        dict_D_docs[str("D")+str(i+1)]=getArrayRoots(arrayDocs)[i]
    return dict_D_docs

def index_structure(arr):  #nte5oud aprintrray_unique
    dict_index_structure={}
    dict_all_doc={}
    dict1=dict_docs_roots(arrayDocs) #[D1:root doc1, D2:root D2....]
    for i in range (len(dict1)):
        dict_all_doc[str("D")+str(i+1)]=dict_TF_IDF(dict1.get(str("D")+str(i+1)))
    #halla2 sar aana key:D1, value a dictionary tabaa kl element maa l weight
    for i in range (len(arr)):
        dict_index_structure[str(arr[i][0])+","+str(arr[i][1])]=[]
    arraykeys=[]
    for k in dict_index_structure:
        arraykeys.append(k)
    for i in range(len(dict_index_structure)):
        arrfinal=[]
        for j in range(len(dict_all_doc)):
            arrayDocj=[]
            arrayDocj.append(str("D")+str(j+1))
            if(dict_all_doc[str("D")+str(j+1)].__contains__(arraykeys[i])):
                arrayDocj.append(dict_all_doc[str("D")+str(j+1)][arraykeys[i]])
                arrfinal.append(arrayDocj)
        dict_index_structure[arraykeys[i]]=arrfinal
    return dict_index_structure

def doc_XML(str1):
    str1="./XMLDOCS/"+str1+".xml"
    return str1

def queryTree(root):
    arr=pre(root)
    return arr

def queryString(str:str):
    arr1=str.split()
    arr=[]
    arrAll=AllPath_AllDocuments_unique(AllPath_AllDocuments(arrayDocs))
    arr2=[]
    for i in range (len(arr1)):
        for j in range (len(arrAll)):
            if(arr1[i]==arrAll[j][0]):
                arr2.append(arr1[i])
                arr2.append(arrAll[j][1])
                arr.append(arr2)
                arr2=[]
    return arr

def searchIndexMain(arr: array, threshold):
    arrayDoc=[]
    dict=indexingContentStructure
    arr1=[]
    for i in range (len(arr)):
        arr1=dict[str(arr[i][0])+","+str(arr[i][1])]
        for j in range (len(arr1)):
            if(arr1[j][1]>= threshold):
                if(not arrayDoc.__contains__(arr1[j][0])):
                    arrayDoc.append(arr1[j][0])
    return arrayDoc

def similarityRankingTree(root,threshold_index,treshold_similarity, mode, measure):
    arrDocsSort=[]
    dictSort={}
    arr_values=[]
    arr1=queryTree(root)
    dict1={}
    dict2={}
    if(mode=="TF"):
        dict1=dict_TF(root)
    if(mode=="IDF"):
        dict1=dict_IDF(root)
    if(mode=="TF-IDF"):
        dict1=dict_TF_IDF(root)
   
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold_index)
    for i in range(len(arrDoc)):
        if(mode=="TF"):
            dict2=dict_TF(getRoot(doc_XML(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDF(getRoot(doc_XML(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDF(getRoot(doc_XML(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_sim(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measure(dict1,dict2)
        dictSort[arrDoc[i]]=sim
    for key in dictSort:
        arr_values.append(dictSort[key])
    arr_values.sort()
    arr_values_sort=arr_values
    arr_values_sort=arr_values_sort[::-1]
    for i in range (len(arr_values_sort)):
        for key in dictSort:
            if(dictSort[key]==arr_values_sort[i] and dictSort[key]>=treshold_similarity):
                arrDocsSort.append(key)
                dictSort[key]= 2
    return arrDocsSort

def similarityRankingStr(str1,threshold,treshold_similarity):
    arr1=queryString(str1)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[str(arr1[i][0])+","+str(arr1[i][1])]=1
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold)
    for i in range(len(arrDoc)):
        dict2=dict_TF_IDF(getRoot(doc_XML(arrDoc[i])))
        sim=cosine_sim(dict1,dict2)
        dictSort[arrDoc[i]]=sim
    for key in dictSort:
        arr_values.append(dictSort[key])
    arr_values.sort()
    arr_values_sort=arr_values
    arr_values_sort=arr_values_sort[::-1]
    for i in range (len(arr_values_sort)):
        for key in dictSort:
            if(dictSort[key]==arr_values_sort[i] and dictSort[key]>=treshold_similarity):
                arrDocsSort.append(key)
                dictSort[key]= 2
    return arrDocsSort



print(queryString("Department"))
print(similarityRankingStr("maria abboud chloe a b", 0.001,0.001))


if __name__ =='__main__':
    app.run(port=5700)