import zulip
import forecastio
import datetime
import calendar
import requests
import os



class ZulipBot(object):
    def __init__(self):    
        self.client = zulip.Client(os.environ['ZULIP_WEATHER_EMAIL'], os.environ['ZULIP_WEATHER_KEY'])
        self.subscribe_all()
        self.weather = Weather()

    def subscribe_all(self):
        response = requests.get('https://api.zulip.com/v1/streams',
            auth=requests.auth.HTTPBasicAuth(os.environ['ZULIP_WEATHER_EMAIL'], os.environ['ZULIP_WEATHER_KEY'])
        )

        if response.status_code == 200:
            json = response.json()['streams']
            streams = [{'name': stream['name']} for stream in json]
            self.client.add_subscriptions(streams)
        else:
            raise Exception(response)

    def process_message(self, msg):
        content = msg['content'].split()
        sender_email = msg['sender_email']

        if sender_email == os.environ['ZULIP_WEATHER_EMAIL']:
            return

        if (content[0] == 'weather') or content[0] == '@**Weather**':

            prompts = {
                'now': self.weather.get_current,
                'tomorrow': self.weather.get_tomorrow,
                'week': self.weather.get_week
            }


            if len(content) < 2 or content[1].lower() not in prompts.keys():
                prompt = 'now'
            else:
                prompt = content[1].lower()
                

            content = prompts[prompt]()




            if msg['type'] == 'stream':
                self.client.send_message({
                    'type': 'stream',
                    'subject': msg['subject'],
                    'to': msg['display_recipient'],
                    'content': content
                })
            elif msg['type'] == 'private':
                self.client.send_message({
                    'type': 'private',
                    'to': msg['sender_email'],
                    'content': content
                })
            else:
                return


class Weather(object):
    def __init__(self):
        self.api_key = os.environ['FORECASTIO_KEY']
        self.lat, self.lng = 40.72078, -74.001119 # 455 Broadway
        self.time = None
        self.client = self.setup()
        self.icons = {'clear-day': ':sun_with_face:',
                      'clear-night': ':stars:',
                      'rain': ':cloud:\n:potable_water:',
                      'snow': ':snowman:',
                      'sleet': '',
                      'wind': ':wind_chime:',
                      'fog': ':foggy:',
                      'cloudy': ':cloud:',
                      'partly-cloudy-day': ':partly_sunny:',
                      'partly-coudy-night': ':crescent_moon:\n:cloud:'}

    def setup(self):
        return forecastio.load_forecast(self.api_key, self.lat, self.lng, time=self.time)
    
    def get_current_icon(self):
        return self.client.currently().icon

    def get_current(self):
        return '{}\n{}'.format(self.client.currently().summary, self.icons[self.client.currently().icon])

    def set_tomorrow(self):
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        self.time = tomorrow

    def get_tomorrow(self):
        self.set_tomorrow()
        client = forecastio.load_forecast(self.api_key, self.lat, self.lng, time=self.time)
        return '{}\n{}'.format(client.hourly().summary, self.icons[self.client.hourly().icon])

    def get_week(self):
        week = self.client.daily()
        return '{}\n{}'.format(week.summary.encode('utf-8'), self.icons[week.icon])

def main():
    bot = ZulipBot()
    bot.client.call_on_each_message(bot.process_message)

if __name__ == '__main__':
    main()
