import os, sys, datetime, random
from flask import Flask, session, g, request, render_template, redirect
from flask_mongoengine import MongoEngine

import annotation.views as views
from annotation.models import User

base_dir = os.path.abspath(os.path.dirname(__file__) + '/')
sys.path.append(base_dir)

app = Flask(__name__)

app.config.from_object('config.Config')
db = MongoEngine(app)


@app.before_request
def before_request():
    g.random = random.randrange(1, 10000)
    if 'username' not in session:
        g.user = None
    else:
        user = User.objects.get(username=session['username'])
        user.accessed_at = datetime.datetime.now
        user.last_ip = request.remote_addr
        user.save()
        g.user = user


app.add_url_rule('/', view_func=views.view_index, methods=['GET'])
app.add_url_rule('/login', view_func=views.view_login, methods=['GET'])
app.add_url_rule('/logout', view_func=views.view_logout, methods=['GET'])
app.add_url_rule('/annotate/<doc_id>/tension', view_func=views.view_annotate_tension, methods=['GET'])
app.add_url_rule('/api/login', view_func=views.api_login, methods=['POST'])
app.add_url_rule('/api/annotate/sent/<sent_id>/tension', view_func=views.api_annotate_tension, methods=['POST'])

if __name__ == '__main__':
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8080)
