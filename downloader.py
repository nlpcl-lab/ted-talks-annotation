import os
from tqdm import tqdm
import subprocess
import pysrt
import csv

from mongoengine import connect

from config import Config
from annotation.models import Doc, Sent


def download_video_from_youtube(title, source):
    print('[download_video_from_youtube] start:', source)
    filename = title.replace(' ', '_')

    if Doc.objects.filter(title=title).count():
        doc = Doc.objects.get(title=title, source=source)
    else:
        doc = Doc(title=title, source=source)
        doc.save()

    subprocess.call(['youtube-dl',
                     # for sub
                     '--sub-lang', 'en',
                     '--write-sub',
                     '--convert-subs', 'srt',
                     # for audio
                     '--extract-audio',
                     '--audio-format', 'mp3',
                     # for filename
                     '--output', './data/videos/{}.%(ext)s'.format(filename),
                     source,
                     ])

    prefix_path = os.path.abspath(os.path.dirname(__file__) + './data/videos/{}'.format(filename))
    subs = align_subtitles(prefix_path)
    for index, sub in enumerate(subs):
        if Sent.objects.filter(doc=doc, index=index + 1).count():
            continue
        sent = Sent(
            doc=doc,
            index=index + 1,
            text=sub.eng_text,
            start_ts=sub.start.ordinal,
            end_ts=sub.end.ordinal)
        sent.save()

    print('[download_video_from_youtube] finish')


class Subtitle:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.eng_text = ''
        self.kor_text = ''


def clean_text(text):
    return text.strip().replace('\n', ' ')


def align_subtitles(srt_path):
    eng_subs = pysrt.open(srt_path + '.en.srt')

    subs = []
    start = 0
    text = ''
    for eng_sub in eng_subs:
        text += ' ' + clean_text(eng_sub.text)
        if start == 0:
            start = eng_sub.start
        if text[-1] in ['.', ':', '-', '"', ')', '?', '!', ';']:
            sub = Subtitle()
            sub.eng_text = clean_text(text)
            sub.start = start
            sub.end = eng_sub.end
            subs.append(sub)
            text = ''
            start = 0

    return subs


if __name__ == '__main__':
    connect(**Config.MONGODB_SETTINGS)

    if not os.path.exists('./data/videos'):
        os.mkdir('./data/videos')

    with open('./data/video_list.csv') as f:
        reader = csv.DictReader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for line in tqdm(reader):
            title, url = line['title'].strip(), line['url'].strip()
            download_video_from_youtube(title, url)
