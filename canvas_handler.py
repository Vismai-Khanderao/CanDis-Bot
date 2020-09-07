from canvasapi.canvas import Canvas
from canvasapi.course import Course
from bs4 import BeautifulSoup
import dateutil.parser.isoparser

class CanvasHandler(Canvas):

    def __init__(self, API_URL, API_KEY, guild):
        super().__init__(API_URL, API_KEY)
        self._courses = []
        self._guild = guild
        self._live_channel = None
    
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
    def live_channel(self):
        return self._live_channel
    
    @live_channel.setter
    def live_channel(self, live_channel):
        self._live_channel = live_channel
    
    def ids_converter(self, ids):
        temp = []
        for i in ids:
            temp.append(int(i))
        return temp
    
    def track_course(self, course_ids):
        course_ids = self.ids_converter(course_ids)
        
        for i in course_ids:
            print(i)
            print(self.get_course(i).name)
            self.courses.append(self.get_course(i))
    
    def untrack_course(self, course_ids):
        course_ids = self.ids_converter(course_ids)

        for c in self.courses:
            for i in course_ids:
                if c.course_id == i:
                    self.courses.remove(c)

    def get_assignments(self, course_ids=None):
        courses_assignments = []
        if course_ids is None:
            for c in self.courses:
                courses_assignments.append([c.name, c.get_assignments()])
        
        else:
            course_ids = ids_converter(course_ids)
            for c in self.courses:
                if c.course_id in course_ids:
                    courses_assignments.append([c.name, c.get_assignments()])
        
        return self._get_assignment_data(courses_assignments)

    def _get_assignment_data(self, courses_assignments):
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
                if ctime_iso is None:
                    ctime_text = "No info"
                else:
                    ctime_text = dateutil.parser.isoparse(ctime_iso).strftime("%Y-%m-%d %H:%M:%S")
                if dtime_iso is None:
                    dtime_text = "No info"
                else:
                    dtime_text = dateutil.parser.isoparse(dtime_iso).strftime("%Y-%m-%d %H:%M:%S")

                data_list.append([title, url, short_desc, ctime_text, dtime_text])

        return data_list



