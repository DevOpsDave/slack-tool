#!/usr/bin/env python

from slacker import Slacker
# import sys
# import json
import datetime
import pytz
import argparse
# import ipdb


def lookup_name(id, users_resp):
    name = list(filter(lambda user: user['id'] == id,
                       users_resp.body['members']))[0]['name']
    return name


class SlackHelp(object):
    def __init__(self, slack_token):
        self.api = Slacker(slack_token)

    @property
    def channels(self):
        return self.api.channels.list().body['channels']

    def get_channel_data(self, channel_name):
        channel_data = next((x for x in self.channels if x['name']
                             == channel_name), None)
        if not channel_data:
            raise('Error: channel {} does not exist.'.format(channel_data))
        return channel_data

    def human_time(self, ts):
        dt_obj = datetime.datetime.fromtimestamp(float(ts),
                                                 pytz.timezone('US/Pacific'))
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S')

    def get_messages(self, channel_name, before=None, after=None,
                     stars_only=None):

        search_str = 'in:#{}'.format(channel_name)

        if before:
            search_str += ' before:{}'.format(before)

        if after:
            search_str += ' after:{}'.format(after)

        if stars_only:
            search_str += ' has:star'

        page = 1
        messages = []
        responses = []
        output = []

        while(True):
            search_resp = self.api.search.messages(search_str,
                                                   sort='timestamp',
                                                   sort_dir='asc', count=1000,
                                                   page=page)

            if not search_resp.successful:
                raise('Error: fail in get_messages => {}'
                      .format(search_resp.error))
            elif search_resp.body['messages']['paging']['pages'] < page:
                raise('Error: fail in get_messages, page got to big.')
            elif search_resp.body['messages']['paging']['pages'] >= page:
                for message in search_resp.body['messages']['matches']:
                    channel_name = message['channel']['name']
                    ts = message['ts']
                    obj_type = message['type']
                    username = message['username']
                    text = message['text']
                    dt_ts = self.human_time(ts)
                    mesg = {'ts': ts, 'type': obj_type, 'username': username,
                            'text': text, 'dt_ts': dt_ts, 'text': text,
                            'channel': channel_name}
                    messages.append(mesg)
                    output_str = '{} {} {} - {}'.format(dt_ts, channel_name, username, text)
                    output.append(output_str)
                responses.append(search_resp)

                if search_resp.body['messages']['paging']['pages'] > page:
                    page += 1
                else:
                    return {'messages': messages, 'responses': responses, 'output': output}


if __name__ == '__main__':

    """Command line aruments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token')
    parser.add_argument('-r', '--rooms', action='append')

    """Get data positional arguments."""
    def validate_date(s):
        try:
            if s.count(':') == 0:
                return datetime.datetime.strptime(s, "%Y-%m-%d")
            elif s.count(':') == 1:
                return datetime.datetime.strptime(s, "%Y-%m-%d:%H")
            elif s.count(':') == 2:
                return datetime.datetime.strptime(s, "%Y-%m-%d:%H:%M")
            elif s.count(':') == 3:
                return datetime.datetime.strptime(s, "%Y-%m-%d:%H:%M:%S")
            else:
                raise ValueError
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    parser.add_argument('start_date', type=validate_date)
    parser.add_argument('end_date', type=validate_date)
    args = parser.parse_args()

    """
    slack = Slacker(args.token)

    ipdb.set_trace()

    # SlackHelper
    sh = SlackHelp(slack)

    # Get Usernames
    users_resp = slack.users.list()

    channels = slack.channels.list().body['channels']

    srvcint_chan = list(filter(
        lambda channel: channel['name'] == 'service-interruption', channels)
                        )[0]
    siu_chan = list(filter(
        lambda channel: channel['name'] == 'siu-investigation', channels))[0]

    # Get all stars I set.
    stars_resp = slack.stars.list(count=1000, page=1)
    all_stars = list(filter(lambda item: item['type'] == 'message' and
                            (item['channel'] == srvcint_chan['id'] or
                            item['channel'] == siu_chan['id']),
                            stars_resp.body['items']))
    all_stars_dict = {}
    ipdb.set_trace()

    for message in all_stars:
        ts = convert_time(message['message']['ts'])
        user = lookup_name(message['message']['user'], users_resp)
        text = message['message']['text']
        all_stars_dict[message['message']['ts']] = (
            "{} - {} - {}".format(ts, user, text))

    index = sorted(all_stars_dict, key=lambda x: float(x))
    for key in index:
        print(all_stars_dict[key])
    """
