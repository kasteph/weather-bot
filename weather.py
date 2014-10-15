import zulip
import forecastio
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
            content = self.weather.get_current()


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
        self.client = self.setup()
        self.icons = {'clear-day': ':sun_with_face:',
                      'clear-night': ':stars:',
                      'rain': ':cloud:\n:droplet:',
                      'snow': ':snowman:',
                      'sleet': '',
                      'wind': ':wind_chime:',
                      'fog': ':foggy:',
                      'cloudy': ':cloud:',
                      'partly-cloudy-day': ':partly_sunny:',
                      'partly-coudy-night': ':crescent_moon:\n:cloud:'}

    def setup(self):
        return forecastio.load_forecast(self.api_key, self.lat, self.lng)
    
    def get_current_icon(self):
        return self.client.currently().icon

    def get_current(self):
        return '{} {}'.format(self.client.currently().summary, self.icons[self.client.currently().icon])



    # def get_tomorrow(self):

    # def get_week(self):

def main():
    bot = ZulipBot()
    bot.client.call_on_each_message(bot.process_message)

if __name__ == '__main__':
    main()


# current = forecast.currently()

# print current.summary

# daily = forecast.daily()

# print daily.data[0].temperatureMin
# print daily.data[0].temperatureMinTime
