# ted-talks-annotation

Code and data for a paper "Computer Assisted Annotation of Tension Development in TED Talks through Crowdsourcing" 

## Annotation Tool

An annotation tool used in the paper to annotate the tension development.

<img src="https://github.com/nlpcl-lab/ted-talks-annotation/raw/master/annotation/static/img/interface.jpg" width="600px">

### Pre-requisites

1. Install and run [Mongodb](https://www.mongodb.com/).

### Setup 

1. To connect the Mongodb, make your own config.py: `cp config.sample.py config.py`
    - If the default setting of the Mongodb has not been changed, you don't need to modify the config.py
    
2. Install python requirements: `pip install -r requirements.txt`

3. Download TED talks videos on the data/video_list: `python downloader.py`

4. Run the web-based annotation tool: `export PYTHONPATH=.;python annotation/app.py`

5. Annotate! 😵
    - We provided the annotators with [this guideline document](https://github.com/nlpcl-lab/ted-talks-annotation/blob/master/guideline_for_annotator.pdf) when using [Amazon Mechanical Turk](https://www.mturk.com).

    

