import MySQLdb
from flask import Flask, json,request,jsonify,Response
from flask_mysqldb import MySQL
from werkzeug.datastructures import HeaderSet
import yaml
from datetime import datetime

app = Flask(__name__)

# Configuration db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST']= db['mysql_host']
app.config['MYSQL_USER']= db['mysql_user']
app.config['MYSQL_PASSWORD']= db['mysql_password']
app.config['MYSQL_DB']= db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    cur = mysql.connection.cursor()
    cur.execute("select * from todo")
    all_tasks = cur.fetchall()
    row_header = [decription[0] for decription in cur.description]
    cur.close()
    if not all_tasks:
        return jsonify({'error' : 'No tasks available'}),404
    else:
        return jsonify(toJsonFormat(row_header,all_tasks)),200

@app.route('/add', methods=['Post'])
def add():
    task_content = request.get_json()
    if task_content['content'] == '':
        return jsonify({'error': 'content should not be empty'}),400
    else:          
        todo_content = task_content['content']
        try:
            datenow = datetime.now().date()
            cur = mysql.connection.cursor()
            cur.execute("INSERT into todo(content, date_created) values(%s,%s)",(todo_content,datenow))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'Successfully task added'}),200
        except(MySQLdb.Error, MySQLdb.Warning) as sqlError:
            print(sqlError)
            return jsonify({'error' : 'There was an issue adding your task',
                            'message': sqlError})


@app.route('/delete/<task_id>',methods=['GET'])
def delete(task_id):
    try:
        cur = mysql.connection.cursor()
        if(cur.execute("select * from todo where id=(%s)",(task_id))):
            cur.execute("delete from todo where id=(%s)",(task_id))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'task deleted successfully'}),200
        else:
            return jsonify({'error':'no data present with task id'}),404
    except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
        print(sqlError)
        return Response({'error': 'There was a problem deleting that task...plz retry',
                        'message': sqlError})

@app.route('/update/<task_id>', methods=['GET', 'POST'])
def update(task_id):
    if request.method == 'POST':
        task_content = request.get_json()
        content = task_content['content']
        try:
            cur = mysql.connection.cursor()
            if(cur.execute("select * from todo where id=(%s)",(task_id))):
                cur.execute("update todo set content=(%s) where id=(%s)",(content,task_id))
                mysql.connection.commit()
                cur.close()
                return jsonify({'message': 'task updated successfully'}),200
            else:
                return jsonify({'error' : 'no data present with task that id'}),404
        except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
            return jsonify({'error': 'There was an issue updating your task','message': sqlError})
    else:
        try:
            cur = mysql.connection.cursor()
            if(cur.execute("select * from todo where id=(%s)",(task_id))):
                cur.execute("select * from todo where id=(%s)",(task_id))
                sql_data = cur.fetchall()
                row_header = [decription[0] for decription in cur.description]
                mysql.connection.commit()
                cur.close()
                return jsonify(toJsonFormat(row_header,sql_data)),200
            else:
                return jsonify({'error' : 'no data present with task that id'}),404
        except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
            return jsonify({'error': 'There was an issue updating your task','message': sqlError})

def toJsonFormat(row_header,sql_data):
    json_data=[]
    for row in sql_data:
        json_data.append(dict(zip(row_header,row)))
    return json_data

if __name__ == "__main__":
    app.run(debug=True)
