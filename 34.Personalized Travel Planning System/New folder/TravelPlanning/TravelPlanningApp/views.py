from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import pymysql
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import dot
from numpy.linalg import norm
import math
import operator

global filename
global X, Y
global user_db, content_db
global vector

user_db = pd.read_csv("Dataset/User.csv",usecols=['Age','Sex','Category','Places'])
content_db = pd.read_csv("Dataset/data_content.csv")
user_db.fillna(0, inplace = True)
content_db.fillna(0, inplace = True)
content_db = content_db.values
user_db = user_db.values

X = []
Y = []
for i in range(len(user_db)):
    age = str(user_db[i,0]).strip()
    sex = user_db[i,1].strip().lower()
    category = user_db[i,2].strip().lower()
    places = user_db[i,3].strip().lower()
    content = age+" "+sex+" "+category+" "+places
    X.append(content)
    Y.append(category+","+places)
vector = TfidfVectorizer()
X = vector.fit_transform(X).toarray()
print(X)
   
def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})
    

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def Predict(request):
    if request.method == 'GET':
       return render(request, 'Predict.html', {})    


def PredictAction(request):
    if request.method == 'POST':
        query = request.POST.get('t1', False)
        user_recommend = []
        global X, Y, vector, content_db
        testArray = vector.transform([query]).toarray()
        testArray = testArray[0]
        for i in range(len(X)):
            recommend = dot(X[i], testArray)/(norm(X[i])*norm(testArray))
            if recommend > 0:
                user_recommend.append([Y[i],recommend])
        user_recommend.sort(key = operator.itemgetter(1),reverse=True)
        top_recommend = []
        for index in range(0,5):
            top_recommend.append(user_recommend[index][0])
        top = max(top_recommend,key=top_recommend.count)
        array = top.split(",")
    
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Recommended Tourist Destination','Distance','Duration','Nearby Places','Rating']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        output += "</tr>"    
        for i in range(len(content_db)):
            if array[0] == str(content_db[i,0]).strip().lower():
                distance = str(content_db[i,1]).strip()
                duration = str(content_db[i,2]).strip()
                nearby = str(content_db[i,4]).strip()
                rating = str(content_db[i,6]).strip()
                output += "<tr><td>"+font+str(array[1])+"</td>"
                output += "<td>"+font+str(distance)+"</td>"
                output += "<td>"+font+str(duration)+"</td>"
                output += "<td>"+font+str(nearby)+"</td>"
                output += "<td>"+font+str(rating)+"</td></tr>"
        context= {'data':output}
        return render(request, 'ViewRecommendation.html', context)    


def LoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'TravelApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1]:
                    uname = username
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+uname}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'Login.html', context)

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'TravelApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"
                    break
        if output == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'TravelApp',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(username,password,contact_no,gender,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+gender+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = 'Signup Process Completed'
        context= {'data':output}
        return render(request, 'Signup.html', context)
      


