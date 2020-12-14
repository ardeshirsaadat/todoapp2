from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:16760@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todolist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todo = db.relationship('Todo', backref='list',
                           lazy=True, cascade='all, delete-orphan')


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'todolist.id'), nullable=False)

    def __repr__(self):
        return f'<Todo:{self.id},Description:{self.description}'


# db.create_all()


@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())


@app.route('/todo/create', methods=['POST'])
def create():
    error = False
    body = {}
    try:
        toDoItem = request.get_json()['todo']
        objectSendToDatabase = Todo(description=toDoItem)
        db.session.add(objectSendToDatabase)
        db.session.commit()
        body['description'] = objectSendToDatabase.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todo/<todo_id>/completeTodoCheckbox', methods=['POST'])
def completeTodoCheckbox(todo_id):
    try:
        completed_state = request.get_json()['completed']
        todoObject = Todo.query.get(todo_id)
        todoObject.completed = completed_state
        db.session.commit()
    except:
        print('smth wrong')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todo/<todo_id>/delete', methods=['DELETE'])
def delete(todo_id):
    try:
        objectToRemove = Todo.query.get(todo_id)
        db.session.delete(objectToRemove)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # return redirect(url_for('index'))
    return jsonify({'success': True})
