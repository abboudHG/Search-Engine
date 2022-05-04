from ast import Dict, Str
import json
from tokenize import String
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import xml.etree.ElementTree as ET
import math
import time
from numpy import array, number
from indexingTables import indexingStructure

app = Flask(__name__) 
CORS(app)
source=0
destination=0
arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml","./XMLDOCS/D6.xml","./XMLDOCS/D7.xml" , "./XMLDOCS/D8.xml", "./XMLDOCS/D9.xml","./XMLDOCS/D10.xml","./XMLDOCS/D11.xml", "./XMLDOCS/D12.xml","./XMLDOCS/D13.xml","./XMLDOCS/D14.xml","./XMLDOCS/D15.xml","./XMLDOCS/D16.xml","./XMLDOCS/D17.xml","./XMLDOCS/D18.xml","./XMLDOCS/D19.xml","./XMLDOCS/D20.xml"]
N=len(arrayDocs)
@app.route("/VSM",methods=['POST'])
def computeVSM():
    doc1=0
    doc2=0
    t0 = time.time()
    source=request.json['source']
    destination=request.json['destination']
    t1=0
     #source
    if source=="Document 1":
       doc1=arrayDocs[0]
    elif source== "Document 2":
        doc1=arrayDocs[1]
    elif source== "Document 3":
        doc1=arrayDocs[2]
    elif source== "Document 4":
        doc1=arrayDocs[3]
    elif source== "Document 5":
        doc1= arrayDocs[4]
    elif source== "Document 6":
        doc1= arrayDocs[5]
    elif source== "Document 7":
        doc1= arrayDocs[6]
    elif source== "Document 8":
        doc1= arrayDocs[7]
    elif source== "Document 9":
        doc1= arrayDocs[8]
    elif source== "Document 10":
        doc1= arrayDocs[9]
    elif source== "Document 11":
        doc1= arrayDocs[10]
    elif source== "Document 12":
        doc1= arrayDocs[11]
    elif source== "Document 13":
        doc1= arrayDocs[12]
    elif source== "Document 14":
        doc1= arrayDocs[13]
    elif source== "Document 15":
        doc1= arrayDocs[14]
    elif source== "Document 16":
        doc1= arrayDocs[15]
    elif source== "Document 17":
        doc1= arrayDocs[16]
    elif source== "Document 18":
        doc1= arrayDocs[17]
    elif source== "Document 19":
        doc1= arrayDocs[18]
    elif source== "Document 20":
        doc1= arrayDocs[19]
    
    #destination
    if destination=="Document 1":
        doc2=arrayDocs[0]
    elif destination== "Document 2":
        doc2=arrayDocs[1]
    elif destination== "Document 3":
        doc2=arrayDocs[2]
    elif destination== "Document 4":
        doc2=arrayDocs[3]
    elif destination== "Document 5":
        doc2= arrayDocs[4]
    elif destination== "Document 6":
       doc2= arrayDocs[5]
    elif destination== "Document 7":
        doc2= arrayDocs[6]
    elif destination== "Document 8":
        doc2= arrayDocs[7]
    elif destination== "Document 9":
        doc2= arrayDocs[8]
    elif destination== "Document 10":
        doc2= arrayDocs[9]
    elif destination== "Document 11":
        doc2= arrayDocs[10]
    elif destination== "Document 12":
        doc2= arrayDocs[11]
    elif destination== "Document 13":
        doc2= arrayDocs[12]
    elif destination== "Document 14":
       doc2= arrayDocs[13]
    elif destination== "Document 15":
        doc2= arrayDocs[14]
    elif destination== "Document 16":
        doc2= arrayDocs[15]
    elif destination== "Document 17":
        doc2= arrayDocs[16]
    elif destination== "Document 18":
        doc2= arrayDocs[17]
    elif destination== "Document 19":
        doc2= arrayDocs[18]
    elif destination== "Document 20":
       doc2= arrayDocs[19]

    root1=getRoot(doc1)
    root2=getRoot(doc2)
   
    mode=request.json['mode'] #TF..
    measure=request.json['measure'] #cosine
    sim=0
    if(mode=="TF"):
        
        dict1=dict_TF(root1)
        dict2=dict_TF(root2)
        
        dict3=extend_dict(dict2,dict1)
        
        dict4=extend_dict(dict1,dict2)
        dict1=dict3
        dict2=dict4
        if(measure=="cosine"):
            sim=cosine_measure(dict1,dict2)
            t1 = time.time()
        if(measure=="euclidian"):
            sim=euclidian_measure(dict1,dict2)
            t1 = time.time()
        
      
    if(mode=="IDF"):
        dict1=dict_IDF(root1)
        dict2=dict_IDF(root2)
        
        
        dict1=extend_dict(dict2,dict1)
        
        dict2=extend_dict(dict1,dict2)
        if(measure=="cosine"):
            sim=cosine_measure(dict1,dict2)
            t1 = time.time()
        if(measure=="euclidian"):
            sim=euclidian_measure(dict1,dict2)
            t1 = time.time()
      

    if(mode=="TF-IDF"):
        dict1=dict_TF_IDF(root1)
        dict2=dict_TF_IDF(root2)
       
       
        dict1=extend_dict(dict2,dict1)
        
        dict2=extend_dict(dict1,dict2)
        if(measure=="cosine"):
            sim=cosine_measure(dict1,dict2)
            t1 = time.time()
        if(measure=="euclidian"):
            sim=euclidian_measure(dict1,dict2)
            t1 = time.time()
        
   
    
    return {'VSM':sim,'timeVSM':t1-t0}

@app.route('/getAllPaths', methods=[ 'POST', 'GET'])
def getAllPaths():
    arr=AllPath_AllDocuments_unique(AllPath_AllDocuments(arrayDocs))

    return { 'allpaths': arr}

@app.route('/indexingTableStructure',  methods=[ 'POST', 'GET'])
def structure():
    arr=AllPath_AllDocuments_unique(AllPath_AllDocuments(arrayDocs))

    return index_structure(arr)

@app.route('/searchXMLPaths', methods=[ 'POST', 'GET'])
def searchXML():
    t2=time.time()
    mode="TF-IDF" #TF..
    measure="cosine" #cosine
    mode2=request.json['mode']
    query=request.json['query'] 
    k=request.json['k']
    arr=[]
    t3=time.time()
    if(mode2=="xml"):
        root=ET.fromstring(query)
        arr=similarityRankingTree(root,0.01,0.01,mode,measure,int(k))
        t3=time.time()
    if (mode2=="paths"):
        arr=similarityRankingStr(query,0.001,0.001,int(k))
        t3=time.time()
    print(arr)
    return { 'arrDoc': arr, 'time': t3-t2, 'results': len(arr)}


#------------------------------------------------------------------
def getArrayRoots(arr1):
    arr=[]
    for i in range(len(arr1)):
        tree=ET.parse(arr1[i])
        root=tree.getroot()
        arr.append(root)
    return arr
def getRoot(doc):
    tree=ET.parse(doc)
    return tree.getroot()

def countChild(root):
    count=0
    for child in root:
        count=count+1
    return count
def preorder(root):
    if root is None:
        return []
    ans= [root.tag.lower()]
    for x in root:
        ans += preorder(x)
    return ans
def preprocessArr(root: ET.Element,sequence : str , arr,count ):
    count = count +1
    seq = sequence
    seq = seq.__add__(root.tag.lower() + "/")
    arr.append(seq)
    # if(countChild(root)==0):
    #  arr.append(seq)
    for child in root:
        seq2 = ""
        if(count ==1):
            preprocessArr(child,seq2,arr,count)
        preprocessArr(child,seq,arr,count)   
    return arr
def preprocess(arr):
    count = len(arr)
    i = 0
    while(i < count):
        arr[i] = arr[i][:len(arr[i]) -1 ]
        i = i+1
    return arr
def pre(root:ET.Element):
    arr = []
    sequence = ""
    count = 0
    return  preprocess(preprocessArr(root,sequence, arr,count))

def remove_nodes_alone(longest):
    longest2=[]
    for i in range (len(longest)):
        if(str(longest[i]).__contains__("/")):
            longest2.append(longest[i])
    return longest2

def final_destination(root):
    long2=remove_nodes_alone(pre(root))
    return long2+preorder(root)

def TF(long2,node):
    count=0
    for i in range (len(long2)): 
        if(long2[i]==node):
            count+=1
    return count

def dict_TF(root):
    dictTF={}
    long2=final_destination(root)
    for i in range (len(long2)): 
        dictTF[long2[i]]=TF(long2,long2[i])
    return dictTF

def DF(node,arr1):
    count=0
    for i in range (len(arr1)):
        longDF= final_destination(arr1[i])
        if(TF(longDF,node) >=1):
            count+=1
    return count

def IDF(node):
    return abs(math.log(N/DF(node,getArrayRoots(arrayDocs)),10))

def dict_IDF(root):
    long2=final_destination(root)
    dictIDF={}
    for i in range (len(long2)):
        dictIDF[long2[i]]=IDF(long2[i])
    return dictIDF

def dict_TF_IDF(root):
    long2=final_destination(root)
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
        arrfinal[i]=final_destination(roott)
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
    arr=final_destination(root)
    return arr

def queryString(str:str):
    arr=str.split()
    return arr
def searchIndexMain(arr: array, threshold):
    arrayDoc=[]
    dict=indexingStructure
    arr1=[]
    for i in range (len(arr)):
        if(dict.__contains__(arr[i])):
              arr1=dict[arr[i]]
        for j in range (len(arr1)):
            if(arr1[j][1]>= threshold):
                if(not arrayDoc.__contains__(arr1[j][0])):
                    arrayDoc.append(arr1[j][0])
    return arrayDoc

def similarityRankingTree(root,threshold_index,treshold_similarity, mode, measure,k):
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
    if(len(arrDoc)==0):
        return []
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
    arrTemp = []
    if(len(arrDocsSort)<=k):
        return arrDocsSort
    else:
        for i in range (k):
            arrTemp.append(arrDocsSort[i])
        return arrTemp


def similarityRankingStr(str,threshold,treshold_similarity,k):
    str=str.lower()
    arr1=queryString(str)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[arr1[i]]=1
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold)
    if(len(arrDoc)==0):
        return []
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
    arrTemp = []
    if(len(arrDocsSort)<=k):
        return arrDocsSort
    else:
        for i in range (k):
            arrTemp.append(arrDocsSort[i])
        return arrTemp








if __name__ =='__main__':
    app.run(port=5500)