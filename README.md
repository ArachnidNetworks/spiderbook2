# Spiderbook v2
Website made for the Arachnid network. All users are anonymous, but their IP's will be put in the database for spammers and other rule violators.

----
## Q&A: Not questions you asked, but questions you deserve
### How will you organize your schedule?
> I will attempt to complete at least 1 TODO item per day, and add anything I think is important to the list ASAP.

### How will you code the API?
> It will contain all of the SQL and more logic-y stuff this time, unlike on the second time I tried doing this. (this is the third time I'm trying , I switched to a different repository from 1st to 2nd because I'm dumb.)

### How will you make the frontend?
> I plan on using Grid and Flexbox for the layouts, which will be relatively simple. I may, at some point, add some prettier decorations, but at first it will be a flat, simplistic design.

### How will you code the backend?
> The backend is being made with Python, with Flask taking care of requests. The Database is going to be made with PostgreSQL with a file named 'setup.psql' containing all the necessary code to set it up on your machine.

### How long do you think this will take?
> From December 2019 to the start of February 2020 I will work at least 2 hours a day on 4 or 5 days of the week, although it varies a lot (mostly to more hours/days of work). In this time I will complete at least 90% of the API TODO list. After that work will go by slower, but by then I will only have to work for 1 or 2 more months. In total, I'm assuming from 3-4 months.
----    
### TODO:
- #### API:
    - specific calls for CRUD actions
        - (mod/admin) ban ip (24h-2mo limit)
        - (mod/admin) unban ip
        - (mod/admin) ban category
        - (mod/admin) get all banned ips
        - (mod/admin) get all banned categories
        - (admin) add moderator
        - (admin) get all admins and moderators
        - (admin) remove moderator
    - proper mod/admin authentication

- #### Frontend:
    - home page
    - single post page
    - proper comment parsing (comment a bit to the right of original post)
    - (mod) moderation dashboard tab
    - (admin) administration dashboard tab
