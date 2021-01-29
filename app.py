from flask import Flask, jsonify, request 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth

# creating a Flask app 
app = Flask(__name__)

#basic authentication 
api = Api(app, prefix="/api/v1")
auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "supersecret"
}

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

db=firestore.client()

docs = db.collection('books_list').get()

x=[]

for doc in docs:
    x.append(doc.to_dict())

#list and create
@app.route('/books',methods=['GET','POST']) 
@auth.login_required
def books():
    if(request.method == 'GET'):
        if len(x)>0:
            return jsonify(x)
        else:
            'Nothing found',404
    if request.method == 'POST':
        iD = request.args.get('id')
        doc_ref=db.collection('books_list').document(iD)
        new_author = request.args.get('author')
        new_lang = request.args.get('language')
        new_title = request.args.get('title')
        doc_ref.set(
            {
            "id" : iD,
            "author" : new_author,
            "language" : new_lang,
            "title" : new_title
            })
        return "created"
        
#read,update and delete
@app.route('/books/<int:id>',methods=['GET','PUT','DELETE'])
@auth.login_required
def single_book(id):
    if request.method == 'GET':
        for book in x:
            if book["id"] == id:
                return jsonify(book)
            pass
    if request.method == 'PUT':
        iD = request.args.get('id')
        new_author = request.args.get('author')
        new_lang = request.args.get('language')
        new_title = request.args.get('title')
        updated_book={
            "id" : iD,
            "author" : new_author,
            "language" : new_lang,
            "title" : new_title
            }
        db.collection('books_list').document(iD).update(updated_book)
        return "updated"
    if request.method == 'DELETE':
        todo_id = request.args.get('docname')
        doc_ref=db.collection('books_list').document(todo_id)
        doc_ref.delete()
        return "deleted"

#filter
@app.route('/filter/',methods=['GET','PUT'])
@auth.login_required
def filter():
    new_lang = request.args.get('language')
    docs=db.collection('books_list').where('language','==',new_lang).get()
    a=[]
    for doc in docs:
        a.append(doc.to_dict())
    return jsonify(a),200

#driver function 
if __name__ == '__main__': 
  
    app.run(debug = True) 