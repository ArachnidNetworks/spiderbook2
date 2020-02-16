#!/usr/bin/env python
import dbint

# General data extractor

def get_data(request, extra: dict, required: list):
    data = dict()

    # Add new keys
    for new_key, new_value in extra.items():
        data[new_key] = new_value

    # Extract required keys
    for required_key in required:
        required_value = request.form[required_key]
        data[required_key] = required_value

    return data

# Connnect to database
db = dbint.DBInterface("spiderbook", "postgres", "postgres")

def add_post(request):
    """ Adds a post """
    extra = {'table': 'posts', 'uid': db.new_uid(32), 'ip': request.environ['REMOTE_ADDR'][:45], 'dt': dbint.dt_now()}
    required = ['body_text', 'body_file', 'title', 'category']
    get_data(request, extra, required)
    if required.get('body_text'):
        required['body_text'] = required['body_text'][:1000]
    print(get_data)

