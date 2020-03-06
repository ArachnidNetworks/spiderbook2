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
        :param form_data: data in dictionary format, with each key being a
        column
        :param ip: OP's IP address.
        :param dtype: post's type (determines the table)
        :returns: boolean determining if the operation succeeded of failed"""

        uid = self.db.new_uid(32)
        if not self.__check_banned(ip):
            data = {"uid": uid, "ip": ip, "dt": dbint.dt_now(), "reply_uids":
                    []}
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
        return False

    def __add_reply(self, uid: str, reply_uid: str, parent_type: str) -> bool:
        """Adds a reply to a row's reply_uid array.
        :param uid: row's UID
        :param reply_uid: UID to add to the parent row's reply_uid array
        :param parent_type: parent row's type, can be either 'post' or 'reply'
        :returns: booln determining if the operation succeeded"""
        try:
            # Update table with new reply_uid
            print(parent_type, uid, reply_uid)
            self.db.update({
                "table": self.__get_correct_table(parent_type),
                "restriction": f"WHERE uid = '{uid}'",
                "reply_uids": f"reply_uids || '{reply_uid}'::VARCHAR(32)"
            })
        except IndexError:
            return False
        return True

    def __check_banned(self, ip: str) -> bool:
        """Checks if an IP address is banned. Removes from banned table if
        past expiry date
        :param ip: IP address to check
        :returns: bool indicating if the operation succeeded"""
        sel = self.db.select({'table': 'banned'}, f"WHERE ip = '{ip}'")
        if sel and sel[0]['dt'] < dbint.dt_now():
            return self.db.delete({
                'table': 'banned',
                'restriction': f'WHERE ip = \'{ip}\' AND dt = \
                \'{sel[0]["dt"]}\''
            })
        return type(sel) != bool

    def delete(self, uid: str, dtype: str) -> bool:
        """Deletes a post or reply
        :param uid: row's UID
        :param dtype: row's type, can be either 'post' or 'reply'
        :returns: bool indicating if the operation succeeded"""
        # removes self from parent's reply list if it's a reply
        if dtype == "reply":
            self.__delete_from_parent(uid, dtype)
        # delete self replies
        for ruid in self.db.select({'table': self.__get_correct_table(dtype),
                                    'cols': ['reply_uids']}, f"WHERE uid = \
                                    '{uid}'")[0]['reply_uids']:
            self.delete(ruid, 'reply')
        # delete self
        return self.db.delete({"table": self.__get_correct_table(dtype),
                               "restriction": f"WHERE uid = '{uid}'"})

    def edit(self, uid: str, dtype: str, new_body: str) -> bool:
        """Edits a row's data, setting the body to  new_body
        :param uid: row's UID
        :param dtype: row's type, can be either 'post' or 'reply'
        :param new_body: row's new body
        :returns: bool indicating if the operation succeeded"""
        return self.db.update({
            "table": self.__get_correct_table(dtype),
            "restriction": f"WHERE uid = '{uid}'",
            "body": "'" + self.db.escape(new_body) + "'"
            })

    def get(self, uid: str, dtype: str) -> dict:
        """Selects a row based on the UID given.
        :param uid: row's UID
        :param dtype: row's type, can be either 'post' or 'reply'
        :returns: the selected row"""
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE uid = '{uid}'")[0]

    def getn(self, n: int, dtype: str) -> tuple:
        """Selects n rows of a certain type, ordered by newest first
        :param n: number of rows to select
        :param dtype: rows' type
        :returns: tuple containing each row as a dictionary"""
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"ORDER BY dt DESC LIMIT {n}")

    def getn_by_parent(self, n: int, dtype: str, parent: str) -> tuple:
        """Selects n rows of a certain type with a specific parent
        :param n: number of rows to select
        :param dtype: row's type
        :param parent: parent, can be either a category name or a row's UID
        :returns: tuple containing each row as a dictionary"""
        return self.db.select({
            'table': self.__get_correct_table(dtype)
        }, f"WHERE parent = '{self.db.escape(parent)}' ORDER BY dt DESC LIMIT\
            {n}")

    def __get_correct_table(self, dtype: str) -> str:
        """Selects the correct table name based on dtype. I'm not really sure \
        why this exists, but it's nice, I guess.
        :param dtype: type to convert to table name, can be either 'post' or \
        'reply'
        :returns: appropriate table name"""
        # Returns correct table name based on 'dtype'.
        # On caller functions, 'dtype' means the current data's
        # type, and 'parent_type' means the parent's type
        return "posts" if dtype == "post" else "replies"

    def __delete_from_parent(self, uid: str, dtype: str):
        """Removes a certain UID from the parent's reply_uid array.
        :param uid: UID to remove
        :param dtype: row's type"""
        parent_uid = self.db.select({'table': self.__get_correct_table(dtype),
                                     'cols': ['parent']}, f"WHERE uid = \
                                     '{uid}'")[0]['parent']
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
        """Finds a row based on a UID
        :param uid: row's UID"""
        dtype = 'post'
        result = self.db.select({'table': 'posts', 'cols':
                                 ['uid', 'reply_uids']}, f"WHERE uid = \
                                '{uid}'")
        if not result:
            dtype = 'reply'
            result = self.db.select({'table': 'replies', 'cols':
                                     ['uid', 'reply_uids']}, f"WHERE uid = \
                                    '{uid}'")
        as_dict = result[0]
        as_dict['dtype'] = dtype
        return as_dict

    def superuser_add(self, data: dict) -> bool:
        """Adds a new superuser
        :param data: dictionary containing a key 'su_type' with value 'ADMIN' \
            or 'MOD' and an email/password combination
        :returns: bool indicating if the operation succeeded"""
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
        """Accepts a new superuser's application
        :param su_id: superuser's ID
        :returns: bool indicating if the operation succeeded"""
        return self.db.update({
            "table": "superusers",
            "accepted": True,
            "restriction": f"WHERE su_id = '{su_id}'"
        })
        return False

    def superuser_verify(self, data: dict) -> bool:
        """Verifies a superuser's identity.
        :param data: dicitonary containing an email/password combination
        :returns: bool indicating if the operation succeeded"""
        password = dbint.secure_hash(data['password'], 32)
        if len(self.db.select({
            "table": "superusers",
            "cols": ["su_id"]
        }, f"WHERE email = '{self.db.escape(data['email'])}' AND password = \
                '{password}'")) > 0:
            return True
        return False

    def superuser_banip(self, ip: str, hours: int) -> bool:
        """Bans an IP address for a specific amount of hours
        :param hours: hours to ban IP address for
        :returns: bool indicating if the operation succeeded"""
        if not self.__check_banned(ip):
            return self.db.insert({'table': 'banned', 'ip': ip, 'dt':
                                   dbint.dt_plus_hour(hours)})

    def superuser_unban(self, ip: str) -> bool:
        """Unbans an IP address.
        :param ip: IP address to unban
        :returns: bool indicating if the operation succeeded"""
        if self.__check_banned(ip):
            return self.db.delete({'table': 'banned', 'restriction':
                                   f"WHERE ip = '{ip}'"})


def remove_all(l: list, to_remove) -> list:
    """Removes all instances of  to_remove  from  l
    :param l: the parent list
    :param to_remove: item to remove from the list"""
    return list(filter(lambda el: el != to_remove, l))


if __name__ == '__main__':
    # Connnect to database
    db = dbint.DBInterface("spiderbook", "postgres", "postgres")

    api = APImgr(db)
    api.superuser_unban('ban_example')
    # post_data = {"title": "example_title", "parent": "example_category",
    # "body": "example_body"}
    # reply_data = {"parent": "fb0a6d619ef5b8c17994c6c0f009fa64", "body":
    # "example_body"}
    # api.add(reply_data, "example_ip_address", "post")

# IP: request.environ['REMOTE_ADDR'][:45]
