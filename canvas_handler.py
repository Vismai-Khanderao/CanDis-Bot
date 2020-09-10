from canvasapi.canvas import Canvas
from canvasapi.course import Course
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateutil.parser.isoparser
import pytz

class CanvasHandler(Canvas):

    def __init__(self, API_URL, API_KEY, guild):
        super().__init__(API_URL, API_KEY)
        self._courses = []
        self._guild = guild
        self._mode = "guild"
        self._channels_courses = None # [[channel, [courses]]]
        self._live_channels = []
    
    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, courses):
        self._courses = courses

    @property
    def guild(self):
        return self._guild
    
    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, mode):
        self._mode = mode
        self.courses = []
        self.channels_courses = None
        self.live_channels = []
    
    @property
    def channels_courses(self):
        return self._channels_courses
    
    @channels_courses.setter
    def channels_courses(self, channels_courses):
        self._channels_courses = channels_courses
    
    @property
    def live_channels(self):
        return self._live_channels
    
    @live_channels.setter
    def live_channels(self, live_channels):
        self._live_channels = live_channels
        
    def _ids_converter(self, ids):
        temp = []
        for i in ids:
            temp.append(int(i))
        return temp
        
    def track_course(self, course_ids, msg_channel):
        course_ids = self._ids_converter(course_ids)
                
        if self.mode == "channels":
            if self.channels_courses is None:
                self.channels_courses = [[msg_channel, []]]

            else:
                channels = [channel_courses[0] for channel_courses in self.channels_courses]
                if msg_channel not in channels:
                    self.channels_courses.append([msg_channel, []])


        for i in course_ids:
            course_to_track = self.get_course(i)

            if self.mode == "guild":
                if course_to_track not in self.courses:
                    self.courses.append(course_to_track)

            elif self.mode == "channels":
                for channel_courses in self.channels_courses:
                    if msg_channel == channel_courses[0]:
                        if course_to_track not in channel_courses[1]:
                            channel_courses[1].append(course_to_track)
                        
    def untrack_course(self, course_ids, msg_channel):
        course_ids = self._ids_converter(course_ids)

        if self.mode == "guild":
            for i in course_ids:
                course_to_untrack = self.get_course(i)
                c_ids = [c.id for c in self.courses]
                if course_to_untrack.id in c_ids:
                    del self.courses[c_ids.index(course_to_untrack.id)]
        
        elif self.mode == "channels":
            for channel_courses in self.channels_courses:
                if msg_channel == channel_courses[0]:
                    for i in course_ids:
                        course_to_untrack = self.get_course(i)
                        c_ids = [c.id for c in channel_courses[1]]
                        if course_to_untrack.id in c_ids:
                            del channel_courses[1][c_ids.index(course_to_untrack.id)]
                            if len(channel_courses[1]) == 0:
                                self.channels_courses.remove(channel_courses)
                        

    def get_assignments(self, till, course_ids, msg_channel):
        courses_assignments = []
        if course_ids:
            course_ids = self._ids_converter(course_ids)

        if self.mode == "guild":
            for c in self.courses:
                if course_ids:
                    if c.id in course_ids:
                        courses_assignments.append([c.name, c.get_assignments()])
                else: 
                    courses_assignments.append([c.name, c.get_assignments()])
        elif self.mode == "channels":
            for channel_courses in self.channels_courses:
                if msg_channel == channel_courses[0]:
                    for c in channel_courses[1]:
                        if course_ids:
                            if c.id in course_ids:
                                courses_assignments.append([c.name, c.get_assignments()])
                        else:
                            courses_assignments.append([c.name, c.get_assignments()])

        return self._get_assignment_data(till, courses_assignments)

    def _get_assignment_data(self, till, courses_assignments):
        if till is not None:
            till_timedelta = self._make_timedelta(till)
    
        data_list = []
        for course_assignments in courses_assignments:
            course_name = course_assignments[0]

            for assignment in course_assignments[1]:
                title = course_name + "\n" + "Assignment: " + assignment.__getattribute__("name")

                url = assignment.__getattribute__("html_url")

                desc_html = assignment.__getattribute__("description")
                if desc_html is None:
                    desc_html = "No description"
                desc_soup = BeautifulSoup(desc_html, 'html.parser')
                short_desc = "\n".join(desc_soup.get_text().split("\n")[:4])

                ctime_iso = assignment.__getattribute__("created_at")
                dtime_iso = assignment.__getattribute__("due_at")

                time_shift = timedelta(hours=4) #DST Pacific
                if ctime_iso is None:
                    ctime_text = "No info"
                else:
                    ctime_text = (dateutil.parser.isoparse(ctime_iso)+time_shift).strftime("%Y-%m-%d %H:%M:%S")
                if dtime_iso is None:
                    dtime_text = "No info"
                else:
                    dtime_iso_parsed = (dateutil.parser.isoparse(dtime_iso)+time_shift)
                    if till is not None:
                        dtime_timedelta = dtime_iso_parsed - (datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(hours=7))
                        if dtime_timedelta > till_timedelta:
                            continue
                    dtime_text = dtime_iso_parsed.strftime("%Y-%m-%d %H:%M:%S")
                                
                data_list.append([title, url, short_desc, ctime_text, dtime_text])

        return data_list
    
    def _make_timedelta(self, till):
        till = till.split('-')
        if till[1] in ["hour", "day", "week", "month", "year"]:
            num = float(till[0])
            options = {"hour"  : timedelta(hours=num),
                       "day"   : timedelta(days=num),
                       "week"  : timedelta(weeks=num),
                       "month" : timedelta(days=30*num),
                       "year"  : timedelta(days=365*num)}
            return options[till[1]]
        else:
            year = int(till[0])
            month = int(till[1])
            day = int(till[2])
            return datetime(year, month, day) - (datetime.utcnow() - timedelta(hours=7))

    def get_course_names(self, msg_channel):
        course_names = []
        if self.mode == "guild":
            for c in self.courses:
                course_names.append(c.name)
        elif self.mode == "channels":
            for channel_courses in self.channels_courses:
                if channel_courses[0] == msg_channel:
                    for c in channel_courses[1]:
                        course_names.append(c.name)
        
        return ", ".join(course_names)


