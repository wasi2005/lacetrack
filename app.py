from flask import Flask, render_template

app = Flask(__name__)

# When someone goes to lace-track.herokuapp.com/ --> index() gets executed
@app.route('/')
def index():
    return render_template("index.html")

# When someone goes to lace-track.herokuapp.com/greeting/Wasi --> greeting gets executed()
@app.route('/greeting/<name>')
def greeting(name):
    return 'Hi, ' + name + '!'

if __name__ == "__main__":
    app.run()
