from flask import Flask, render_template
app = Flask(__name__)
posts = [
    {
        'author' : 'Shaikh Malik',
        'title' : 'Blog Post 1',
        'content' : 'First post content',
        'date_post' : 'April 04 2020'
    },
    {
        'author' : 'Shaikh Alam',
        'title' : 'Blog Post 2',
        'content' : 'Second post content',
        'date_post' : 'April 05 2021'
    }
]
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)