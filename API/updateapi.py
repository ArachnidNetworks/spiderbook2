#!/usr/bin/env python
import dbint


def pd(d: dict):
    print('{\n  ' + str(d).replace("', '", "',\n  '")[1:][:-1] + '\n}')


class APImgr:
    def __init__(self, db: dbint.DBInterface):
        self.db = db

    def add(self, form_data: dict, parent_type: str) -> dict:
        data = {"uid": db.new_uid(32), "ip": "example_ip_address", "dt": dbint.dt_now(), "reply_uids": []}
        if parent_type == "category":
            data["table"] = "posts"
        elif parent_type == "post_or_reply":
            data["table"] = "replies"
        else:
            return False
        # Set correct title size
        if form_data.get("title"):
            data["title"] = form_data["title"][:200]
        # Set correct parent and body size
        data["parent"] = form_data["parent"][:1000]
        data["body"] = form_data["body"][:1000]
        # Get correct table
        return self.db.insert(data)

    def delete(self, uid: str, dtype: str) -> None:
        if dtype == "post":
            table = "posts"
        elif dtype == "reply":
            table = "replies"
        elif dtype == "superuser":
            table = "superusers"
        self.db.delete({"table": table, "restriction": f"WHERE uid = '{uid}'"})

    def edit(self, uid, new_content) -> None:
        pass

    def get(self, uid) -> dict:
        pass

    def getn(self, n) -> tuple:
        pass

    def getn_by_parent(self, n, parent) -> tuple:
        pass

    def add_reply(self, original_uid, reply_uid) -> tuple:
        pass


if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr(db)
    form_data = {"title": "example_title", "parent": "example_category", "body": "example_body"}
    api.add(form_data, 'category')
    form_data = {"parent": "example_post_uid", "body": "example_body"}
    api.add(form_data, 'post_or_reply')

    api.delete('d64ca426320970cec9fc34c82039df68', 'reply')

# IP: request.environ['REMOTE_ADDR'][:45]
