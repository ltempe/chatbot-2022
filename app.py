# -*- coding: utf-8 -*-

# imports
import json
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import discord
import re
import nest_asyncio
from random import choice
from datetime import datetime

# make async functions work
nest_asyncio.apply()

# %%

cid = '9ffe6a6cffed429cac2fa7448844442f'
secret = 'bf748672ad1b4498a3da1097dfd0de91'
client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# %%
print('Getting all musics informations...')
try:
    df = pd.read_csv('tracks.csv')
    df['artists'] = df['artists'].apply(
        lambda x: x.strip('[').strip(']').replace(', ', ','))
except:
    artist_names = []
    artist_lists = []
    track_names = []
    album_names = []
    times = []
    popularities = []
    track_ids = []
    years = []
    for year in range(2010, 2022):
        for i in range(0, 1000, 50):
            track_results = sp.search(
                q=f'year:{year}', type='track', limit=50, offset=i)
            for i, t in enumerate(track_results['tracks']['items']):
                artist_names.append(
                    ','.join([a['name'] for a in t['artists']]))
                track_names.append(t['name'])
                album_names.append(t['album']['name'])
                times.append(t['duration_ms'] / 1000)
                track_ids.append(t['id'])
                popularities.append(t['popularity'])
                years.append(year)

    df = pd.DataFrame({'artists': artist_names, 'track': track_names, 'album': album_names,
                       'time (s)': times, 'popularity':  popularities, 'year': years, 'id': track_ids})
    df.to_csv('tracks.csv')

print('All musics have been loaded')
# %%
# defining patterns and intents in regex
city = r'(?P<city>([\w-]+ ?))'
patterns = [{
    'pattern': r'\bthanks?\b',
    'intent': 'thank'
}, {
    'pattern': rf'\W*live\W+in\W+{city}\b',
    'intent': 'city'
}, {
    'pattern': r'\btime is it\b',
    'intent': 'time'
}, {
    'pattern': r'\b(?P<greeting>greetings|hi+|he+[loy]+)\b\W*(you|there|chatbot)?(.*name is (?P<name>\w+)\b)?',
    'intent': 'hello'
}, {
    'pattern': r'\bname is (?P<name>\w+)\b',
    'intent': 'name'
}, {
    'pattern': r'\byour name\b',
    'intent': 'yname'
}, {
    'pattern': r'\b((good\W?)?bye|exit)\b',
    'intent': 'bye'
}, {
    'pattern': r"\bno\b",
    'intent': 'no'
}, {
    'pattern': r'\b(ye+s+|ye+a+h+|of course|su+re|absolutely)\b',
    'intent': 'yes'
}, {
    'pattern': r'\bwhy+\b',
    'intent': 'why'
}, {
    'pattern': r'\bfrom (?P<artist>[a-z -]+)\b',
    'intent': 'from'
}, {
    'pattern': r'\b(?P<rec>artist|music|track).+recommand\b',
    'intent': 'recommand'
}, {
    'pattern': r'\brecommand.+(?P<rec>artist|music|track)\b',
    'intent': 'recommand'
}]

# %%

# %%


def get_answer(intent, res, user):
    """
    Function returning a list of possible answers to the intent of the 
    previous message

    Parameters
    ----------
    intent : str
        Intent of the message, that will be used for the automated answer..
    res : re.Match
        Regex match pattern of the message.
    user : dict
        Dictionnary containing information about the user who wrote the message.

    Returns
    -------
    ans : array
        Array of possible answer from the bot to the intent of the message.

    """
    ans = []

    # We switch every intent, and save possible answers in ans
    if intent == 'thank':
        ans = [f'You are welcome, {user["name"]}!',
               f'It\'s all my pleasure, {user["name"]}!',
               f'Thanks to you !',
               'You\'re welcome !']

    elif intent == 'city':
        # If the user reveal the city he lives in, we save it in user infos
        city = res.group('city').title()
        ans = [f'Oh, {city} is a really nice city!',
               f'I have never been in {city}, is it cool?',
               f'In {city} ? How lucky you are!']
        user['city'] = city

    elif intent == 'time':
        # get the current time
        current_time = datetime.now().strftime("%H:%M:%S")
        ans = [f'Right now, it is {current_time}.',
               f'{current_time}!']

    elif intent == 'hello':
        # get the greeting, if the user say Hiiiii, the bot can answer hiiiii
        greeting = res.group('greeting')
        ans = [f'{greeting.title()}, {user["name"]}! Good to see you!',
               f'Oh, {greeting}, {user["name"]}! How are you today?',
               f'Hey, {user["name"]}, what can I do for you?',
               f'{greeting.title()}, {user["name"]}!']

    elif intent == 'name':
        # if the user reveal his name, that can be different from his username,
        # we save the name in user info
        user["name"] = res.group('name').title()
        ans = [f'Oh, {user["name"]} is a beautiful name!',
               f'Good to know, {user["name"]}!',
               f'I am happy for you, {user["name"]}. I do not even have a name... :(']

    elif intent == 'yname':
        ans = ['Thanks for asking! Actually, I don\'t have name...',
               'I am a bot, I don\'t need a name']

    elif intent == 'bye':
        ans = [f'Bye, {user["name"]}! See you soon.',
               f'We will miss you, {user["name"]}, come back when you can!',
               f'It\'s time to go. See you!',
               'See you!',
               f'Good bye, {user["name"]}']

    elif intent == 'yes':
        ans = ['Cool.',
               'That\'s positive.',
               'Ok.',
               ':)',
               'Fine.']

    elif intent == 'no':
        ans = ['Oh, ok.',
               'I understand',
               'That\'s not positive',
               ':/']

    elif intent == 'why':
        ans = [f'Because, it is like that, {user["name"]}.',
               'Well, why not?',
               'I don\'t know why, actually...',
               'I wish I knew.']

    elif intent == 'from':
        artist = res.group('artist')
        print(artist)
        ts = df[df['artists'].apply(
            lambda x: artist in x.lower())]
        if len(ts) > 0:
            _id = choice(list(ts.loc[:, 'id']))
            t = ts[ts['id'] == _id]
            artists = list(t['artists'])[0].replace(',', ' and ')
            track = list(t["track"])[0]
            popularity = list(t['popularity'])[0]
            time = list(t['time (s)'])[0]
            album = list(t['album'])[0]
            ans = [f'You can listen that song from {artists}, "{track}", from the album {album}. \
 The track lasts {t["time (s)"]} seconds, and has a score of {t["popularity"]} of popularity.\
 Listen it here : https://open.spotify.com/track/{_id}',
                   f'What about {track}, by {artists} ? A track that have {popularity} of popularity,\
 from {album}\'s album. https://open.spotify.com/track/{_id}',
                   f'I can recommand you that track of {time} seconds, from {artists} : {track}!\
 Popularity : {popularity}, please listen it : https://open.spotify.com/track/{_id}']
        else:
            ans = ['I do not know that artist',
                   f'Who is {artist}?']

    elif intent == 'recommand':
        _id = choice(list(df.loc[:, 'id']))
        t = df[df['id'] == _id]
        if res.group('rec') == 'artist':
            artist = choice(choice(list(t['artists'])).split(','))
            ans = [f'I can recommand you {artist}, do you like him ?',
                   f'Do you know {artist} ? It\'s a good artist!',
                   f'What about {artist} ?']
        else:
            artists = list(t['artists'])[0].replace(',', ' and ')
            track = list(t["track"])[0]
            popularity = list(t['popularity'])[0]
            time = list(t['time (s)'])[0]
            album = list(t['album'])[0]
            ans = [f'You can listen that song from {artists}, "{track}", from the album {album}. \
 The track lasts {t["time (s)"]} seconds, and has a score of {t["popularity"]} of popularity.\
 Listen it here : https://open.spotify.com/track/{_id}',
                   f'What about {track}, by {artists} ? A track that have {popularity} of popularity,\
 from {album}\'s album. https://open.spotify.com/track/{_id}',
                   f'I can recommand you that track of {time} seconds, from {artists} : {track}!\
 Popularity : {popularity}, please listen it : https://open.spotify.com/track/{_id}']

    return ans

# %%


def get_response(user_message):
    """
    Function returning the intent of the message

    Parameters
    ----------
    user_message : str
        Message typed by the user on Discord.

    Returns
    -------
    str
        Intent of the message, that will be used for the automated answer.
    res : re.Match
        Regex match pattern of the message.

    """
    for pattern in patterns:
        # for each pattern, we try to match the message
        pat = re.compile(pattern['pattern'])  # compile first
        res = pat.search(user_message)  # and try to match
        if res:
            # if there is match, we return the intent and the match
            return pattern['intent'], res


# %%
# create discord client
client = discord.Client()

# dictionnary that will contains all information about users
users = {}


@client.event
async def on_ready():
    """
    Function launched when the bot is ready

    Returns
    -------
    None.

    """
    print('Bot is ready')


@client.event
async def on_message(message):
    """
    Actions that will be done when a message is received in a channel

    Parameters
    ----------
    message : discord message
        Contains all information about the message sent on the discord channel.

    Returns
    -------
    None.

    """

    # first get the relevant information
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} ({channel})')

    # we don't want the chatbot to answer himself
    if message.author == client.user:
        return

    # if the username is unknown, we save him in the dictionnary
    if username not in users:
        users[username] = {'username': username, 'name': username}

    # if the message have been sent in the correct channel, or if it starts
    # by $chatbot, the chatbot will answer, else no
    if message.channel.name == 'chatbot' or user_message.startswith('$chatbot '):
        # if started by $chatbot, we remove that from the message
        if user_message.startswith('$chatbot '):
            user_message = ' '.join(user_message.split(' ')[1:])

        # array of default answer, if the intent of the message is not clear enough
        ans = ['I cannot tell you',
               f'Sorry, {users[username]["name"]}, I don\'t know...',
               'Can you be more precise?',
               f'What do you mean by {user_message}?']
        if user_message[-1] == '?':
            # if the message is a question, we can add another possibility
            ans.append('That\'s a good question...')
            ans.append('I don\'t think I can answer that question.')

        # get the intent and the match
        response = get_response(user_message.lower())

        if response:
            # if there is a match, get a list of possible answer
            ans = get_answer(*response, users[username])

        # the bot sends back one of the possible answer in the ans array.
        # choice(list) is imported from random module, and will choose a
        # random element from the list
        await message.channel.send(choice(ans))

client.run('OTUwNDI2NjE2OTEwMjE3Mjc2.YiYvww.dcKMinNPUunZAfkFIu4rhMMJkaw')
