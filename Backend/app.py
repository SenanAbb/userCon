from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from bson import json_util

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost/userConn'
mongo = PyMongo(app)

@app.route('/')
def index():
    #Recibiendo datos
    return render_template("index.html")

@app.route('/homepage', methods=['GET','POST'])
def login():
    #Compruebo el método
    if request.method == 'GET': 
        name = request.args.get('name')
        user = mongo.db.users.find_one({'name': name})
        return render_template("homepage.html", user = user)
    else:
        name = request.form.get('name')
        #Si no se encuentra en la base de datos -> lo creo (aseguramos que sea unico)
        if (not mongo.db.users.find_one({"name": name})):
            id = mongo.db.users.insert_one({
                'name': name,
                'conn': []
            })
            print(id)
            return("post")
        #Si lo hemos encontrado
        else:
            return "Ya esta registrado"

#####FALTA DEFINIR EL RETURN
@app.route('/addConn/<id_user>/<name_to_add>', methods=['PUT'])
def add_conn(id_user, name_to_add):
    #Busco el usuario de la sesion
    user = mongo.db.users.find_one({'_id':ObjectId(id_user)})

    #Busco al usuario por añadir, para obtener su ID
    user_to_add = mongo.db.users.find_one({'name':name_to_add})

    #Modifico la lista de conexiones de user, añadiendo al nuevo usuario, y viceversa
    user['conn'] += [
        {
            '_id': user_to_add['_id'],
            'name': user_to_add['name']
        }
    ]

    user_to_add['conn'] += [
        {
            '_id': user['_id'],
            'name': user['name']
        }
    ]

    #Actualizo los usuarios
    update = mongo.db.users.update_one(
        {'_id': ObjectId(id_user)},
        {'$set':{
            'conn': user['conn']
            }
        }
    )

    update = mongo.db.users.update_one(
        {'_id': user_to_add['_id']},
        {'$set':{
            'conn': user_to_add['conn']
            }
        }
    )
    return "1"

@app.route('/deleteConn/<id>/<id_to_delete>', methods=['PUT'])
def delete_conn(id, id_to_delete):
    update_conn_list(id, id_to_delete)
    update_conn_list(id_to_delete, id)
    print(id)
    print(id_to_delete)
    return "boorao"

def update_conn_list(id, id_to_delete):
    cont = 0
    #Buscamos al usuario con "id"
    user = mongo.db.users.find_one({'_id':ObjectId(id)})
    #Actualizo el usuario
    update = mongo.db.users.update_one(
        {'_id':ObjectId(id)},
        {'$pull':
            {'conn': {'$elemMatch': {'_id': ObjectId(id_to_delete)}}}
        }
    )

def update_user_deleted_conn_list(name_to_delete, id, cont):    
    cont = 0
    #Busco el usuario de la sesion
    data = mongo.db.users.find_one({"name":name_to_delete})

    #Elimino el usuario de su lista de conexiones
    for i in data['conn']:
        if i == name_to_delete:
            data['conn'].pop(cont)
        cont += 1

    #Actualizo el usuario
    update = mongo.db.users.update(
        {'_id': ObjectId(id)},
        {'$set':{
            'conn': data['conn']
            }
        }
    )

if __name__ == "__main__":
    app.run(debug=True)