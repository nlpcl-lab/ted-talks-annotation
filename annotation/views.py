import json, math, datetime, os
from flask import request, render_template, Response, g, session, redirect, send_file, make_response
from flask_mongoengine import Pagination
from bson import json_util
from datetime import datetime

from annotation.decorator import is_user

from annotation.models import Doc, User, Sent, Annotation


@is_user
def view_index():
    docs = Doc.objects.all().order_by('id')
    return render_template('index.html', docs=docs, g=g)


def view_login():
    callback = request.args.get('callback', '/')
    return render_template('login.html', g=g, callback=callback)


@is_user
def view_logout():
    callback = request.args.get('callback', '/')
    if 'username' in session:
        del session['username']
    return render_template('login.html', g=g, callback=callback)


@is_user
def view_annotate_tension(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        try:
            annotation = Annotation.objects.get(user=g.user, sent=sent, type=Annotation.TYPE_TENSION)
            sent.label = annotation.basket['tension']
        except Annotation.DoesNotExist:
            sent.label = ''

    doc.sent_total = sents.count()
    return render_template('annotate_tension.html', doc=doc, sents=sents, g=g)


def api_login():
    data = request.get_json()
    turker_id = data['turker_id']

    if User.objects.filter(turker_id=turker_id).count():
        user = User.objects.get(turker_id=turker_id)
    else:
        user = User(username=turker_id, turker_id=turker_id)
        user.save()

    session['username'] = user.username
    g.user = user
    return Response('success', status=200)


@is_user
def api_annotate_tension(sent_id):
    data = request.get_json()

    label = data['label']
    focus_started_at = data['focus_started_at']
    input_viewed_at = data['input_viewed_at']
    local_updated_at = data['local_updated_at']
    sent = Sent.objects.get(id=sent_id)

    type = Annotation.TYPE_TENSION
    try:
        annotation = Annotation.objects.get(sent=sent, user=g.user, type=type)
    except Annotation.DoesNotExist:
        annotation = Annotation(
            sent=sent,
            doc=sent.doc,
            user=g.user,
            first_focus_started_at=datetime.fromtimestamp(focus_started_at / 1000),
            first_input_viewed_at=datetime.fromtimestamp(input_viewed_at / 1000),
            first_updated_at=datetime.fromtimestamp(local_updated_at / 1000),
            type=type)

    annotation.basket['tension'] = label
    annotation.updated_at = datetime.now()
    annotation.save()

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=sent.doc, user=g.user, type=type).count(),
        'sent_total': Sent.objects.filter(doc=sent.doc).count(),
    })
