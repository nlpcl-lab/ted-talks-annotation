import os
import json
import argparse
from tqdm import tqdm
import pickle
from bson import json_util
from mongoengine import connect

from annotation.models import Doc, User, Sent, Annotation
import config as config


def export_data(annotation_type):
    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/output/')
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    data_path = os.path.join(output_path, '{}.json'.format(annotation_type))
    docs = Doc.objects.all()
    data = []
    for doc in tqdm(docs):
        sents = Sent.objects.filter(doc=doc).order_by('index')
        for sent in sents:
            annotations = Annotation.objects.filter(sent=sent, type=annotation_type)
            labels = []
            for annotation in annotations:
                label = annotation.basket['tension']
                labels.append(label)

            data.append({
                'doc_id': str(doc.id),
                'doc_title': doc.title,
                'source': doc.source,
                'sent_id': str(sent.id),
                'sent_index': sent.index,
                'text': sent.text,
                'labels': labels,
                'start_ts': sent.start_ts,
                'end_ts': sent.end_ts,
            })

    data_json = json.dumps(data, default=json_util.default, ensure_ascii=False, indent=2)
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_json)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=str, default='export_data')

    arg = parser.parse_args()
    if arg.run == 'export_data':
        export_data(annotation_type=Annotation.TYPE_TENSION)
    else:
        parser.print_help()
