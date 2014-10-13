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
            daily = self.weather.setup()
            daily = daily.daily()

            content = daily.data[0].temperatureMin


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
                    'content': translation.translated_text
                })
            else:
                return


class Weather(object):
    def __init__(self):
        self.api_key = os.environ['FORECASTIO_KEY']
        self.lat, self.lng = 40.72078, -74.001119
        
    def setup(self):
        return forecastio.load_forecast(self.api_key, self.lat, self.lng)

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
