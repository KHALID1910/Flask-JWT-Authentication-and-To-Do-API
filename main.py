from flask import Flask, render_template, request, redirect, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps 


app = Flask(__name__)

app.config['SECRET_KEY']='thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///jwt-todo.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(20), unique=True)
    name=db.Column(db.String(100))
    password=db.Column(db.String(50))
    admin=db.Column(db.Boolean)
    
    
class Todo(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    text=db.Column(db.String(500), nullable=False)
    completed=db.Column(db.Boolean, default=False)
    user_id=db.Column(db.Integer)
    
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(f"Received Token: {token}")  # Debugging

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            print(f"Decoded Data: {data}")
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
    
@app.route("/user", methods=['GET'])
@token_required
def get_all_users(current_user):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    data=[]
    users=User.query.all()
    if not users:
        return jsonify({"message": "no data found!!!!"})
    
    for user in users:
        output={}
        output['id']=user.id
        output['public_id']=user.public_id
        output['name']=user.name
        output['password']=user.password
        output['admin']=user.admin
        data.append(output)
    return jsonify({"users ": data})

@app.route("/user/<public_id>", methods=["GET"])
@token_required
def get_one_user(current_user,public_id):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    user= User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "Invalid id or no record found!!!"})
    
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    
    return jsonify({"user" : user_data})

@app.route("/user", methods=['POST'])
def create_user():
    data=request.get_json()
    hashed_password = generate_password_hash(data['password']) # we can use pbkdf2:sha256 or another supported method like bcrypt or argon2
    new_user=User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message" : "user created successfully!!"})

@app.route("/user/<public_id>", methods=['PUT'])
@token_required
def promote_user(current_user,public_id):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    user=User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "Invalid id or no record found!!!"})
    user.admin=True
    db.session.commit()
    return jsonify({"message":"user has been promoted to admin!!"})

@app.route("/user/<public_id>", methods=['DELETE'])
@token_required
def delete_user(current_user,public_id):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    user=User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "Invalid id or no record found!!!"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message":"user has been deleted successfully!!!"})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("could not verify", 404, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(name=auth.username).first()
    
    if not user:
        return make_response("could not verify", 404, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 
            app.config['SECRET_KEY'], algorithm='HS256'
        )

        # Remove `.decode('UTF-8')`
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    output = []

    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['completed'] = todo.completed
        output.append(todo_data)

    return jsonify({'todos' : output})

@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['completed'] = todo.completed

    return jsonify(todo_data)

@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()

    new_todo = Todo(text=data['text'], completed=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message' : "Todo created!"})

@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    todo.completed = True
    db.session.commit()

    return jsonify({'message' : 'Todo item has been completed!'})

@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'Todo item deleted!'})

    
if __name__ == '__main__':
    app.run(debug=True, port=8000)
    