from canvasapi.requester import Requester
from canvasapi.util import get_institution_url, combine_kwargs

def get_course_stream(course_id, base_url, access_token, **kwargs):
    access_token = access_token.strip()
    base_url = get_institution_url(base_url)
    requester = Requester(base_url, access_token)
    response = requester.request(
        "GET",
        "courses/{}/activity_stream".format(course_id),
        _kwargs=combine_kwargs(**kwargs)
        )
    return response.json()

def get_course_stream_summary(course_id, base_url, access_token, **kwargs):
    access_token = access_token.strip()
    base_url = get_institution_url(base_url)
    requester = Requester(base_url, access_token)
    response = requester.request(
        "GET",
        "courses/{}/activity_stream/summary".format(course_id),
        _kwargs=combine_kwargs(**kwargs)
        )
    return response.json()

def get_course_url(course_id, base_url):
    base_url = get_institution_url(base_url)
    return "{}/courses/{}".format(base_url, course_id)