from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    done = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f"<Task {self.name}>"
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods = ['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_name = request.form['task_name']
        new_task = Task(name=task_name)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/done/<int:task_id>')
def mark_done(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)

