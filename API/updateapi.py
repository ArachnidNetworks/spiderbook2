#!/usr/bin/env python
import dbint


def pd(d: dict):
    print('{\n  ' + str(d).replace("', '", "',\n  '")[1:][:-1] + '\n}')


class APImgr:
    def __init__(self, db: dbint.DBInterface):
        self.db = db

    def __add_reply(self, uid: str, reply_uid: str, parent_type: str) -> bool:
        table = "posts" if parent_type == "post" else "replies"
        try:
            # Update table with new reply_uid
            self.db.update({
                "table": table,
                "restriction": f"WHERE uid = '{uid}'",
                "reply_uids": f"reply_uids || '{reply_uid}'::VARCHAR(32)"
            })
            print(uid, ":", reply_uid)
        except IndexError:
            return False
        return True

    def add(self, form_data: dict, parent_type: str) -> bool:
        uid = db.new_uid(32)
        data = {"uid": uid, "ip": "example_ip_address", "dt": dbint.dt_now(), "reply_uids": []}
        # Set correct title size
        if form_data.get("title"):
            data["title"] = form_data["title"][:200]
        # Set correct parent and body size
        data["parent"] = form_data["parent"][:1000]
        data["body"] = form_data["body"][:1000]
        # Get correct table and run required adjustments
        if parent_type == "category":
            data["table"] = "posts"
        elif parent_type == "post" or parent_type == "reply":
            data["table"] = "replies"
            self.__add_reply(data['parent'], uid, parent_type)
        else:
            return False
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
    post_uid = "19807548e119cb1ad2ca34aeb731bbe5"
    form_data = {"parent": post_uid, "body": "example_body"}
    post_uid = "14c4f11412d95be4aa44597ceb462a81"
    form_data = {"parent": post_uid, "body": "example_body"}
    api.add(form_data, 'reply')

# IP: request.environ['REMOTE_ADDR'][:45]
