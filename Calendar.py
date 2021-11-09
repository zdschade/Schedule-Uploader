import copy
import datetime
import pickle
import os.path
import sys
import pytz
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def format_schedule(ocr_results, startdate, timezone):
    """
    Reformats the ocr results so the google cal API can properly use it
    ocr_results should be a list of lists containing times: [[], ['10:00AM-04:00PM'], [], ['02:00PM-10:00PM'], ['02:00PM-09:00PM'], ['02:00PM-10:00PM'], []]
    startdate should be the first day on the schedule reguardless of there being a shift on that day or not
    timeszone should be in standard format, defaults to EST
    """
    schedule = []
    currdate = startdate.split("/")
    currdate = [int(sect) for sect in currdate]
    tz = pytz.timezone(timezone)
    for time in ocr_results:
        if time == []:
            currdate[1] += 1
            pass
        else:
            split = time[0].split('-')

            start = datetime.datetime.strptime(split[0], "%I:%M%p")
            start = datetime.datetime.strftime(start, "%H:%M")

            end = datetime.datetime.strptime(split[1], "%I:%M%p")
            end = datetime.datetime.strftime(end, "%H:%M")

            scurrdate = str(currdate[0]) + "/" + str(currdate[1]) + "/" + str(currdate[2])

            startdatetime = datetime.datetime.strptime(scurrdate + start, "%m/%d/%Y%H:%M").isoformat()
            enddatetime = datetime.datetime.strptime(scurrdate + end, "%m/%d/%Y%H:%M").isoformat()

            schedule.append([startdatetime, enddatetime])
            currdate[1] += 1

    return schedule

def format_date(date):
    """The date passed from the frontend is not formatted propely, this fixes it
    changes yyyy-mm-dd to mm-dd-yyyy"""

    splitdate = date.split('-')
    newdate = splitdate[1] + "/" + splitdate[2] + "/" + splitdate[0]

    return newdate


SCOPES = ['https://www.googleapis.com/auth/calendar']

def google_login(id=''):
    """Creates the token which allows a user to remain logged in"""

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token = 'token' + id + '.pickle'
    if os.path.exists(token):
        with open(token, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token, 'wb') as token:
            pickle.dump(creds, token)

    global service
    service = build('calendar', 'v3', credentials=creds)
    
    primary_cal = service.calendarList().get(calendarId='primary').execute()
    etag = str(primary_cal['etag'].replace('"', ''))
    if not os.path.exists("token" + etag + ".pickle"):
        os.rename('token.pickle', "token" + etag + ".pickle")
    return etag

def create_events(schedule):
    """Makes events from the recently formatted schedule"""
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    num_shifts = 0
    print("SCHEDULE: " + str(schedule))
    for shift in schedule:
        print("SHIFT: " + str(shift))
        num_shifts += 1

        event = {
            'summary': 'Work',
            #'location': '91 Erford Rd',
            'start': {
                #'date': date,
                'dateTime': shift[0],
                'timeZone': 'America/New_York',
            },
            'end': {
                #'date': date,
                'dateTime': shift[1],
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 60},
                    {'method': 'popup', 'minutes': 60 * 12},
                ],
            },
        }

        #Need to get list of calendars
        primary_cal = service.calendarList().get(calendarId='primary').execute()
        print(primary_cal['etag'])
        event = service.events().insert(calendarId='primary', body=event).execute()
    print(str(num_shifts) + ' events created')
