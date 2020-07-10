#!/usr/bin/env python
"""
Communication Webex bot
"""
import os
import time
import json
import requests


BASE_URL = 'https://webexapis.com/v1'
ACCESS_TOKEN = os.environ['WT_ACCESS_TOKEN']
HEADERS = {
    'content-type': 'application/json',
    'authorization': f'Bearer {ACCESS_TOKEN}'
    }


def get_team(name: str) -> dict:
    """Get Webex Team by team name.

    - name (string): team name
    - Return a specific Webex Team (dict) if team name is found.
      Otherwise, return None.
    """
    resource = 'teams'

    try:
        response = requests.get(
            url=f'{BASE_URL}/{resource}', headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    else:
        return next((
            team for team in response.json()['items']
            if team.get('name') == name.strip()), None)


def get_authenticated_user():
    """Get the details of authenticated user."""
    resource = 'people/me'

    try:
        response = requests.get(url=f'{BASE_URL}/{resource}', headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    else:
        return response.json()['emails'][0]


def get_room(title: str = None, team_id: str = None) -> dict:
    """Get a specific Webex room by room Title or associated Team ID.

    - title (string): the name of team space/room
    - team_id (string): team ID
    -> Return a specific room (dict).
    """
    resource = 'rooms'
    params = {'teamId': team_id, 'max': 1000}

    try:
        response = requests.get(
            url=f'{BASE_URL}/{resource}', params=params, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    else:
        if title and team_id:
            return next((
                item for item in response.json()['items']
                if item.get('title') == title and
                item.get('teamId') == team_id), None)

        if title and not team_id:
            return next((
                item for item in response.json()['items']
                if item.get('title') == title.strip()), None)

        if not title:
            return response.json()['items']

        return None


def get_members(room_id: str) -> list:
    """Get membership assoicated with a specific room.

    - room_id (string): Room ID.
    - Return a list of members.
    """
    resource = 'memberships'
    params = {'roomId': room_id}

    try:
        response = requests.get(
            url=f'{BASE_URL}/{resource}', params=params, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    else:
        return response.json()['items']


def send_group_message(room_id: str, message: str):
    """Send a group message to a specific room and its member.

    - room_id (string): Room ID
    - message (string): message
    """
    resource = 'messages'
    members = get_members(room_id=room_id)
    authenticated_user = get_authenticated_user()

    try:
        response = requests.post(
                url=f'{BASE_URL}/{resource}',
                json={'roomId': room_id, 'text': message},
                headers=HEADERS
                )
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    else:
        print(f'Successfully sent a message to {room_id}.')
        if members:
            for member in members:
                if (member['personEmail'] != authenticated_user and
                        'webex.bot' not in member['personEmail']):
                    person_email = member['personEmail']

                    print(f'Sending 1:1 message to {person_email}.')

                    try:
                        response = requests.post(
                            url=f'{BASE_URL}/{resource}',
                            json={
                                'toPersonEmail': person_email,
                                'text': message
                                },
                            headers=HEADERS
                            )
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as http_err:
                        print(f'HTTP Error: {http_err}')
                    else:
                        print(f'Message is successfully sent to {person_email}.')


def main():
    """
    Main function.
    """
    team_space = input('Enter the name of team space: ').strip()
    message = input('Enter message: ').strip()

    room_id = get_room(title=team_space)['id']
    members = get_members(room_id)
    authenticated_user = get_authenticated_user()

    if members:
        print(f'Total of people in this {team_space}: {len(members)}')
        for member in members:
            if (member['personEmail'] != authenticated_user and
                    'webex.bot' not in member['personEmail']):
                person_email = member['personEmail']

                print(f'Sending 1:1 message to {person_email}.')

    # send_group_message(room_id=room_id, message=message)


if __name__ == '__main__':
    main()
