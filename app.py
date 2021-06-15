from datetime import datetime
from util.format import Format
import yaml
import MySQLdb
from flask import Flask, json,request,jsonify,Response
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from contextlib import contextmanager

app = Flask(__name__)
format_obj = Format()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Configuration db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST']= db['mysql_host']
app.config['MYSQL_USER']= db['mysql_user']
app.config['MYSQL_PASSWORD']= db['mysql_password']
app.config['MYSQL_DB']= db['mysql_db']

#for docker
# app.config['MYSQL_HOST']= 'localhost'
# app.config['MYSQL_USER']= 'root'
# app.config['MYSQL_PASSWORD']='udayb@123'
# app.config['MYSQL_ROOT_PASSWORD']='udayb@123'
# app.config['MYSQL_DATABASE']= 'flaskapp'
# app.config['port']= '3306'

# def getMysqlConnection():
#     return mysql.connector.connect(user='root', host='db', port='3306', password='root', database='flaskapp')

# config = {
#     'user': 'root',
#     'password': 'root',
#     'host': 'db',
#     'port': '3306',
#     'database': 'flaskapp'
# }

mysql = MySQL(app)
# connection = mysql.connector.connect(**config)

@contextmanager
def my_database():
    try:
        # cur = getMysqlConnection()
        # cur = connection.cursor(dictionary=True)
        cur = mysql.connection.cursor()
        yield cur
    finally:
        mysql.connection.commit()
        cur.close()

@app.route('/')
@cross_origin()
def index():
    return jsonify({'message': 'helth check'}),200

@app.route('/alltasks', methods=['GET'])
@cross_origin()
def all_tasks():
    with my_database() as cur:
        sql = "select * from todo"
        cur.execute(sql)
        all_tasks = cur.fetchall()
    row_header = [decription[0] for decription in cur.description]
    if not all_tasks:
        return jsonify({'error' : 'No tasks available'}),404
    else:
        tasks = format_obj.toJsonFormat(row_header,all_tasks)
        return jsonify(tasks),200

@app.route('/task/<task_id>')
@cross_origin()
def task(task_id):
    try:
        sql = "select * from todo where id=(%s)"
        with my_database() as cur:
            if(cur.execute(sql,(task_id,))):
                cur.execute(sql,(task_id,))
                sql_data = cur.fetchall()
                row_header = [decription[0] for decription in cur.description]
                return jsonify(format_obj.toJsonFormat(row_header,sql_data)),200
            else:
                return jsonify({'error' : 'no data present with task that id'}),404
    except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
        return jsonify({'error': 'There was an issue updating your task','message': sqlError}),500

@app.route('/add', methods=['POST'])
@cross_origin()
def add():
    task_content = request.get_json()
    todo_content = task_content['content']
    if not task_content:
        return jsonify({'error': 'content should not be empty'}),400
    else:          
        try:
            datenow = datetime.now().date()
            sql = "INSERT into todo(content, date_created) values(%s,%s)"
            with my_database() as cur:
                cur.execute(sql,(todo_content,datenow,))
                return jsonify({'message': 'Successfully task added'}),200
        except(MySQLdb.Error, MySQLdb.Warning) as sqlError:
            print(sqlError)
            return jsonify({'error' : 'There was an issue adding your task',
                            'message': sqlError}),500


@app.route('/delete/<task_id>',methods=['DELETE'])
@cross_origin()
def delete(task_id):
    try:
        with my_database() as cur:
            sql_id_exists = "select * from todo where id=(%s)"
            if(cur.execute(sql_id_exists,(task_id,))):
                sql_id_delete = "delete from todo where id=(%s)"
                cur.execute(sql_id_delete,(task_id,))
                return jsonify({'message': 'task deleted successfully'}),200
            else:
                return jsonify({'error':'no data present with task id'}),404
    except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
        print(sqlError)
        return Response({'error': 'There was a problem deleting that task...please retry',
                        'message': sqlError}),500

@app.route('/update/<task_id>', methods=['PUT'])
@cross_origin()
def update(task_id):
    task_content = request.get_json()
    content = task_content['content']
    if not content:
        return jsonify({'error': 'content should not be empty'}),400
    else:
        try:
            with my_database() as cur:
                sql_id_exists = "select * from todo where id=(%s)"
                if(cur.execute(sql_id_exists,(task_id,))):
                    sql_update = "update todo set content=(%s) where id=(%s)"
                    cur.execute(sql_update,(content,task_id,))
                    return jsonify({'message': 'task updated successfully'}),200
                else:
                    return jsonify({'error' : 'no data present with task that id'}),404
        except(MySQLdb.Error, MySQLdb.Warning)as sqlError:
            return jsonify({'error': 'There was an issue updating your task','message': sqlError}),500

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
