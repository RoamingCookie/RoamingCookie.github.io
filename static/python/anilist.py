import json
import os
import random
import time
import traceback

from browser import ajax, bind, document, html, timer, window, worker
from browser.local_storage import storage


class HTML:
    def __init__(self, data):
        self.data = data
        self.cache = {}

        for cache_id, cache_data in data['CACHE'].items():
            if cache_id != 'SETTINGS':
                storage[cache_id] = json.dumps(cache_data) if isinstance(
                    cache_data, str) else cache_data

        dictionary = ('0', list('abcdefghijklmnopqrstuvwxyz'))
        self.anime = {key.upper(): dict()
                      for key in [dictionary[0]] + dictionary[1]}
        for iD, media in data['DATA'].items():
            title_key = media[iD]['title'][0].upper()
            if not title_key in self.anime:
                title_key = dictionary[0]
            self.anime[title_key][iD] = media
        for key, value in self.anime.copy().items():
            if not value:
                del self.anime[key]

    def code_status(self, extra_data):
        if not extra_data['completed'] and extra_data['available'] and not extra_data['willWatch'] and extra_data['outThere']:
            return 'code-blue'
        elif extra_data['available'] and extra_data['willWatch']:
            return 'code-red'
        else:
            return 'code'

    def stat_out(self):
        user = self.data['USER']
        count = user['count']
        yield html.TABLE(
            html.TR(
                html.TD(html.IMG(src=user['avatar']))
                + html.TD(html.H3('Anime Watched'))
                + html.TD(html.H3('Title Count'))
                + html.TD(html.H3('Episode Count'))
                + html.TD(html.H3('Watch Time')),
            )
            + html.TR(
                html.TD(html.H4(html.A('@' + user['name'], href=user['url'])))
                + html.TD(html.H4(count['anime']))
                + html.TD(html.H4(count['title']))
                + html.TD(html.H4(count['episode']))
                + html.TD(html.H4(count['time']['formated'])),
            )
        )

    def list_out(self):
        lkey = list(self.anime)[-1]
        for key, value in self.anime.items():
            yield html.H6(f'{key} - {len(self.anime[key])}')
            yield html.UL(
                html.SPAN(
                    html.LI(
                        html.EM(
                            media[media_id]['title']
                        ) + html.STRONG(' - ') + html.CODE(
                            media[media_id]['extra']['stat']['formated'],
                            Class='stat-box ' +
                            self.code_status(media[media_id]['extra']),
                            Id=media_id,
                        ),
                    ),
                ) for media_id, media in value.items()
            )
            if key != lkey:
                yield html.SPAN(html.BR(), Class='br-span')

    def dump_data(self):
        yield self.listout_header()
        yield html.DIV(self.stat_out(), Class="stats")
        yield html.BR()
        yield html.DIV(self.list_out(), Class="output")

    def bind_modal(self):
        modal_window = document['modal-window']
        modal_close = document['modal-close']

        def fn_modal_close(event):
            modal_window.style.display = 'none'

        def fn_win_modal_close(event):
            if event.target == modal_window:
                modal_window.style.display = 'none'

        for element in self.data['DATA']:
            document[element].bind('click', lambda event,
                                   element=element: self.make_popup(element))

        modal_close.bind('click', fn_modal_close)

        window.bind('click', fn_win_modal_close)

    def listout_header(self):
        return html.DIV(
            html.DIV(
                html.SPAN(
                    html.IMG(
                        src='/static/image/close.png',
                    ),
                    Class='close',
                    Id='modal-close',
                ) + html.BR() + html.BR() + html.H2(
                    Class='modal-title',
                    Id='modal-title-id',
                ) + html.DIV(
                    Class='modal-img',
                    Id='modal-image-id',
                ) + html.BR() + html.BR(),
                Class='modal-content',
            ),
            Id='modal-window',
            Class='modal',
        )

    def leftout_media(self, iD):
        if iD in self.cache:
            return self.cache[iD]
        watched_media = len([media for media in self.data["DATA"]
                            [iD] if self.data["DATA"][iD][media]["watched"]])
        total_media = len(self.data["DATA"][iD])
        self.cache[iD] = (
            watched_media,
            total_media,
            watched_media == total_media,
        )
        return self.cache[iD]

    def gscolor(self, media):
        if media['status'] in ('RELEASING', 'HIATUS'):
            return 'green'
        elif media['willWatch']:
            return 'red'
        elif media['available']:
            return 'blue'
        else:
            return 'yellow'

    def make_popup(self, iD):
        modal_title = document['modal-title-id']
        modal_image = document['modal-image-id']
        modal_window = document['modal-window']
        media_data = self.data['DATA'][iD]

        modal_title.text = f"{media_data[iD]['title']} ({media_data[iD]['extra']['watchedCount']}/{media_data[iD]['extra']['totalCount']})"

        modal_image.html = ''
        modal_image <= html.DIV(
            html.SPAN(
                html.A(
                    html.DIV(
                        html.IMG(
                            src=media['cover'],
                            Class='modal-image',
                        ),
                        Class='not-grayscale' +
                        ('' if media['watched'] else (
                            ' grayscale gscolor-' + self.gscolor(media))),
                    ),
                    href=media['url'],
                    target="_blank",
                ),
            ) for ID, media in media_data.items()
        )

        modal_window.style.display = 'block'


def settings(close=False, show=False, save=False, get=True, api_key=False):
    if 'SETTINGS' in storage:
        SETTINGS = json.loads(storage['SETTINGS'])
    else:
        SETTINGS = {
            'api': '',
            'music': True,
            'css': True,
            'spoiler': False,
            'nsfw': False,
        }

    if save and api_key:
        SETTINGS['api'] = api_key
        storage['SETTINGS'] = json.dumps(SETTINGS)
        return None

    if get and not show and not save:
        if isinstance(SETTINGS, str):
            return json.loads(SETTINGS)
        return SETTINGS

    settings_window = document['settings-window']

    if save:
        storage['SETTINGS'] = json.dumps({
            'api': document['login-key-box'].value,
            'music': document['settings-ux-music'].checked,
            'css': document['settings-ux-css'].checked,
            'spoiler': document['settings-meme-spoiler'].checked,
            'nsfw': document['settings-meme-nsfw'].checked,
        })
        settings_window.style.display = 'none'
        music_toggle()
        toggle_css()
        return None

    if close:
        settings_window.style.display = 'none'
    else:
        def fn_win_modal_close(event):
            if event.target == settings_window:
                settings_window.style.display = 'none'

        settings_window.style.display = 'block'
        window.bind('click', fn_win_modal_close)

    document['login-key-box'].value = SETTINGS['api']
    document['settings-ux-music'].checked = SETTINGS['music']
    document['settings-ux-css'].checked = SETTINGS['css']
    document['settings-meme-spoiler'].checked = SETTINGS['spoiler']
    document['settings-meme-nsfw'].checked = SETTINGS['nsfw']

    def fn_modal_close(event):
        settings_window.style.display = 'none'

    document['settings-close'].bind('click', fn_modal_close)

def meme(memes=None, toggle=None, hide=False):
    if hide:
        document['memes'].style.display = 'none'
        return None

    global CALCULATING, MEME_INDEX
    meme_setting = settings()

    if not CALCULATING:
        return None

    if toggle is not None:
        if toggle == 'next':
            MEME_INDEX += 1
        elif toggle == 'previous':
            MEME_INDEX -= 1

        if len(memes) == MEME_INDEX:
            MEME_INDEX = 0

        document['meme-title'].text = memes[MEME_INDEX][0]
        document['meme-image'].src = ''
        document['meme-image'].src = memes[MEME_INDEX][1]
        document['meme-link'].href = memes[MEME_INDEX][2]

        document['memes'].style.display = 'flex'

        return None

    subreddits = [
        'wholesomeanimemes',
        'goodanimemes',
        'Animemes',
        'animememes',
    ]
    count = 30
    if memes is None:
        ajax.get(
            f'https://meme-api.herokuapp.com/gimme/{random.choice(subreddits)}/{count}',
            mode="json",
            oncomplete=meme,
        )
        return None
    else:

        def check_meme(spoiler, nsfw):
            pref_spoiler = meme_setting['spoiler']
            pref_nsfw = meme_setting['nsfw']

            if spoiler and not nsfw and pref_spoiler:
                return True
            elif not spoiler and nsfw and pref_nsfw:
                return True
            elif spoiler and nsfw and pref_nsfw and pref_spoiler:
                return True
            elif not spoiler and not nsfw:
                return True
            else:
                return False

        memes = [
            (
                m['title'],
                m['url'],
                m['preview'][-1],
            )
            for m in memes.json['memes']
            if check_meme(m['spoiler'], m['nsfw'])
        ]
        MEME_INDEX = 0

        document['meme-toggle-previous'].bind(
            'click', lambda event, memes=memes, toggle='previous': meme(memes, toggle))
        document['meme-toggle-next'].bind('click', lambda event,
                                          memes=memes, toggle='next': meme(memes, toggle))

        meme(memes, 'next')

def music_toggle(event=None, sourcef=None):
    music_setting = settings()
    pref_music = music_setting['music']
    source = document['music-source']
    player = document['music-player']

    if sourcef is not None:
        source.src = sourcef

    if pref_music:
        player.play()
    else:
        player.pause()


def toggle_css():
    if 'css' in document.query and settings()['css']:
        document['custom-css'].href = document.query['css']
    else:
        document['custom-css'].href = ''


def api_login(event):
    client_id = 10122
    url = f'https://anilist.co/api/v2/oauth/authorize?client_id={client_id}&response_type=token'
    window.location.replace(url)

def err(e):
    document['listout'] <= html.H1('An Exception Has Occurred...') + html.PRE(html.CODE(e))
    return None

def sync_server(data, response):
    ajax.post(
        f'https://roamingcookie.pythonanywhere.com/update/{data["USER"]["id"]}',
        data=json.dumps(data['USER']),
        headers={'UserID':str(data["USER"]["id"]), 'Content-type':'application/json'}
        #oncomplete=lambda response, data=data: sync_server(data, response),
    )


def main_handle(event, userName=None):
    try:
        global start, CALCULATING

        document['listout'].html = ''

        start = time.time()
        CALCULATING = True

        meme()

        if userName is not None:
            user = userName
            document["username-input-box"].value = '@' + user
        else:
            user = document["username-input-box"].value.strip()

        if user.startswith('@'):
            user = user[1:]
        if user.startswith('#'):
            user = int(user[1:])

        api.send(json.dumps({'user': user, 'KEY': settings()['api'], 'CWD': os.getcwd(), 'CACHE': dict(storage)}))
    except:
        err(traceback.format_exc())



    
api = worker.Worker("AniListWorker")

@bind(api, "message")
def display(event):
    try:
        global CALCULATING

        CALCULATING = False

        meme(hide=True)
        data = json.loads(event.data)
        document['listout'].html = ''

        if 'ERROR' in data:
            return err(data['ERROR'])

        dump = HTML(data)

        ajax.post(
            'https://jsonhero.io/api/create.json',
            data={
                'title': f'{data["USER"]["name"]} - {time.time()}.json',
                'content': json.dumps(data),
            },
            oncomplete=lambda response, data=data: sync_server(data, response),
        )

        document['listout'] <= html.DIV(dump.dump_data())
        dump.bind_modal()

        print('DONE', time.time() - start)
    except:
        err(traceback.format_exc())


try:
    document["username-input-button"].bind("click", main_handle)
    document["settings-button"].bind("click", lambda event: settings(show=True))
    document["settings-save"].bind("click", lambda event: settings(save=True))
    document["body"].bind('click', music_toggle)
    document["body"].bind('scrol', music_toggle)
    document["login-key-button"].bind('click', api_login)
    document['username-input-box'].bind('keyup', lambda event: main_handle(event) if event.which == 13 else None)

    toggle_css()


    if window.location.hash.startswith('#access_token='):
        token = dict([i.split('=') for i in window.location.hash[1:].split('&')])['access_token']
        settings(save=True, api_key=token)
        settings(show=True)

    if 'user' in document.query:
        main_handle(None, userName=document.query['user'])

except:
    err(traceback.format_exc())




document['load-content'].style.display = 'none'
document['main-content'].style.display = 'block'
