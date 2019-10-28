# ted-talks-annotation

Code and data for a paper "Computer Assisted Annotation of Tension Development in TED Talks through Crowdsourcing" 

## Annotation Tool

<img src="https://github.com/nlpcl-lab/ted-talks-annotation/raw/master/annotation/static/img/interface.jpg" width="600px">

### Pre-requisites

1. Install and run [Mongodb](https://www.mongodb.com/).
    - It is easy to install and run.

### Setup 

1. To connect the Mongodb, make your own config.py: `cp config.smaple.py config.py`
    - If the default setting of the Mongodb has not been changed, you don't need to modify the config.py
    
2. Install python requirements: `pip install -r requirements.txt`

3. Download TED talks videos on the data/video_list: `python downloader.py`

4. Run the web-based annotation tool: `export PYTHONPATH=.;python annotation/app.py`

5. Annotate! 😵

    

