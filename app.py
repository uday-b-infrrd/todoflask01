from os import error
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
        load_instance = True

todoSchema = TodoSchema()
todoListSchema = TodoSchema(many=True)

@app.route('/', methods=['GET'])
def index():
    tasks = Todo.query.order_by(Todo.date_created).all()
    all_tasks = todoListSchema.dump(tasks)
    if not tasks:
        error = "No tasks available"
        return jsonify(error)
    else:
        return jsonify(all_tasks)

@app.route('/add', methods=['Post'])
def add():
    task_content = request.get_json()
    if task_content['content'] == '':
        return jsonify({'error': 'content should not be empty'})
    else:          
        todo_content = task_content['content']
        new_task = Todo(content = todo_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'message': 'Successfully task added'})
        except:
            return jsonify({'error' : 'There was an issue adding your task'})

@app.route('/delete/<task_id>',methods=['GET'])
def delete(task_id):
    task_to_delete = Todo.query.get_or_404(task_id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return jsonify({'message': 'task deleted successfully'})
    except:
        return jsonify({'error': 'There was a problem deleting that task...plz retry'})

@app.route('/update/<task_id>', methods=['GET', 'POST'])
def update(task_id):
    task = Todo.query.get_or_404(task_id)

    if request.method == 'POST':
        task_content = request.get_json()
        task.content = task_content['content']
        try:
            db.session.commit()
            return jsonify({'message': 'task updated successfully'})
        except:
            return jsonify({'error': 'There was an issue updating your task'})

    else:
        task_contant_to_update = todoSchema.dump(task)
        return jsonify(task_contant_to_update)

if __name__ == "__main__":
    app.run(debug=True)
