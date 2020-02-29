#!/usr/bin/env python
import dbint

SUPERUSER_ADM = 1
SUPERUSER_MOD = 2


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
        uid = self.db.new_uid(32)
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
            return self.__add_reply(data['parent'], uid, parent_type)
        else:
            return False
        return self.db.insert(data)

    def delete(self, uid: str, dtype: str) -> bool:
        return self.db.delete({"table": self.__get_correct_table(dtype), "restriction": f"WHERE uid = '{uid}'"})

    def edit(self, uid: str, dtype: str, new_body: str) -> bool:
        return self.db.update({
            "table": self.__get_correct_table(dtype),
            "restriction": f"WHERE uid = '{uid}'",
            "body": "'" + new_body + "'"
            })

    def get(self, uid: str, dtype: str) -> dict:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE uid = '{uid}'")[0]

    def getn(self, n: int, dtype: str) -> tuple:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"ORDER BY dt DESC LIMIT {n}")

    def getn_by_parent(self, n: int, dtype: str, parent: str) -> tuple:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE parent = '{parent}' ORDER BY dt DESC LIMIT {n}")

    def __get_correct_table(self, dtype: str) -> str:
        if dtype == "post":
            table = "posts"
        elif dtype == "reply":
            table = "replies"
        return table

    def superuser_add(self, data: dict) -> bool:
        su_type = None
        if data['su_type'] == 'ADMIN':
            su_type = SUPERUSER_ADM
        elif data['su_type'][:3] == 'MOD':
            su_type = SUPERUSER_MOD
        if su_type is not None:
            return self.db.insert({
                'table': 'superusers',
                'su_id': self.db.new_uid(32),
                'su_type': su_type,
                'email': data['email'],
                'password': dbint.secure_hash(data['password'], 32),
                'accepted': False
            })
        return False

    def superuser_accept(self, su_id: str) -> bool:
        return self.db.update({
            "table": "superusers",
            "accepted": True,
            "restriction": f"WHERE su_id = '{su_id}'"
        })
        return False

    def superuser_verify(self, data: dict) -> bool:
        password = dbint.secure_hash(data['password'], 32)
        if len(self.db.select({
            "table": "superusers",
            "cols": ["su_id"]
        }, f"WHERE email = '{data['email']}' AND password = '{password}'")) > 0:
            return True
        return False

if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr(db)
    su_data = {"su_type": "MOD", "email": "mod@service.example", "password": "hello123"}
    result = api.superuser_verify({"email": "mod@service.example", "password": "hello123"})
    if len(result) == 1:
        print("Found", result[0])
    # uid = ""
    # form_data = {"title": "; DELETE FROM posts *", "parent": "example_category", "body": "example_body"}
    # api.add(form_data, 'example_ip_address', 'category')
    # if uid and len(uid) > 0:
    #     form_data = {"parent": uid, "body": "example_body"}
    #     api.add(form_data, 'example_ip_address', 'post')
    #     api.add(form_data, 'example_ip_address', 'reply')
    # print('-'*40)
    # for row in result:
    #     pd(row)
    #     print('-'*40)

# IP: request.environ['REMOTE_ADDR'][:45]
