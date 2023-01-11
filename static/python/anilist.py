import json
import os
import random
import time
import traceback
import javascript
from urllib.parse import urlencode
import base64

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
                
                
        self.manga = {key.upper(): dict()
                      for key in [dictionary[0]] + dictionary[1]}
        for iD, media in data['DATA']['MANGA'].items():
            title_key = media[iD]['title'][0].upper()
            if not title_key in self.manga:
                title_key = dictionary[0]
            self.manga[title_key][iD] = media
            
        for key, value in self.manga.copy().items():
            if not value:
                del self.manga[key]
            else:
                self.manga[key] = dict(sorted(value.items(), key=lambda k: k[1][k[0]]['title'].lower()))
       
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
        yield self.listout_header()
        yield html.DIV(html.H1(f"@{self.data['USER']['name']} Watched {self.data['USER']['count']['anime']} Anime & Read {self.data['USER']['count']['manga']} Manga"), Class="output")
        yield html.BR()
        yield html.DIV(self.stat_out(), Class="stats")
        yield html.BR()
        yield html.DIV(self.list_out(), Class="output")
        yield html.BR()
        yield html.TABLE(self.misc_out(), Class="output misc-data")
        yield html.BR()
        yield html.CENTER(html.TABLE(self.unwatch_out(), Class="output"))
        yield html.BR()
        yield html.CENTER(html.TABLE(self.unwatch(), Class="output unwatch-list"))
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
    def update_badge(response):
        document['badge-image'].src = f"{SERVER}/badge/{data['USER']['id']}{window.location.search}"
        document['svg_badge-image'].src = f"{SERVER}/svg/{data['USER']['id']}{window.location.search}" 
    
    response = []
    ajax.get(
        data['USER']['avatar'],
        blocking=True,
        mode="binary",
        oncomplete=response.append
    )
    data['CARD']['UserAvatarB64'] = base64.b64encode(response[-1].read()).decode()
    
    ajax.post(
        f'{SERVER}/update/{data["USER"]["id"]}',
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

        if 'ERROR' in data:
            return err(data['ERROR'])
        
        document['listout'].html = '' 
        sync_server(data)
        
        dump = HTML(data)

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
