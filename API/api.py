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

    def add(self, form_data: dict, ip: str, parent_type: str) -> bool:
        """Adds a new row to a specified table.
        :param form_data: The data in dictionary format, with each key being a column
        :type form_data: dict
        :param ip: OP's IP address.
        :type ip: str
        :param dtype: The post's type (determines the table)
        :type dtype: str
        :returns: a boolean determining if the operation succeeded of failed."""

        uid = self.db.new_uid(32)
        if not self.__check_banned(ip):
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
                return self.__add_reply(data['parent'], uid, self.__esc(parent_type))
            else:
                return False
            return self.db.insert(data)
        return False

    def __add_reply(self, uid: str, reply_uid: str, parent_type: str) -> bool:
        try:
            # Update table with new reply_uid
            self.db.update({
                "table": self.__get_correct_table(parent_type),
                "restriction": f"WHERE uid = '{uid}'",
                "reply_uids": f"reply_uids || '{self.__esc(reply_uid)}'::VARCHAR(32)"
            })
        except IndexError:
            return False
        return True

    def __check_banned(self, ip: str) -> bool:
        sel = self.db.select({'table': 'banned'}, f"WHERE ip = '{ip}'")
        if sel and sel[0]['dt'] < dbint.dt_now():
            self.db.delete({
                'table': 'banned',
                'restriction': f'WHERE ip = \'{ip}\' AND dt = \'{sel[0]["dt"]}\''
            })
            return False
        return len(sel) > 0

    def delete(self, uid: str, dtype: str) -> bool:
        # removes self from parent's reply list if it's a reply
        if dtype == "reply":
            self.__delete_from_parent(uid, dtype)
        # delete self replies
        for ruid in self.db.select({'table': self.__get_correct_table(dtype), 'cols': ['reply_uids']}, f"WHERE uid = '{uid}'")[0]['reply_uids']:
            self.delete(ruid, 'reply')
        # delete self
        return self.db.delete({"table": self.__get_correct_table(dtype), "restriction": f"WHERE uid = '{uid}'"})

    def edit(self, uid: str, dtype: str, new_body: str) -> bool:
        return self.db.update({
            "table": self.__get_correct_table(dtype),
            "restriction": f"WHERE uid = '{self.__esc(uid)}'",
            "body": "'" + self.__esc(new_body) + "'"
            })

    def get(self, uid: str, dtype: str) -> dict:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE uid = '{self.__esc(uid)}'")[0]

    def getn(self, n: int, dtype: str) -> tuple:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"ORDER BY dt DESC LIMIT {n}")

    def getn_by_parent(self, n: int, dtype: str, parent: str) -> tuple:
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE parent = '{self.__esc(parent)}' ORDER BY dt DESC LIMIT {n}")

    def __get_correct_table(self, dtype: str) -> str:
        # Returns correct table name based on 'dtype'.
        # On caller functions, 'dtype' means the current data's
        # type, and 'parent_type' means the parent's type
        return "posts" if dtype == "post" else "replies"

    def __delete_from_parent(self, uid: str, dtype: str):
        parent_uid = self.db.select({'table': self.__get_correct_table(dtype), 'cols': ['parent']}, f"WHERE uid = '{uid}'")[0]['parent']
        print(uid, parent_uid)
        # parent is on posts (?)
        parent = self.__find_by_uid(parent_uid)
        parent['reply_uids'] = remove_all(parent['reply_uids'], uid)
        self.db.update({
            'table': self.__get_correct_table(dtype),
            'reply_uids': parent['reply_uids'],
            'restriction': f"WHERE uid = '{parent_uid}'"
        })

    def __find_by_uid(self, uid: str) -> dict:
        dtype = 'post'
        result = self.db.select({'table': 'posts', 'cols': ['uid', 'reply_uids']}, f"WHERE uid = '{uid}'")
        if not result:
            dtype = 'reply'
            result = self.db.select({'table': 'replies', 'cols': ['uid', 'reply_uids']}, f"WHERE uid = '{uid}'")
        as_dict = result[0]
        as_dict['dtype'] = dtype
        return as_dict

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
            "restriction": f"WHERE su_id = '{self.__esc(su_id)}'"
        })
        return False

    def superuser_verify(self, data: dict) -> bool:
        password = dbint.secure_hash(data['password'], 32)
        if len(self.db.select({
            "table": "superusers",
            "cols": ["su_id"]
        }, f"WHERE email = '{self.__esc(data['email'])}' AND password = '{self.esc(password)}'")) > 0:
            return True
        return False

    def superuser_banip(self, ip: str, hours: int) -> bool:
        if not self.__check_banned(ip):
            return self.db.insert({'table': 'banned', 'ip': ip, 'dt': dbint.dt_plus_hour(hours)})

    def __esc(self, s: str) -> str:
        escaped = repr(s)
        if isinstance(s, str):
            assert escaped[:1] == 'u'
            escaped = escaped[1:]
        if escaped[:1] == '"':
            escaped = escaped.replace("'", "\\'")
        elif escaped[:1] != "'":
            raise AssertionError("unexpected repr: %s", escaped)
        return "E'%s'" % (escaped[1:-1],)


def remove_all(l: list, to_remove) -> list:
    return list(filter(lambda el: el != to_remove, l))


if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr(db)
    form_data = {"body": "example_body", "parent": "example_category"}
    api.add(form_data, 'example_ip_address', 'category')
    # api.delete("188474a66bc02a41b9fef51dc56e9bd9", "reply")
    # result = api.superuser_verify({"email": "mod@service.example", "password": "hello123"})
    # print('-'*40)
    # for row in result:
    #     pd(row)
    #     print('-'*40)

# IP: request.environ['REMOTE_ADDR'][:45]
