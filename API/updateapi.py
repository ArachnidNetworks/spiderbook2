#!/usr/bin/env python
import dbint

def pd(d: dict):
    print('{\n  ' + str(d).replace("', '", "',\n  '")[1:][:-1] + '\n}')

def extract_data(form_data, extra: dict, required: list):
    """ Extracts data from a request object and adds elements from the arguments 'extra' and 'required'. """
    data = dict()

    # Add new keys
    data = form_data

    # Extract required keys
    for required_key in required:
        required_value = form_data.get(required_key)
        data[required_key] = required_value

    return data

class APImgr:
    def __init__(self, db: dbint.DBInterface):
        self.db = db

    def add(self, form_data: dict, extra: dict):
        extra = {'table': 'posts', 'uid': db.new_uid(32), 'ip': request.environ['REMOTE_ADDR'][:45], 'dt': dbint.dt_now()}
        required = ['body_text', 'body_file', 'title', 'category']
        data = extract_data(form_data, extra, required)
        if data.get('body_text'):
            data['body_text'] = data['body_text'][:1000]
        db.insert(data)

    def delete(self, uid):
        pass
    def edit(self, uid, new_content):
        pass
    def get(self, uid):
        pass
    def getn(self, n):
        pass
    def getn_by_parent(self, n, parent):
        pass
    def add_reply(self, original_uid, reply_uid):
        pass

if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr()
    api.add({'title': 'example_title', 'category': 'example_category', 'body_text': 'example_body'})

