import json
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
import xml.etree.ElementTree as ET
import time
app = Flask(__name__) 
CORS(app)

arrayDocs=["./XMLDOCS/D1.xml", "./XMLDOCS/D2.xml","./XMLDOCS/D3.xml","./XMLDOCS/D4.xml","./XMLDOCS/D5.xml"]


@app.route('/TED',methods=['POST'])
def getTED():
    doc1=0
    doc2=0
    t0 = time.time()
    source=request.json['source']
    destination=request.json['destination']
   
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
    

    root1=getRoot(doc1)
    root2=getRoot(doc2)
    TED1=TED(root1,root2)
    t1 = time.time()
    TEDfinal={'TED':1/(1+TED1), 'timeTED':t1-t0 }
    
    return TEDfinal

def preorder(root):
    if root is None:
        return []
    ans= [root]
    for x in root:
        ans += preorder(x)
    return ans
def getRoot(doc):
    tree=ET.parse(doc)
    return tree.getroot()
def countChild(root):

    count=0

    for child in root:

        count=count+1

    return count

def preorderTag(root:ET.Element):

    if root is None:

        return []

    ans= [root.tag]

    for x in root:

        ans += preorderTag(x)

    return ans

 

def countTree(root):

    count =0

    for rootA in root.iter():

        count = count +1

    return count

def listChild(root):

    arr = []

    count = 0

    arr.insert(count,root)

    count= count +1

    for x in root:

        arr.insert(count,x)

        count = count +1

    return arr





def TED2(treeA,treeB,tree1,tree2):
    M=countChild(treeA)
    N=countChild(treeB)
    dist=[[0 for x in range (N+1)] for y in range (M+1)]
    ES=[[0 for x in range (N+1)] for y in range (M+1)]

   

    arrA=preorder(treeA)

   

    arrB=preorder(treeB)

 

    arr1 = listChild(treeA)

    arr2 = listChild(treeB)

   

 

    dist[0][0]=costUpdate(arrA[0],arrB[0])

    if(dist[0][0] != 0):

        ES[0][0]="U00"

   

    for i in range(1,M+1):

     

        dist[i][0]=dist[i-1][0]+cost(arr1[i],tree2)

        ES[i][0]="D"

   

    for j in range(1,N+1):

            #print(j)

            dist[0][j]=dist[0][j-1]+cost(arr2[j],tree1)

            # print(arrB[j])

            # print(j)

            ES[0][j]="I"

         

       

       

   

   

    for i in range(1,M+1):

       

        for j in range(1,N+1):

            x=dist[i-1][j-1]+TED2(arr1[i],arr2[j],tree1,tree2) #update

         

            y=dist[i-1][j]+cost(arr1[i],tree2) #delete

           

            z=dist[i][j-1]+cost(arr2[j],tree1) #insert

 

            minimum = min(x,y,z)

            if(minimum==x):

                ES[i][j]="U"

            if(minimum==y):

                ES[i][j]="D"

            if(minimum==z):

                ES[i][j]="I"

               

               

 

            dist[i][j]=minimum

   

   

    arr=[]

   

   

    return dist[M][N]

def costUpdate(rootA,rootB):

    if(rootA.tag == rootB.tag):

        return 0

    else:

        return 1
def cost(treeA , treeB):

    rootC = treeA

    arr = preorderTag(treeA)

   

    for rootB in treeB.iter():

        arr2= preorderTag(rootB)

       

        if(arr == arr2):

                return 1  

 

    return countTree(rootC)


def TED(treeA,treeB):

  tree1 = treeA

  tree2 = treeB

  ED = TED2(treeA, treeB,tree1,tree2)

  return ED



if __name__ =='__main__':
    app.run(port=5400)