from array import array
import math
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import time
from indexingTables import indexingContent
arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml","./XMLDOCS/D6.xml","./XMLDOCS/D7.xml" ]
N=len(arrayDocs)
app = Flask(__name__) 
CORS(app)
@app.route('/content', methods=[ 'POST', 'GET'])
def content():
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






#-------------------------------------------------------------------------------------
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


def contentProcess(root : ET.Element,arr):

    if(root.text != None):
        arr3=root.text.split()
        for i in range (len(arr3)):
            arr.append(arr3[i])
    for child in root:
        contentProcess(child,arr)
    return arr

def TF(arr, node): # arr hiye l big array w  arr1 hiye one node maa l context
    count=0
    for i in range(len(arr)):
        if(arr[i]== node):
            count+=1
    return count

def dict_TF(root):
    dictTF={}
    arr=contentProcess(root,[])
    for i in range (len(arr)): 
        dictTF[arr[i]]=TF(arr,arr[i])
    return dictTF

def DF(node,arr1):
    count=0
    for i in range (len(arr1)):
        longDF= contentProcess(arr1[i],[])
        if(TF(longDF,node) >=1):
            count+=1
    return count

def IDF(node):
    return abs(math.log(N/DF(node,getArrayRoots(arrayDocs)),10))

def dict_IDF(root):
    long2=contentProcess(root,[])

    dictIDF={}
    for i in range (len(long2)):
        dictIDF[long2[i]]=IDF(long2[i])
    return dictIDF

def dict_TF_IDF(root):
    long2=contentProcess(root,[])
    dictTF_IDF={}
    for i in range (len(long2)): 
        dictTF_IDF[long2[i]]=IDF(long2[i])*TF(long2,long2[i])
    return dictTF_IDF

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
def cosine_measure(dict3,dict4):
    numerator=0
    dict2=extend_dict(dict3,dict4)
    dict1=extend_dict(dict4,dict3)
    for key in dict1:
        numerator+=(float(dict1[key])*float(dict2.__getitem__(key)))
    den1=0 #stands for Asquare
    den2=0 #stands for Bsquare
    for key in dict1:
        den1+=(float(dict1[key])**2)
    for key in dict2:
        den2+=(float(dict2[key])**2)
    den3=den1*den2
    denominator=math.sqrt(den3)
    return numerator/denominator

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
        arrfinal[i]=contentProcess(roott,[])
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
        dict_index_structure[arr[i]]=[]
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
def doc_XML(str):
    str="./XMLDOCS/"+str+".xml"
    return str

def queryTree(root):
    arr=contentProcess(root,[])
    return arr

def queryString(str:str):
    arr=str.split()
    return arr
def searchIndexMain(arr: array, threshold):
    arrayDoc=[]
    dict=indexingContent
    arr1=[]
    for i in range (len(arr)):
        arr1=dict[arr[i]]
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
    sim=0
    for i in range(len(arrDoc)):
        if(mode=="TF"):
            dict2=dict_TF(getRoot(doc_XML(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDF(getRoot(doc_XML(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDF(getRoot(doc_XML(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_measure(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measure(dict1,dict2)
        if(measure=="pearson"):
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
    
def similarityRankingStr(str,threshold,treshold_similarity):
    arr1=queryString(str)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[arr1[i]]=1
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold)
    for i in range(len(arrDoc)):
        dict2=dict_TF(getRoot(doc_XML(arrDoc[i])))
        sim=cosine_measure(dict1,dict2)
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








if __name__ =='__main__':
    app.run(port=5600)