from array import ArrayType, array
import math
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import time
from indexingTables import indexingContent,indexingContentStructure,indexingStructure
arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml","./XMLDOCS/D6.xml","./XMLDOCS/D7.xml" ]
N=len(arrayDocs)
app = Flask(__name__) 
CORS(app)


@app.route('/advanced', methods=['POST','GET'])
def advanced():
    t1=time.time()
    type=request.json['type']
    mode=request.json['mode']
    measure=request.json['measure']
    queryType=request.json['queryType']
    query=request.json['query']
    arr=[]
    if(type=="structure"):
        if(queryType=="tree"):
            root=ET.fromstring(query)
            arr=similarityRankingTreeStruct(root,0.01,0.01,mode,measure)
            t2=time.time()
        if(queryType=="keywords"):
            arr=similarityRankingStrStruct(query,0.001,0.001,mode,measure)
            t2=time.time()
    if(type=="content"):
        if(queryType=="tree"):
            root=ET.fromstring(query)
            arr=similarityRankingTreeContent(root,0.01,0.01,mode,measure)
            t2=time.time()
        if(queryType=="keywords"):
            arr=similarityRankingStrContent(query,0.001,0.001,mode,measure)
            t2=time.time()
    if(type=="structureContent"):
        if(queryType=="tree"):
            root=ET.fromstring(query)
            arr=similarityRankingTree(root,0.01,0.01,mode,measure)
            t2=time.time()
        if(queryType=="keywords"):
            arr=similarityRankingStr(query,0.001,0.001,mode,measure)
            t2=time.time()

    return{'arrDoc': arr, 'time': t2-t1, 'results': len(arr)}





















# Structure------------------------------------------------------------------------------


def getArrayRootsStruct(arr1):
    arr=[]
    for i in range(len(arr1)):
        tree=ET.parse(arr1[i])
        root=tree.getroot()
        arr.append(root)
    return arr
def getRootStruct(doc):
    tree=ET.parse(doc)
    return tree.getroot()

def countChildStruct(root):
    count=0
    for child in root:
        count=count+1
    return count
def preorderStruct(root):
    if root is None:
        return []
    ans= [root.tag]
    for x in root:
        ans += preorderStruct(x)
    return ans
def preprocessArrStruct(root: ET.Element,sequence : str , arr,count ):
    count = count +1
    seq = sequence
    seq = seq.__add__(root.tag + "/")
    arr.append(seq)
    # if(countChild(root)==0):
    #  arr.append(seq)
    for child in root:
        seq2 = ""
        if(count ==1):
            preprocessArrStruct(child,seq2,arr,count)
        preprocessArrStruct(child,seq,arr,count)   
    return arr
def preprocessStruct(arr):
    count = len(arr)
    i = 0
    while(i < count):
        arr[i] = arr[i][:len(arr[i]) -1 ]
        i = i+1
    return arr
def preStruct(root:ET.Element):
    arr = []
    sequence = ""
    count = 0
    return  preprocessStruct(preprocessArrStruct(root,sequence, arr,count))

def remove_nodes_aloneStruct(longest):
    longest2=[]
    for i in range (len(longest)):
        if(str(longest[i]).__contains__("/")):
            longest2.append(longest[i])
    return longest2

def final_destinationStruct(root):
    long2=remove_nodes_aloneStruct(preStruct(root))
    return long2+preorderStruct(root)

def TFStruct(long2,node):
    count=0
    for i in range (len(long2)): 
        if(long2[i]==node):
            count+=1
    return count

def dict_TFStruct(root):
    dictTF={}
    long2=final_destinationStruct(root)
    for i in range (len(long2)): 
        dictTF[long2[i]]=TFStruct(long2,long2[i])
    return dictTF

def DFStruct(node,arr1):
    count=0
    for i in range (len(arr1)):
        longDF= final_destinationStruct(arr1[i])
        if(TFStruct(longDF,node) >=1):
            count+=1
    return count

def IDFStruct(node):
    return abs(math.log(N/DFStruct(node,getArrayRootsStruct(arrayDocs)),10))

def dict_IDFStruct(root):
    long2=final_destinationStruct(root)
    dictIDF={}
    for i in range (len(long2)):
        dictIDF[long2[i]]=IDFStruct(long2[i])
    return dictIDF

def dict_TF_IDFStruct(root):
    long2=final_destinationStruct(root)
    dictTF_IDF={}
    for i in range (len(long2)): 
        dictTF_IDF[long2[i]]=IDFStruct(long2[i])*TFStruct(long2,long2[i])
    return dictTF_IDF

def extend_dictStruct(dict1,dict2):
    arr1=[]
    dict11={}   
    for key in dict1:
        if key not in dict2.keys():
            arr1.append(key)
    for i in range (len(arr1)): 
        dict11[arr1[i]]=0
    dict2.update(dict11)
    return dict2

def cosine_measureStruct(dict3,dict4):
    numerator=0
    dict2=extend_dictStruct(dict3,dict4)
    dict1=extend_dictStruct(dict4,dict3)
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

def euclidian_measureStruct(dict3,dict4):
    dict2=extend_dictStruct(dict3,dict4)
    dict1=extend_dictStruct(dict4,dict3)
    numerator=1
    den1=0
    for key in dict1:
        den1+=(float(dict1[key])-float(dict2.__getitem__(key)))**2
    den2=math.sqrt(den1)
    denominator=1+den2
    return numerator/denominator



def pearsonStruct(dict3,dict4):
    dict1_sum=0
    count=0
   
    for key in dict3:
        dict1_sum+=(float(dict3[key]))
        count+=1
    dict1_avg=dict1_sum/count
    dict2_sum=0
    count2=0
    for key in dict4:
        dict2_sum+=(float(dict4[key]))
        count2+=1
    dict2_avg=dict2_sum/count2
    dict2=extend_dictStruct(dict3,dict4)
    dict1=extend_dictStruct(dict4,dict3)
    num=0
    for key in dict1:
        num+=(float(dict1.__getitem__(key))-dict1_avg)*(float(dict2.__getitem__(key))-dict2_avg)
    numerator=num
    den=0
    for key in dict1:
        den+=((float(dict1.__getitem__(key))-dict1_avg)**2)*((float(dict2.__getitem__(key))-dict2_avg)**2)
    denominator=math.sqrt(den)
   
    return numerator/denominator


def AllPath_AllDocumentsStruct(arr):
    #arr=[]
    arrfinal = [0 for i in range(len(arr))]
    for i in range (len(arr)):
        roott=getArrayRootsStruct(arr)[i]
        arrfinal[i]=final_destinationStruct(roott)
    return arrfinal

def AllPath_AllDocuments_uniqueStruct(arr):
    arr_unique=[]
    for i in range (len(arr)):
        for j in range(len(arr[i])):
            if(not arr_unique.__contains__(arr[i][j])):
                arr_unique.append(arr[i][j])
    return arr_unique

def dict_docs_rootsStruct(arrayDocs):
    dict_D_docs={}
    for i in range(len(arrayDocs)):
        dict_D_docs[str("D")+str(i+1)]=getArrayRootsStruct(arrayDocs)[i]
    return dict_D_docs




def doc_XMLStruct(str):
    str="./XMLDOCS/"+str+".xml"
    return str

def queryTreeStruct(root):
    arr=final_destinationStruct(root)
    return arr

def queryStringStruct(str:str):
    arr=str.split()
    return arr
def searchIndexMainStruct(arr: array, threshold):
    arrayDoc=[]
    dict=indexingStructure
    arr1=[]
    for i in range (len(arr)):
        arr1=dict[arr[i]]
        for j in range (len(arr1)):
            if(arr1[j][1]>= threshold):
                if(not arrayDoc.__contains__(arr1[j][0])):
                    arrayDoc.append(arr1[j][0])
    return arrayDoc

def similarityRankingTreeStruct(root,threshold_index,treshold_similarity, mode, measure):
    arrDocsSort=[]
    dictSort={}
    arr_values=[]
    arr1=queryTreeStruct(root)
    dict1={}
    dict2={}
    if(mode=="TF"):
        dict1=dict_TFStruct(root)
    if(mode=="IDF"):
        dict1=dict_IDFStruct(root)
    if(mode=="TF-IDF"):
        dict1=dict_TF_IDFStruct(root)
   
    arr_values_sort=[]
    arrDoc=searchIndexMainStruct(arr1,threshold_index)
    sim=0
    for i in range(len(arrDoc)):
        if(mode=="TF"):
            dict2=dict_TFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_measureStruct(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measureStruct(dict1,dict2)
        if(measure=="pearson"):
            sim=euclidian_measureStruct(dict1,dict2)
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


def similarityRankingStrStruct(str,threshold,treshold_similarity,mode,measure):
    arr1=queryStringStruct(str)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[arr1[i]]=1
    arr_values_sort=[]
    arrDoc=searchIndexMainStruct(arr1,threshold)
    sim=0
    for i in range(len(arrDoc)):
        
        if(mode=="TF"):
            dict2=dict_TFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDFStruct(getRootStruct(doc_XMLStruct(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_measureStruct(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measureStruct(dict1,dict2)
        if(measure=="pearson"):
            sim=euclidian_measureStruct(dict1,dict2)
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


#Content ---------------------------------------------------------------------

def getRootContent(doc):
    tree=ET.parse(doc)
    return tree.getroot()

def getArrayRootsContent(arr1):
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

def TFContent(arr, node): # arr hiye l big array w  arr1 hiye one node maa l context
    count=0
    for i in range(len(arr)):
        if(arr[i]== node):
            count+=1
    return count

def dict_TFContent(root):
    dictTF={}
    arr=contentProcess(root,[])
    for i in range (len(arr)): 
        dictTF[arr[i]]=TFContent(arr,arr[i])
    return dictTF

def DFContent(node,arr1):
    count=0
    for i in range (len(arr1)):
        longDF= contentProcess(arr1[i],[])
        if(TFContent(longDF,node) >=1):
            count+=1
    return count

def IDFContent(node):
    return abs(math.log(N/DFContent(node,getArrayRootsContent(arrayDocs)),10))

def dict_IDFContent(root):
    long2=contentProcess(root,[])

    dictIDF={}
    for i in range (len(long2)):
        dictIDF[long2[i]]=IDFContent(long2[i])
    return dictIDF

def dict_TF_IDFContent(root):
    long2=contentProcess(root,[])
    dictTF_IDF={}
    for i in range (len(long2)): 
        dictTF_IDF[long2[i]]=IDFContent(long2[i])*TFContent(long2,long2[i])
    return dictTF_IDF

def extend_dictContent(dict1,dict2):
    arr1=[]
    dict11={}   
    for key in dict1:
        if key not in dict2.keys():
            arr1.append(key)
    for i in range (len(arr1)): 
        dict11[arr1[i]]=0
    dict2.update(dict11)
    return dict2

def cosine_measureContent(dict3,dict4):
    numerator=0
    dict2=extend_dictContent(dict3,dict4)
    dict1=extend_dictContent(dict4,dict3)
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

def euclidian_measureContent(dict3,dict4):
    dict2=extend_dictContent(dict3,dict4)
    dict1=extend_dictContent(dict4,dict3)
    numerator=1
    den1=0
    for key in dict1:
        den1+=(float(dict1[key])-float(dict2.__getitem__(key)))**2
    den2=math.sqrt(den1)
    denominator=1+den2
    return numerator/denominator

def AllPath_AllDocumentsContent(arr):
    #arr=[]
    arrfinal = [0 for i in range(len(arr))]
    for i in range (len(arr)):
        roott=getArrayRootsContent(arr)[i]
        arrfinal[i]=contentProcess(roott,[])
    return arrfinal

def AllPath_AllDocuments_uniqueContent(arr):
    arr_unique=[]
    for i in range (len(arr)):
        for j in range(len(arr[i])):
            if(not arr_unique.__contains__(arr[i][j])):
                arr_unique.append(arr[i][j])
    return arr_unique

def dict_docs_rootsContent(arrayDocs):
    dict_D_docs={}
    for i in range(len(arrayDocs)):
        dict_D_docs[str("D")+str(i+1)]=getArrayRootsContent(arrayDocs)[i]
    return dict_D_docs


def doc_XMLContent(str):
    str="./XMLDOCS/"+str+".xml"
    return str

def queryTreeContent(root):
    arr=contentProcess(root,[])
    return arr

def queryStringContent(str:str):
    arr=str.split()
    return arr
def searchIndexMainContent(arr: array, threshold):
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

def similarityRankingTreeContent(root,threshold_index,treshold_similarity, mode, measure):
    arrDocsSort=[]
    dictSort={}
    arr_values=[]
    arr1=queryTreeContent(root)
    dict1={}
    dict2={}
    if(mode=="TF"):
        dict1=dict_TFContent(root)
    if(mode=="IDF"):
        dict1=dict_IDFContent(root)
    if(mode=="TF-IDF"):
        dict1=dict_TF_IDFContent(root)
   
    arr_values_sort=[]
    arrDoc=searchIndexMainContent(arr1,threshold_index)
    sim=0
    for i in range(len(arrDoc)):
        if(mode=="TF"):
            dict2=dict_TFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_measureContent(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measureContent(dict1,dict2)
        if(measure=="pearson"):
            sim=euclidian_measureContent(dict1,dict2)
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
    
def similarityRankingStrContent(str,threshold,treshold_similarity,mode,measure):
    arr1=queryStringContent(str)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[arr1[i]]=1
    arr_values_sort=[]
    arrDoc=searchIndexMainContent(arr1,threshold)
    sim=0
    for i in range(len(arrDoc)):
        if(mode=="TF"):
            dict2=dict_TFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(mode=="IDF"):
            dict2=dict_IDFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(mode=="TF-IDF"):
            dict2=dict_TF_IDFContent(getRootContent(doc_XMLContent(arrDoc[i])))
        if(measure=="cosine"):
            sim=cosine_measureContent(dict1,dict2)
        if(measure=="euclidian"):
            sim=euclidian_measureContent(dict1,dict2)
        if(measure=="pearson"):
            sim=euclidian_measureContent(dict1,dict2)
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

#Struct+Content---------------------------------------------------------------------

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
    sim=0
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

def similarityRankingStr(str1,threshold,treshold_similarity,mode,measure):
    arr1=queryString(str1)
    arr_values=[]
    arrDocsSort=[]
    dict1={}
    dictSort={}
    for i in range (len(arr1)):
        dict1[str(arr1[i][0])+","+str(arr1[i][1])]=1
    arr_values_sort=[]
    arrDoc=searchIndexMain(arr1,threshold)
    sim=0
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






































if __name__ =='__main__':
    app.run(port=4000)