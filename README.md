# Spiderbook v2
### Website made for the Arachnid network. All users are anonymous, but their IP's will be put in the database for spammers and other rule violators.

The backend is being made with Python, with Flask taking care of requests. It will use a PostgreSQL database.

TODO:
- API:
    - specific calls for CRUD actions
        - add post
        - reply to post
        - reply to reply
        - get all posts
        - get categorized posts
        - get specific post + replies
        - (admin/moderator) remove post
        - (admin/moderator) ban ip (24h-2mo limit)
        - (admin/moderator) unban ip
        - (admin/moderator) ban category
        - (admin/moderator) get all banned ips
        - (admin/moderator) get all banned categories
        - (admin) add moderator
        - (admin) get all admins and moderators
        - (admin) remove moderator
        - (admin) ban moderator
        - (admin) unban moderator
    - proper admin/moderator authentication

- Frontend:
    - home page
    - (admin/moderator) moderation dashboard tab
    - (admin) administration dashboard tab
    - complete this list
