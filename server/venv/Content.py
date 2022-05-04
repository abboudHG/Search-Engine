from array import array
from synonyms import synonym_D5
import math
from tkinter.messagebox import NO
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import time
from indexingTables import indexingContent
import json

arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml","./XMLDOCS/D6.xml","./XMLDOCS/D7.xml" , "./XMLDOCS/D8.xml", "./XMLDOCS/D9.xml","./XMLDOCS/D10.xml","./XMLDOCS/D11.xml", "./XMLDOCS/D12.xml","./XMLDOCS/D13.xml","./XMLDOCS/D14.xml","./XMLDOCS/D15.xml","./XMLDOCS/D16.xml","./XMLDOCS/D17.xml","./XMLDOCS/D18.xml","./XMLDOCS/D19.xml","./XMLDOCS/D20.xml"]
N=len(arrayDocs)
#historyDict= json.load(open("History.json","r"))
app = Flask(__name__) 
CORS(app)
@app.route('/content', methods=[ 'POST', 'GET'])
def content():
    t1=time.time()
    t2=time.time()
    arr=[]
    strNew=""
    mode2=request.json['mode']
    query=request.json[ 'query']
    k=request.json['k']
    if(mode2=="xml"):
        root=ET.fromstring(query)
        arr=similarityRankingTree(root,0.01,0.01,"TF-IDF","euclidian",int(k))
        t2=time.time()
    if(mode2=="keywords"):
        arr=similarityRankingStr(query,0.001,0.001,int(k))
        t2=time.time()
    if(len(arr)==0):
        strNew=choose_Do_You_Mean(query)
    if(len(strNew)==0):
        strNew=synonymsSearch(query)
    return {'arrDoc': arr, 'time': t2-t1, 'results': len(arr),'word': strNew}

@app.route('/clearHistory', methods=['POST', 'GET'])
def clearHistory():
    fo = open("History.json", "w")
    fo.truncate()
    json.dump({}, open("History.json","w"))
    return

    





#-------------------------------------------------------------------------------------
def getRoot(doc):   #returns root of a specific document
    tree=ET.parse(doc)
    return tree.getroot()

def getArrayRoots(arr1): #returns an array containing all the roots of all documents respectively
    arr=[]
    for i in range(len(arr1)):
        tree=ET.parse(arr1[i])
        
        root=tree.getroot()
        arr.append(root)
    return arr


def contentProcess (root : ET.Element,arr): 
    str1=",.?!&#$%*^@)("
    arrStrings=['i','and', 'or','not', 'is', 'are', 'you', 'your', 'it', 'he', 'she', 'her', 'his', 'them', 'to', 'the','a','an','of', 'in', 'on', 'at','for', 'me','him','our', 'their', 'too']
    if(root.text != None ):
        arr3=root.text.split()
        arr2 =[]
        for i in range (len(arr3)):
            if(not arrStrings.__contains__(arr3[i]) and not str1.__contains__(arr3[i])):
                 arr2.append(arr3[i].lower())  # arr2 holds all the words
                 arr.append(arr3[i].lower())
        for i in range (len(arr2)):  # ex: abboud ate an apple --> abboud , ate, apple, abboud ate, ate apple...
            c=arr2[i]
            for j in range (i+1,len(arr2)):
                c += " " + arr2[j]
                arr.append(c)
    for child in root:
        contentProcess(child,arr)
    return arr

def TF(arr, node): # arr is the array containing all the contents of one doc (content process), and node is the string(node)
    count=0
    for i in range(len(arr)):
        if(arr[i]== node):
            count+=1
    return count

def dict_TF(root): #returns each node, how many times it occured in a document in form of a dictionnary
    dictTF={}
    arr=contentProcess(root,[])
    for i in range (len(arr)): 
        dictTF[arr[i]]=TF(arr,arr[i])
    return dictTF

def DF(node,arr1): # returns the number of documents node at least once in their doc
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

def extend_dict(dict1,dict2): #extends dict2 into dict1
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

def euclidian_measure(dict3,dict4): # 1/ 1+ radical(sum (Ai-Bi)^2)
    dict2=extend_dict(dict3,dict4)
    dict1=extend_dict(dict4,dict3)
    numerator=1
    den1=0
    for key in dict1:
        den1+=(float(dict1[key])-float(dict2.__getitem__(key)))**2
    den2=math.sqrt(den1)
    denominator=1+den2
    return numerator/denominator

def AllPath_AllDocuments(arr):  #array that contains all the content of all documents 
    #arr=[]
    arrfinal = [0 for i in range(len(arr))]
    for i in range (len(arr)):
        roott=getArrayRoots(arr)[i]
        arrfinal[i]=contentProcess(roott,[])
    return arrfinal

def AllPath_AllDocuments_unique(arr): #removes duplicate content from the function above
    arr_unique=[]
    for i in range (len(arr)):
        for j in range(len(arr[i])):
            if(not arr_unique.__contains__(arr[i][j])):
                arr_unique.append(arr[i][j])
    return arr_unique

def dict_docs_roots(arrayDocs): #{D1: root of D1....}
    dict_D_docs={}
    for i in range(len(arrayDocs)):
        dict_D_docs[str("D")+str(i+1)]=getArrayRoots(arrayDocs)[i]
    return dict_D_docs

def index_structure(arr):  #takes arguments allpathsunique(allpathsdocuments(arraydocs))
    dict_index_structure={} #to return 
    dict_all_doc={}
    dict1=dict_docs_roots(arrayDocs) #[D1:root doc1, D2:root D2....]
    for i in range (len(dict1)):
        dict_all_doc[str("D")+str(i+1)]=dict_TF_IDF(dict1.get(str("D")+str(i+1))) # {D1:{Tf id of D1}, D2: {Tf-idf of T2}}
    for i in range (len(arr)): # for every content we are appending which is an empty array
        dict_index_structure[arr[i]]=[]
    arraykeys=[]
    for k in dict_index_structure:
        arraykeys.append(k) #using an array holding every content we have 
    for i in range(len(dict_index_structure)):
        arrfinal=[]
        for j in range(len(dict_all_doc)):
            arrayDocj=[]
            arrayDocj.append(str("D")+str(j+1))
            if(dict_all_doc[str("D")+str(j+1)].__contains__(arraykeys[i])):
                arrayDocj.append(dict_all_doc[str("D")+str(j+1)][arraykeys[i]]) #appends D1 with its weight 
                arrfinal.append(arrayDocj) #append [D1, 0.9] to the final array
        dict_index_structure[arraykeys[i]]=arrfinal
    return dict_index_structure

def doc_XML(str):
    str="./XMLDOCS/"+str+".xml"
    return str

def queryTree(root):
    arr=contentProcess(root,[])
    return arr

def queryString(str:str):
    arr=[]
    if (str[0]=='"' and str[-1]=='"'):
        arr = [str[1:len(str)-1].lower()] # we add the phrase as it is into the array
    else:
        arr = str.split()
    return arr

def searchIndexMain(arr: array, threshold): #takes as arguments the pre processing array containing the content of the query
    arrayDoc=[]
    dict=indexingContent 
    arr1=[]
    for i in range (len(arr)):
        if(dict.__contains__(arr[i])):
            arr1=dict[arr[i]]
        for j in range (len(arr1)):
            if(arr1[j][1]>= threshold):
                if(not arrayDoc.__contains__(arr1[j][0])):
                    arrayDoc.append(arr1[j][0])
    return arrayDoc # returns all documents that contain the words in the array, with respect to a certain threshold

def similarityRankingTree(root,threshold_index,treshold_similarity, mode, measure,k):
    arrDocsSort=[] # the final array to return
    dictSort={}
    arr_values=[]
    arr1=queryTree(root) # returns the array of pre processing containing all content of the specific tree
    dict1={}
    dict2={}
    
    dict1=dict_TF(root) # dict Tf of the query
   
   
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold_index) # all the documents that we got from the indexing table that contain the words that we searched
   
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
        dictSort[arrDoc[i]]=sim # {D1: similarity between query and document, D2: ...}
    for key in dictSort:
        arr_values.append(dictSort[key]) # appending in an array all values of similarities
    arr_values.sort() #sorting our similarities
    arr_values_sort=arr_values
    arr_values_sort=arr_values_sort[::-1] # reverse the order , decreasing 
    for i in range (len(arr_values_sort)):
        for key in dictSort:
            if(dictSort[key]==arr_values_sort[i] and dictSort[key]>=treshold_similarity):
                arrDocsSort.append(key)
                dictSort[key]= 2
    arrTemp = []
    #KNN
    if(len(arrDocsSort)<=k):
        return arrDocsSort
    else:
        for i in range (k):
            arrTemp.append(arrDocsSort[i])
        return arrTemp
    
def similarityRankingStr(str,threshold,treshold_similarity,k):
    str=str.lower()
    #history search 
    historyDict = json.load(open("History.json","r"))
    if(historyDict.__contains__(str)):
        arrHistTemp=[]
        arrHistory= historyDict[str]
        if(len(historyDict[str])<=k):
            return historyDict[str]
        else:
            for i in range(k):
                arrHistTemp.append(arrHistory[i])
            return arrHistTemp
            
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
    historyDict[str]=arrDocsSort
    json.dump(historyDict, open("History.json","w"))
    arrTemp = []
    if(len(arrDocsSort)<=int(k)):
        return arrDocsSort
    else:
        for i in range (k):
            arrTemp.append(arrDocsSort[i])
        return arrTemp

def costUpdate(char1,char2):
    if(char1==char2):
        return 0
    else: return 1

def Wegner_Fisher(str1 :str, str2 : str):
    len1 = len(str1)
    len2 = len(str2)
    dist=[[0 for x in range (len2+1)] for y in range (len1+1)]
    dist[0][0]=0
    for i in range (1,len1+1):
        dist[i][0] = dist[i-1][0]+1
    for j in range (1,len2+1):
        dist[0][j] = dist[0][j-1]+1
    for i in range (1,len1+1):
        for j in range (1,len2+1):
            a=dist[i-1][j-1]+costUpdate(str1[i-1], str2[j-1])
            b=dist[i-1][j]+1
            c=dist[i][j-1]+1
            dist[i][j]= min(a,b,c)
  
    return dist[len1][len2]

 #first one row, second one column

def choose_Do_You_Mean(str1 :str):
    minimum=100
    str_to_choose=""
    for key in indexingContent:
        num = Wegner_Fisher(str1,key)
       # print("num = "+ str(num))
        if(num < minimum and num<3):
            
            minimum=num
           # print("minimum = "+str(minimum))
            str_to_choose=key
           # print("key is: "+str(key))
    return str_to_choose

def synonymsSearch(str):
    for key in synonym_D5:
        arr=synonym_D5[key]
        for j in range(len(arr)):
            if(arr[j]==str):
                return key
    return None


        


if __name__ =='__main__':
    app.run(port=5600)