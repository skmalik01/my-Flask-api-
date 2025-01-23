from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = [{
    'id' : 1,
    'name' : 'malik',
    'city' : 'mumbai',
}]
task_id = 1

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id
    data=request.json
    task = {
        'id' : 'task_id',
        'name' : data['name'],
        'city' : data['city']
    }
    tasks.append(task)
    task_id += 1
    return jsonify(task), 201
@app.route('/')
def show():
    return 'Your data'
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=["GET"])
def get_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            return jsonify(task)
    return jsonify({"message": "Task Not Found"})

@app.route('/tasks')
def update_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['name'] = request.json.get('name', task['name'])
            task['city'] = request.json.get('city', task['city'])
            return jsonify(task)
    return jsonify({"message" : "Task Not Found"})

if __name__ == '__main__':
    app.run(debug=True)