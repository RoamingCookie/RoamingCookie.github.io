import json
import os
import sys
import random
import time
import traceback
import javascript
from urllib.parse import urlencode
import base64

from browser import ajax, bind, document, html, timer, window, worker
from browser.local_storage import storage

sys.setrecursionlimit(10**12) 

class HTML:
    def __init__(self, data):
        self.data = data
        self.cache = {}
        print(11)
        for cache_id, cache_data in data['CACHE'].items():
            if cache_id != 'SETTINGS':
                storage[cache_id] = json.dumps(cache_data) if isinstance(
                    cache_data, str) else cache_data
        print(12)
        for cache_id, cache_data in data['CACHE'].items():
            try:
                data['CACHE'][cache_id] = json.loads(data['CACHE'][cache_id])
            except Exception:
                pass
            
        dictionary = ('0', list('abcdefghijklmnopqrstuvwxyz'))
        self.anime = {key.upper(): dict()
                      for key in [dictionary[0]] + dictionary[1]}
        print(13)
        for iD, media in data['DATA']['ANIME'].items():
            title_key = media[iD]['title'][0].upper()
            if not title_key in self.anime:
                title_key = dictionary[0]
            self.anime[title_key][iD] = media
            
        for key, value in self.anime.copy().items():
            if not value:
                del self.anime[key]
            else:
                self.anime[key] = dict(sorted(value.items(), key=lambda k: k[1][k[0]]['title'].lower()))
                
        print(14)        
        self.manga = {key.upper(): dict()
                      for key in [dictionary[0]] + dictionary[1]}
        print(15)
        for iD, media in data['DATA']['MANGA'].items():
            title_key = media[iD]['title'][0].upper()
            if not title_key in self.manga:
                title_key = dictionary[0]
            self.manga[title_key][iD] = media
        print(16)
        for key, value in self.manga.copy().items():
            if not value:
                del self.manga[key]
            else:
                self.manga[key] = dict(sorted(value.items(), key=lambda k: k[1][k[0]]['title'].lower()))
        print(17)
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
                + html.TD(html.H3('Manga Read'))
                + html.TD(html.H3('Anime Title Count'))
                + html.TD(html.H3('Manga Title Count'))
                + html.TD(html.H3('Episode Watch Count'))
                + html.TD(html.H3('Chapters Read Count')) 
                + html.TD(html.H3('Anime Watch Time'))
                + html.TD(html.H3('Manga Read Time')), 
            )
            + html.TR(
                html.TD(html.H4(html.A('@' + user['name'], href=user['url'])))
                + html.TD(html.H4(count['anime']))
                + html.TD(html.H4(count['manga']))
                + html.TD(html.H4(count['title']))
                + html.TD(html.H4(count['headings']))
                + html.TD(html.H4(count['episode']))
                + html.TD(html.H4(count['chapter']))
                + html.TD(html.H4(count['watchtime']['formated']))
                + html.TD(html.H4(count['readtime']['formated'])), 
            )
        )

    def list_out(self):
        lkey = list(self.anime)[-1]
        yield html.H1('Anime')
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
                yield html.SPAN('', Class='br-span')
        
        if len(self.manga) != 0:
            lkey = list(self.manga)[-1]
            yield html.H1('Manga')
            
        for key, value in self.manga.items():
            yield html.H6(f'{key} - {len(self.manga[key])}')
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
                yield html.SPAN('', Class='br-span')
        
    def unwatch(self):
        yield html.TR(
            html.TD(html.H1('Anime'))
          + html.TD('')
          + html.TD('')
          + html.TD('')
        )
        
        yield html.TR(
            html.TD(html.B('Format/Status'))
          + html.TD(html.B('Anime Title'))
          + html.TD(html.B('ID'))
          + html.TD(html.B('zoro.to')),
        )
        
        media_s = []
        for series in self.data['DATA']['ANIME'].values():
            for media in series.values():
                media_s.append(media)
        
        media_s = sorted(media_s, key=lambda k: k['title'])
        for media in media_s:
            if not media['watched']:
                yield html.TR(
                    html.TD(
                        html.CODE(
                            media['format'],
                            Class='unwatch-' + self.gscolor(media),
                        )
                    )
                  + html.TD(
                        html.A(
                            media['title'],
                            href=media['url'],
                            target='_blank',
                        ),
                    )
                  + html.TD(
                        html.CODE(
                            media['id'],
                        )
                    )
                  + html.TD(
                        html.A(
                            html.BUTTON(
                                html.IMG(src="/static/image/zoro.to.png", width='25px'),
                                Class='button-30'
                            ),
                            href='https://zoro.to/search?' + urlencode({'keyword': media['title']}),
                            target='_blank',
                        ),
                    ) 
                )
                
        if len(self.manga) != 0:
            yield html.TR(
                html.TD(html.H1('Manga'))
              + html.TD('')
              + html.TD('')
              + html.TD('')
            )
            
            yield html.TR(
                html.TD(html.B('Format/Status'))
              + html.TD(html.B('Manga Title'))
              + html.TD(html.B('ID'))
              + html.TD(html.B('mangareader.to')),
            )
        
        media_s = []
        for series in self.data['DATA']['MANGA'].values():
            for media in series.values():
                media_s.append(media)
        
        media_s = sorted(media_s, key=lambda k: k['title'])
        for media in media_s:
            if not media['watched']:
                yield html.TR(
                    html.TD(
                        html.CODE(
                            media['format'],
                            Class='unwatch-' + self.gscolor(media),
                        )
                    )
                  + html.TD(
                        html.A(
                            media['title'],
                            href=media['url'],
                            target='_blank',
                        ),
                    )
                  + html.TD(
                        html.CODE(
                            media['id'],
                        )
                    )
                  + html.TD(
                        html.A(
                            html.BUTTON(
                                html.IMG(src="/static/image/mangareader.to.png", width='25px'),
                                Class='button-30'
                            ),
                            href='https://mangareader.to/search?' + urlencode({'keyword': media['title']}),
                            target='_blank',
                        ),
                    )
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
            html.TD(html.B('Data Sent To Server')) 
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
        yield html.TR(
            html.TD(html.B('Additional Relation Rule File')) 
          + html.TD(html.BUTTON('Click To View', Class='button-30', Id='relation-rule-data-view')),
        )
        
    def dump_data(self):
        print(20)
        yield self.listout_header()
        yield html.DIV(html.H1(f"@{self.data['USER']['name']} Watched {self.data['USER']['count']['anime']} Anime & Read {self.data['USER']['count']['manga']} Manga"), Class="output")
        yield html.BR()
        print(2)
        yield html.DIV(self.stat_out(), Class="stats")
        yield html.BR()
        yield html.DIV(self.list_out(), Class="output")
        yield html.BR()
        print(3)
        yield html.TABLE(self.misc_out(), Class="output misc-data")
        yield html.BR()
        yield html.CENTER(html.TABLE(self.unwatch_out(), Class="output"))
        yield html.BR()
        print(4)
        yield html.CENTER(html.TABLE(self.unwatch(), Class="output unwatch-list"))
        yield html.BR()
        yield html.DIV(self.badge_out(), Class="output")
        yield html.BR()
        print(5)
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
        print(6)
        
    def badge_out(self):
        query = {k.lower():v for k,v in dict(document.query).items()}
        badge_parameters = {
            'svg': query.get('svg', ''),
            'message': query.get('message', ''),
            'style': query.get('style', ''),
            'label': query.get('label', ''),
            'logo': query.get('logo', ''),
            'logoColor': query.get('logoColor', ''),
            'logoWidth': query.get('logoWidth', ''),
            'link': query.get('link', ''),
            'labelColor': query.get('labelColor', ''),
            'color': query.get('color', ''),
        }
        
        for k,v in query.items():
            if k.startswith('jinja_'):
                badge_parameters[k] = v
                
        badge_parameters = {k:v for k,v in badge_parameters.items() if v != ''}
        
        site_parameters = {
            'user': query.get('user', ''),
            'music': query.get('music', ''),
            'css': query.get('css', ''),
        }
        site_parameters['user'] = '#' + str(self.data['USER']['id'])
        site_parameters = {k:v for k,v in site_parameters.items() if v != ''}
        site_parameters.update(badge_parameters)
        
        
        badge_url = f"{SERVER}/badge/{self.data['USER']['id']}?{urlencode(badge_parameters)}"
        svg_badge_url = f"{SERVER}/svg/{self.data['USER']['id']}?{urlencode(badge_parameters)}"
        
        current_url = f'https://roamingcookie.github.io/?{urlencode(site_parameters)}'
        
        html_code = f'''
        <a href="{current_url}"><img src="{badge_url}" alt="@{self.data['USER']['name']} Badge"></a>
        '''.strip()
        md_code = f'''
        [![@{self.data['USER']['name']} Badge]({badge_url})]({current_url})
        '''.strip()
        
        svg_html_code = f'''
        <a href="{current_url}"><img src="{svg_badge_url}" alt="@{self.data['USER']['name']} Badge"></a>
        '''.strip()
        svg_md_code = f'''
        [![@{self.data['USER']['name']} Badge]({svg_badge_url})]({current_url})
        '''.strip()

        html_code_element = html.CODE()
        html_code_element.text = html_code
        md_code_element = html.CODE()
        md_code_element.text = md_code
        
        svg_html_code_element = html.CODE()
        svg_html_code_element.text = svg_html_code
        svg_md_code_element = html.CODE()
        svg_md_code_element.text = svg_md_code
        
        yield html.CENTER(html.H2('Use them in your AniList Bio\'s'))
        yield html.HR()
        
        yield html.CENTER(html.IMG(src=f"{SERVER}/placeholder/{self.data['USER']['name']}", Id='badge-image'))
        yield html.H6('Markdown') + html.PRE(md_code_element, Id='md-code')
        yield html.H6('HTML') + html.PRE(html_code_element, Id='html-code')
        
        yield html.HR()
        
        yield html.CENTER(html.IMG(src=f"{SERVER}/placeholder/{self.data['USER']['name']}", Id='svg_badge-image'))
        yield html.H6('Markdown') + html.PRE(svg_md_code_element, Id='svg_md-code')
        yield html.H6('HTML') + html.PRE(svg_html_code_element, Id='svg_html-code')
 
        yield html.CENTER(html.A('CUSTOMIZE LIVE BADGE', href='/docs/badge_api', target='_blank'))
        
    def unwatch_out(self):
        yield html.TR(
            html.TD(html.B('Category'))
          + html.TD('')
          + html.TD(html.B('Anime'))
          + html.TD('')
          + html.TD(html.B('Manga'))
          + html.TD(''),
        )
        yield html.TR(
            html.TD('Dropped/Paused')
          + html.TD('')
          + html.TD(self.data['CARD']['UnwatchDropped'])
          + html.TD('')
          + html.TD(self.data['CARD']['UnReadDropped'])
          + html.TD(''),
        )
        yield html.TR(
            html.TD('Not Released')
          + html.TD('')
          + html.TD(self.data['CARD']['UnwatchNotReleased'])
          + html.TD('')
          + html.TD(self.data['CARD']['UnReadNotReleased'])
          + html.TD(''),
        )
        yield html.TR(
            html.TD('Airing')
          + html.TD('')
          + html.TD(self.data['CARD']['UnwatchAiring'])
          + html.TD('')
          + html.TD(self.data['CARD']['UnReadAiring'])
          + html.TD(''),
        )
        yield html.TR(
            html.TD('Plausible')
          + html.TD('')
          + html.TD(self.data['CARD']['UnwatchPlausible'])
          + html.TD('')
          + html.TD(self.data['CARD']['UnReadPlausible'])
          + html.TD(''),
        )
        yield html.TR(
            html.TD('Total')
          + html.TD('')
          + html.TD(self.data['CARD']['TotalUnwatch'])
          + html.TD('')
          + html.TD(self.data['CARD']['TotalUnRead'])
          + html.TD(''),
        )
    
    def bind_modal(self):
        modal_window = document['modal-window']
        modal_close = document['modal-close']

        def fn_modal_close(event):
            modal_window.style.display = 'none'

        def fn_win_modal_close(event):
            if event.target == modal_window:
                modal_window.style.display = 'none'

        for element in self.data['DATA']['ANIME']:
            document[element].bind('click', lambda event,
                                   element=element: self.make_popup(element))
        
        for element in self.data['DATA']['MANGA']:
            document[element].bind('click', lambda event,
                                   element=element: self.make_popup(element, manga=True))

        modal_close.bind('click', fn_modal_close)

        window.bind('click', fn_win_modal_close)
        
        document['server-data-view'].bind('click', lambda e, data={str(self.data['USER']['id']): list(self.data['CARD'].values())}: pop_json(data))
        document['relation-rule-data-view'].bind('click', lambda e, data={'Rules': CUSTOM}: pop_json(data))
        document['live-server-data-view'].bind('click', lambda e: window.open(f"{SERVER}/view/{self.data['USER']['id']}", '_blank').focus())
        document['data-view'].bind('click', lambda e, data=self.data: pop_json(data))

        window.hljs.highlightElement(document['md-code'])
        window.hljs.highlightElement(document['html-code'])
        
        window.hljs.highlightElement(document['svg_md-code'])
        window.hljs.highlightElement(document['svg_html-code'])
        
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
        watched_media = len([media for media in self.data["DATA"]['ANIME']
                            [iD] if self.data["DATA"]['ANIME'][iD][media]["watched"]])
        total_media = len(self.data["DATA"]['ANIME'][iD])
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

    def make_popup(self, iD, manga=False):
        modal_title = document['modal-title-id']
        modal_image = document['modal-image-id']
        modal_window = document['modal-window']
        media_data = self.data['DATA']['ANIME' if not manga else 'MANGA'][iD]

        modal_title.text = f"{media_data[iD]['title']} ({media_data[iD]['extra']['watchedCount']}/{media_data[iD]['extra']['totalCount']})"

        modal_image.html = ''
        modal_image <= html.DIV(
            html.SPAN(
                html.SPAN(
                    html.DIV(
                        html.IMG(
                            src=media['cover'],
                            Class='modal-image',
                        ),
                        Class='not-grayscale' +
                        ('' if media['watched'] else (
                            ' grayscale gscolor-' + self.gscolor(media))),
                    ),
                    Id=f'C{ID}',
                ),
            ) for ID, media in media_data.items()
        )
        
        for ID, media in media_data.items():
            anilist_co = media['url']
            external = f'https://{"mangareader" if manga else "zoro"}.to/search?' + urlencode({'keyword': media['title']})
            _pop_up_click_bind(f'C{ID}', anilist_co, external)

        modal_window.style.display = 'block'

class _pop_up_click_bind:
    def __init__(self, Id, click_url, dbclick_url):
        self.dom = document[Id]
        
        self.prevent_click = False
        self.delay = 250
        self.timer = 0
        
        self.anilist_co = click_url
        self.external = dbclick_url
        
        self.dom.bind('click', self.click_timer)
        self.dom.bind('dblclick', self.dblclick)
    
    def click_timer(self, event):
        self.timer = timer.set_timeout(self.click, self.delay)
        
    def open_link(self, url):
        window.open(url, '_blank').focus()
        
    def click(self):
        if not self.prevent_click:
            self.open_link(self.anilist_co)
        self.prevent_click = False
        
    def dblclick(self, event):
        timer.clear_timeout(self.timer)
        self.prevent_click = True
        self.open_link(self.external)

def settings(close=False, show=False, save=False, get=True, api_key=False):
    if 'SETTINGS' in storage:
        SETTINGS = json.loads(storage['SETTINGS'])
    else:
        SETTINGS = {
            'api': '',
            'music': False,
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
            f'https://meme-api.com/gimme/{random.choice(subreddits)}/{count}',
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
    global CALCULATING, CRASH 
    CALCULATING = False
    if not CRASH:
        CRASH = True
        document['listout'].html = ''
    document['listout'] <= html.H1('An Exception Has Occurred...') + html.PRE(html.CODE(e))
    return None

def sync_server(data):
    print(32)
    def update_badge(response):
        document['badge-image'].src = f"{SERVER}/badge/{data['USER']['id']}{window.location.search}"
        document['svg_badge-image'].src = f"{SERVER}/svg/{data['USER']['id']}{window.location.search}" 
    print(33)
    response = []
    ajax.get(
        data['USER']['avatar'],
        blocking=True,
        mode="binary",
        oncomplete=response.append
    )
    print(34)
    image_data = response[-1].read()
    print(40)
    try:
        image_data = base64.b64encode(image_data)
    except:
        image_data = b'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'
    print(41)
    image_data = image_data.decode() 
    print(42)
    data['CARD']['UserAvatarB64'] = image_data 
    print(35)
    ajax.post(
        f'{SERVER}/update/{data["USER"]["id"]}',
        data=json.dumps({data["USER"]["id"]: list(data['CARD'].values())}),
        headers={
            'UserID': str(data["USER"]["id"]), 
            'Content-type':'application/json',
        },
        oncomplete=update_badge,
    )
    print(36)

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
        global start, CALCULATING, CUSTOM
    
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

        api.send(json.dumps({'user': user, 'KEY': settings()['api'], 'CWD': os.getcwd(), 'CACHE': dict(storage), 'CUSTOM': CUSTOM}))
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
        #print(data)
        if 'ERROR' in data:
            return err(data['ERROR'])
        print(30)
        document['listout'].html = '' 
        print(31)
        sync_server(data)
        print(10)
        dump = HTML(data)
        print(1)
        document['listout'] <= html.DIV(dump.dump_data())
        dump.bind_modal()

        document['time-taken'].text = str(round(time.time() - start, 3)) + ' seconds'
    except:
        err(traceback.format_exc())


try:
    SERVER = 'https://roamingcookie.pythonanywhere.com'
    CRASH = False
    
    document["username-input-button"].bind("click", main_handle)
    document["settings-button"].bind("click", lambda event: settings(show=True))
    document["settings-save"].bind("click", lambda event: settings(save=True))
    document["body"].bind('click', music_toggle)
    document["body"].bind('scrol', music_toggle)
    document["login-key-button"].bind('click', api_login)
    document['username-input-box'].bind('keyup', lambda event: main_handle(event) if event.which == 13 else None)
    
    try:
        with open(os.path.join(os.getcwd(), 'static', 'relations.yaml')) as f:
            CUSTOM = window.jsyaml.load(f.read())
            if not isinstance(CUSTOM, list):
                CUSTOM = []
    except:
        CUSTOM = []
    
    toggle_css()

    if window.location.hash.startswith('#access_token='):
        token = dict([i.split('=') for i in window.location.hash[1:].split('&')])['access_token']
        settings(save=True, api_key=token)
        settings(show=True)

    if 'user' in document.query:
        user = document.query['user']
        if isinstance(user, list):
            user = user[-1]
        main_handle(None, userName=user)

except:
    err(traceback.format_exc())




document['load-content'].style.display = 'none'
document['main-content'].style.display = 'block'
