# Spiderbook v2
### Website made for the Arachnid network. All users are anonymous, but their IP's will be put in the database for spammers and other rule violators.

The backend is being made with Python, with Flask taking care of requests. It will use a PostgreSQL database.

TODO:
- API:
    - specific calls for CRUD actions
        - add post
        - reply to post
        - reply to reply
        - (admin/moderator) remove post
        - (admin/moderator) ban ip (24h-2mo limit)
        - (admin/moderator) ban category
        - (admin) add moderator
        - (admin) remove moderator
        - (admin) ban moderator

- Frontend:
    - home page
    - admin/moderator dashboard
    - complete this list
