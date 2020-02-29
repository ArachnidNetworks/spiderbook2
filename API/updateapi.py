#!/usr/bin/env python
import dbint


def pd(d: dict):
    for k, v in d.items():
        print(str(k) + ": " + str(v))


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
        except IndexError:
            return False
        return True

    def add(self, form_data: dict, ip: str, parent_type: str) -> bool:
        uid = db.new_uid(32)
        data = {"uid": uid, "ip": ip, "dt": dbint.dt_now(), "reply_uids": []}
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
        self.db.delete({"table": self.__get_correct_table(dtype), "restriction": f"WHERE uid = '{uid}'"})

    def edit(self, uid, new_content) -> None:
        pass

    def get(self, uid, dtype) -> dict:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE uid = '{uid}'")

    def getn(self, n, dtype) -> tuple:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"ORDER BY dt DESC LIMIT {n}")

    def getn_by_parent(self, n, parent) -> tuple:
        pass

    def __get_correct_table(self, dtype: str) -> str:
        if dtype == "post":
            table = "posts"
        elif dtype == "reply":
            table = "replies"
        elif dtype == "superuser":
            table = "superusers"
        return table


if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr(db)
    uid = "6b93ea6dba952725a35ba2f2e27cf493"
    result = api.getn(2, 'post')
    print('-'*40)
    for row in result:
        pd(row)
        print('-'*40)
    # form_data = {"title": "example_title", "parent": "example_category", "body": "example_body"}
    # api.add(form_data, 'example_ip_address', 'category')
    # if uid and len(uid) > 0:
    #     form_data = {"parent": uid, "body": "example_body"}
    #     api.add(form_data, 'example_ip_address', 'post')
    #     api.add(form_data, 'example_ip_address', 'reply')

# IP: request.environ['REMOTE_ADDR'][:45]
