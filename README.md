# <img src="canvas_discord_logo.png" alt="drawing" width="50"/> CanDis-Bot 
Canvas Instructure integration for Discord bot.

## Ever wanted to lose a 14-15 round because of a new assignment?
Me neither, but here we are.

## Features:
- Track canvas courses server-wide or individual channel-wide
- Retrieve linked assignments and announcements
- Be notified about new announcements/assignments and assignment due dates

## Currently being implemented:
- Live notifications for `channels` mode

# How to use:

### Important Notice: 
It has come to my attention that depending on the canvas url you use, the times retrieved are from different regions, sometimes not even from the zone of the institution. Hence the time zone in `canvas_handler.py` must be adjusted accordingly. Currently it is set for PST.

## Activating the bot in the server:
Sending the command `!cd-track` or `!cd-mode` *activates* the bot in the server.

## Finding your course id:
- Go to the Canvas course page
- End of URL would read as this `courses/{course_id}`

## Dealing with multiple courses:
Whenever you see `course_ids`, ensure there is only white space between course ids for multiple courses.

## Adding course(s) to track:
- `!cd-track (course_id | course_ids)`
  
    If this is called before `!cd-mode`, it will initialise the server's Canvas handler to `guild` mode. 
    
    More on this under `!cd-mode`

    - If guild's Canvas handler is in `guild` mode, then tracked course is added server-wide.

    - If guild's Canvas handler is in `channels` mode, then tracked course is added channel-wide only
    
    

## Removing tracked course(s):
- `!cd-untrack (course_id | course_ids)`

    Similar to tracking a course,
    - If guild's Canvas handler is in `guild` mode, then tracked course is removed server-wide.

    - If guild's Canvas handler is in `channels` mode, then tracked course is removed channel-wide only

    If after calling, no courses are currently being tracked, the bot will *deactivate* itself in the server, see **Activating the bot in the server:**

## Getting assignments:
- `!cd-ass ( | (-till (n-(hour|day|week|month|year)) | YYYY-MM-DD | YYYY-MM-DD-HH:MM:SS) | -all) ( | course_id | course_ids)`

    Gets assignments for courses being tracked in the server if `guild` mode or in the channel if `channels` mode.
    
    First argument can be left blank for sending assignments due 2 weeks from now.

    Second argument must have the id for a course currently being tracked, additionally this argument can also be left blank for sending assignments from ALL courses being tracked.
 
    *Filter till due date:*
    - `!cd-ass -till` can be in time from now `e.g.: -till 4-hour` or all assignments before a certain date `e.g.: -till 2020-10-21`

    *All assignments:*
    - `!cd-ass -all` returns ALL assignments.
    
    ### **BEWARE OF POTENTIAL SPAM**
    
    I take no responsibility for you being kicked from a server for having the bot send 20 assignments with -all multiple times.

## Getting announcements:
- `!cd-stream ( | (-till (n-(hour|day|week|month|year)) | YYYY-MM-DD | YYYY-MM-DD-HH:MM:SS) | -all) ( | course_id | course_ids)`

    Every Professor seems to send out announcements using different methods ._. The function is currently working for some courses.

    Gets announcements for courses being tracked in the server if `guild` mode or in the channel if `channels` mode.
    
    First argument can be left blank for sending announcements from 2 weeks ago to now.

    Second argument must have the id for a course currently being tracked, additionally this argument can also be left blank for sending announcements from ALL courses being tracked.
 
    *Filter till due date:*
    - `!cd-stream -till` can be in time from now `e.g.: -till 4-hour` or all announcements after a certain date `e.g.: -till 2020-10-21`

    *All announcements:*
    - `!cd-stream -all` returns ALL announcements.

## Changing modes:
- `!cd-mode (guild | channels)`

    Changes functionality for bot in this server.
    - `guild` mode tracks courses server-wide, i.e. tracking and untracking from any channel changes courses tracked server-wide.
    - `channels` mode tracks courses channel-wide, i.e. tracking and untracking from a channel changes courses tracked channel-wide only.

    **This essentially *resets* the bot in the server, it untracks all courses and stops live updates in the previously live channels.**

## Live announcement updates and assignment reminders:
- `!cd-live`

    Live announcements and assignment reminders are sent to the channel this command is called in.

    If bot is running `guild` mode, then updates are given for all courses being tracked.

    Updates for `channels` mode is being implemented.

    Users with a **@notify** role are pinged before update is sent.

- `!cd-unlive`

    Stops sending updates to the channel it is called in.

    

    