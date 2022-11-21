import json
import os
import random
import time
import traceback
import javascript

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
        
        for cache_id, cache_data in data['CACHE'].items():
            try:
                data['CACHE'][cache_id] = json.loads(data['CACHE'][cache_id])
            except Exception:
                pass
            
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
            else:
                self.anime[key] = dict(sorted(value.items(), key=lambda k: k[1][k[0]]['title'].lower()))
                
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
    
    def unwatch(self):
        yield html.TR(
            html.TD(html.B('Anime Title'))
          + html.TD(html.B('Format/Status'))
          + html.TD(html.B('ID')),
        )
        
        media_s = []
        for series in self.data['DATA'].values():
            for media in series.values():
                media_s.append(media)
        
        media_s = sorted(media_s, key=lambda k: k['title'])
        for media in media_s:
            if not media['watched']:
                yield html.TR(
                    html.TD(
                        html.A(
                            media['title'],
                            href=media['url'],
                            target='_blank',
                        ),
                    )
                  + html.TD(
                        html.CODE(
                            media['format'],
                            Class='unwatch-' + self.gscolor(media),
                        )
                    )
                  + html.TD(
                        html.CODE(
                            media['id'],
                        )
                    ),
                )
    
    def misc_out(self):
        yield html.TR(
            html.TD(html.B('User Name')) 
          + html.TD(html.CODE('@' + self.data['USER']['name'])),
        )
        yield html.TR(
            html.TD(html.B('User ID')) 
          + html.TD(html.CODE('#' + str(self.data['USER']['id']))),
        )
        yield html.TR(
            html.TD(html.B('Time Taken To Process')) 
          + html.TD(html.CODE('processing...', Id='time-taken')),
        )
        yield html.TR(
            html.TD(html.B('Data Send To Server')) 
          + html.TD(html.BUTTON('Click To View', Class='button-30', Id='server-data-view')),
        )
        yield html.TR(
            html.TD(html.B('Raw Processed Data')) 
          + html.TD(html.BUTTON('Click To View', Class='button-30', Id='data-view')),
        )
        yield html.TR(
            html.TD(html.B('Data At Server')) 
          + html.TD(html.BUTTON('View in JsonHero', Class='button-30', Id='live-server-data-view')),
        )
        
    def dump_data(self):
        yield self.listout_header()
        yield html.DIV(html.H1(f"@{self.data['USER']['name']} Watched {self.data['USER']['count']['anime']} Anime"), Class="output")
        yield html.BR()
        yield html.DIV(self.stat_out(), Class="stats")
        yield html.BR()
        yield html.DIV(self.list_out(), Class="output")
        yield html.BR()
        yield html.TABLE(self.misc_out(), Class="output misc-data")
        yield html.BR()
        yield html.TABLE(self.unwatch_out(), Class="output")
        yield html.BR()
        yield html.TABLE(self.unwatch(), Class="output unwatch-list")
        yield html.BR()
        yield html.DIV(self.badge_out(), Class="output")
        yield html.BR()
        yield html.CENTER(
            html.IMG(src="/static/image/made-with-python.svg")
          + html.BR()
          + html.IMG(src="/static/image/uses-html.svg")
          + html.IMG(src="/static/image/uses-css.svg")
          + html.IMG(src="/static/image/uses-js.svg")
          + html.BR()
          + html.IMG(src="/static/image/powered-by-electricity.svg"),
            Id='badge',
        )
        
    def badge_out(self):
        badge_url = f"https://roamingcookie.pythonanywhere.com/{'svg' if 'svg' in document.query else 'badge'}/{self.data['USER']['id']}{window.location.search}"
        current_url = f'https://roamingcookie.github.io/{window.location.search}'
        
        html_code = f'''
        <a href="{current_url}"><img src="{badge_url}" alt="@{self.data['USER']['name']} Badge"></a>
        '''.strip()

        md_code = f'''
        [![@{self.data['USER']['name']} Badge]({badge_url})]({current_url})
        '''.strip()

        html_code_element = html.CODE()
        html_code_element.text = html_code

        md_code_element = html.CODE()
        md_code_element.text = md_code
        
        yield html.CENTER(html.IMG(src=badge_url, Id='badge-image'))

        yield html.H6('Markdown') + html.PRE(md_code_element, Id='md-code')

        yield html.H6('HTML') + html.PRE(html_code_element, Id='html-code')

        yield html.CENTER(html.A('CUSTOMIZE', href='/docs/badge_api'))
        
    def unwatch_out(self):
        yield html.TR(
            html.TD(html.B('Unwatched Anime'))
          + html.TD(html.B('Count')),
        )
        yield html.TR(
            html.TD('Dropped')
          + html.TD(self.data['CARD']['UnwatchDropped']),
        )
        yield html.TR(
            html.TD('Not Released')
          + html.TD(self.data['CARD']['UnwatchNotReleased']),
        )
        yield html.TR(
            html.TD('Airing')
          + html.TD(self.data['CARD']['UnwatchAiring']),
        )
        yield html.TR(
            html.TD('Plausible')
          + html.TD(self.data['CARD']['UnwatchPlausible']),
        )
        yield html.TR(
            html.TD('Total')
          + html.TD(self.data['CARD']['TotalUnwatch']),
        )
    
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
        
        document['server-data-view'].bind('click', lambda e, data={str(self.data['USER']['id']): list(self.data['CARD'].values())}: pop_json(data))
        document['live-server-data-view'].bind('click', lambda e: window.open(f"https://roamingcookie.pythonanywhere.com/view/{self.data['USER']['id']}", '_blank').focus())
        document['data-view'].bind('click', lambda e, data=self.data: pop_json(data))

        window.hljs.highlightElement(document['md-code'])
        window.hljs.highlightElement(document['html-code'])
        
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
        document['meme-tip'].style.display = 'none'
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
        document['meme-tip'].style.display = 'flex'

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
            if check_meme(m['spoiler'], m['nsfw']) and not m['preview'][-1].startswith('https://i.imgur.com/')
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

def sync_server(data):
    def update_badge(response):
        document['badge-image'].src = ''
        document['badge-image'].src = f"https://roamingcookie.pythonanywhere.com/{'svg' if 'svg' in document.query else 'badge'}/{data['USER']['id']}{window.location.search}"
    
    ajax.post(
        f'https://roamingcookie.pythonanywhere.com/update/{data["USER"]["id"]}',
        data=json.dumps({data["USER"]["id"]: list(data['CARD'].values())}),
        headers={
            'UserID': str(data["USER"]["id"]), 
            'Content-type':'application/json',
        },
        oncomplete=update_badge,
    )

def pop_json(jsond):
    json_window_modal = document['json-window-modal']
    json_window_modal.style.display = 'block'
    json_window = document['json-window']
    cjson = javascript.JSON.stringify(jsond, javascript.NULL, 4)
    json_window.html = ''
    json_window <= html.BUTTON(html.IMG(src='/static/image/close.png'), Class="button-30", Id='close-json')
    json_window <= html.BUTTON(html.IMG(src='/static/image/copy.png'), Class="button-30", Id='copy-json')
    json_window <= html.BUTTON(html.IMG(src='/static/image/jsonhero.png'), Class="button-30", Id='view-json') 
    json_window <= html.BR() + html.BR() 
    json_window <= html.PRE(html.CODE(cjson), Id='json-code')
    window.hljs.highlightElement(document['json-code'])
    
    def close_json(e):
        json_window_modal.style.display = 'none'
    def copy_json(e, js=cjson):
        window.navigator.clipboard.writeText(js)
    def view_json(e, js=cjson):
        window.navigator.clipboard.writeText(js)
        window.open('https://jsonhero.io/', '_blank').focus()
    def fn_win_modal_close(event):
        if event.target == json_window_modal:
            json_window_modal.style.display = 'none'
            
    document['close-json'].bind('click', close_json)
    document['copy-json'].bind('click', copy_json)
    document['view-json'].bind('click', view_json)
    window.bind('click', fn_win_modal_close)

def main_handle(event, userName=None):
    try:
        global start, CALCULATING
    
        document['listout'].html = ''
    
        start = time.time()
        CALCULATING = True
    
        meme()

        if userName is not None:
            user = userName
            document["username-input-box"].value = ('@' if not userName.startswith('#') else '') + user
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
        
        sync_server(data)
        
        dump = HTML(data)

        document['listout'] <= html.DIV(dump.dump_data())
        dump.bind_modal()

        document['time-taken'].text = str(round(time.time() - start, 3)) + ' seconds'
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
