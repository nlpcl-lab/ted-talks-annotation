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
    username = request.args.get('username')
    try:
        user = User.objects.get(username=username)
        g.user = user
        session['username'] = username
    except User.DoesNotExist:
        pass

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


@is_user
def view_annotate_tension_v2(doc_id):
    username = request.args.get('username')
    try:
        user = User.objects.get(username=username)
        g.user = user
        session['username'] = username
    except User.DoesNotExist:
        pass

    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        try:
            annotation = Annotation.objects.get(user=g.user, sent=sent, type=Annotation.TYPE_TENSION_V2)
            sent.label = annotation.basket['tension']
        except Annotation.DoesNotExist:
            sent.label = ''

    doc.sent_total = sents.count()
    return render_template('annotate_tension_v2.html', doc=doc, sents=sents, g=g)


@is_user
def view_annotate_tension_v3(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        try:
            annotation = Annotation.objects.get(user=g.user, sent=sent, type=Annotation.TYPE_TENSION_V3)
            sent.label = annotation.basket['tension']
        except Annotation.DoesNotExist:
            sent.label = ''

    doc.sent_total = sents.count()
    return render_template('annotate_tension_v3.html', doc=doc, sents=sents, g=g)


@is_user
def view_annotate_tension_v4(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        try:
            annotation = Annotation.objects.get(user=g.user, sent=sent, type=Annotation.TYPE_TENSION_V4)
            sent.label = annotation.basket['tension']

            try:
                down = float(annotation.basket.get('auto_down', 0))
                similar = float(annotation.basket.get('auto_similar', 0))
                up = float(annotation.basket.get('auto_up', 0))
            except ValueError:
                down = 0
                similar = 0
                up = 0

            sent.auto_down = down
            sent.auto_similar = similar
            sent.auto_up = up

            if up > down and up > similar:
                sent.auto_label = 1
            elif down > up and down > similar:
                sent.auto_label = -1
            else:
                sent.auto_label = 0

        except Annotation.DoesNotExist:
            sent.label = ''
            sent.auto_down = ''
            sent.auto_similar = ''
            sent.auto_up = ''
            sent.auto_label = ''

    doc.sent_total = sents.count()
    return render_template('annotate_tension_v4.html', doc=doc, sents=sents, g=g)


@is_user
def view_annotate_role(doc_id):
    username = request.args.get('username')
    try:
        user = User.objects.get(username=username)
        g.user = user
        session['username'] = username
    except User.DoesNotExist:
        pass

    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        try:
            # 동일한 주석이 두 개 생긴경우가 발생해서 대처함 (왜 같은 문장에 두개가 주석되는지 조사해봐야함)
            # annotations = Annotation.objects.filter(user=g.user, sent=sent, type=Annotation.TYPE_ROLE)
            # if annotations.count() >= 2:
            #     for annotation in annotations[1:]:
            #         annotation.delete()
            annotation = Annotation.objects.get(user=g.user, sent=sent, type=Annotation.TYPE_ROLE)
            sent.label = annotation.basket['role']
        except Annotation.DoesNotExist:
            sent.label = ''

    doc.sent_total = sents.count()
    return render_template('annotate_role.html', doc=doc, sents=sents, g=g)


@is_user
def view_compare_tension(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects.filter(doc=doc).order_by('index')
    for sent in sents:
        annotations = Annotation.objects.filter(sent=sent, type=Annotation.TYPE_TENSION)
        sent.annotations = []
        for annotation in annotations:
            if annotation.user:
                sent.annotations.append('{}: {}'.format(annotation.user.username, annotation.basket['tension']))

    doc.sent_total = sents.count()
    return render_template('compare.html', doc=doc, sents=sents, g=g)


@is_user
def view_youtube_practice():
    return render_template('youtube_practice.html', g=g)


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
    sent = Sent.objects.get(id=sent_id)

    try:
        annotation = Annotation.objects.get(sent=sent, user=g.user, type=Annotation.TYPE_TENSION)
    except Annotation.DoesNotExist:
        annotation = Annotation(
            sent=sent,
            doc=sent.doc,
            user=g.user,
            type=Annotation.TYPE_TENSION)
    annotation.basket['tension'] = label
    annotation.save()

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=sent.doc, user=g.user, type=Annotation.TYPE_TENSION).count(),
        'sent_total': Sent.objects.filter(doc=sent.doc).count(),
    })


@is_user
def api_annotate_tension_v2(sent_id):
    data = request.get_json()

    label = data['label']
    sent = Sent.objects.get(id=sent_id)

    type = Annotation.TYPE_TENSION_V2

    try:
        annotation = Annotation.objects.get(sent=sent, user=g.user, type=type)
    except Annotation.DoesNotExist:
        annotation = Annotation(
            sent=sent,
            doc=sent.doc,
            user=g.user,
            type=type)
    annotation.basket['tension'] = label
    annotation.save()

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=sent.doc, user=g.user, type=type).count(),
        'sent_total': Sent.objects.filter(doc=sent.doc).count(),
    })


@is_user
def api_annotate_tension_v3(sent_id):
    data = request.get_json()

    label = data['label']
    focus_started_at = data['focus_started_at']
    input_viewed_at = data['input_viewed_at']
    local_updated_at = data['local_updated_at']
    sent = Sent.objects.get(id=sent_id)

    type = Annotation.TYPE_TENSION_V3

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


@is_user
def api_annotate_tension_v4(sent_id):
    data = request.get_json()

    label = data['label']
    auto_down = data['auto_down']
    auto_similar = data['auto_similar']
    auto_up = data['auto_up']
    focus_started_at = data['focus_started_at']
    input_viewed_at = data['input_viewed_at']
    local_updated_at = data['local_updated_at']
    sent = Sent.objects.get(id=sent_id)

    try:
        auto_down = float(auto_down)
        auto_similar = float(auto_similar)
        auto_up = float(auto_up)
    except ValueError:
        auto_down = 0
        auto_similar = 0
        auto_up = 0

    type = Annotation.TYPE_TENSION_V4

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
    annotation.basket['auto_down'] = auto_down
    annotation.basket['auto_similar'] = auto_similar
    annotation.basket['auto_up'] = auto_up
    annotation.updated_at = datetime.now()
    annotation.save()

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=sent.doc, user=g.user, type=type).count(),
        'sent_total': Sent.objects.filter(doc=sent.doc).count(),
    })


@is_user
def api_annotate_tension_v3_stat(doc_id):
    doc = Doc.objects.get(id=doc_id)
    type = Annotation.TYPE_TENSION_V3

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=doc, user=g.user, type=type).count(),
        'sent_total': Sent.objects.filter(doc=doc).count(),
    })


@is_user
def api_annotate_tension_v4_stat(doc_id):
    doc = Doc.objects.get(id=doc_id)
    type = Annotation.TYPE_TENSION_V4

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=doc, user=g.user, type=type).count(),
        'sent_total': Sent.objects.filter(doc=doc).count(),
    })


@is_user
def api_annotate_role(sent_id):
    data = request.get_json()

    label = data['label']
    sent = Sent.objects.get(id=sent_id)

    try:
        annotation = Annotation.objects.get(sent=sent, user=g.user, type=Annotation.TYPE_ROLE)
    except Annotation.DoesNotExist:
        annotation = Annotation(
            sent=sent,
            doc=sent.doc,
            user=g.user,
            type=Annotation.TYPE_ROLE)
    annotation.basket['role'] = label
    annotation.save()

    return json.dumps({
        'label_total': Annotation.objects.filter(doc=sent.doc, user=g.user, type=Annotation.TYPE_ROLE).count(),
        'sent_total': Sent.objects.filter(doc=sent.doc).count(),
    })
