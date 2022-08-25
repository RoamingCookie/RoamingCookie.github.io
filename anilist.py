import time
from browser import ajax
from datetime import datetime
import sys
from browser import document

def cprint(string):
    console = document["console"]
    out = console.html + '<br><pre><code>' + str(string) + '</code></pre>'
    console.html += out

ANIME = []

def catbox(url):
    out = []
    response_g = ajax.post(
        'https://catbox.moe/user/api.php',
        blocking=True,
        data={
            'reqtype': 'urlupload',
            'url': url,
            },
        oncomplete=out.append
    )
    return out[-1].text

def get_user_completed(user, stat='COMPLETED'):
    query = '''query($page:Int,$userName:String){Page(page:$page){pageInfo{total perPage currentPage lastPage hasNextPage}mediaList(userName:$userName,status:''' + stat + '''){media{id startDate{year month day}title{romaji english}format episodes relations{nodes{id format}edges{relationType node{id format}}}}}}}'''
    resx = []
    response_g = ajax.post(
        'https://graphql.anilist.co',
        blocking=True,
        mode="json",
        data={
            'query': query,
            'variables': '{"userName": "' + user + '","page": 1}'
            },
        oncomplete=resx.append
    )
    response = resx[-1].json
    for i in range(2, response['data']['Page']['pageInfo']['lastPage'] + 1):
        ani_res = ajax.post(
            'https://graphql.anilist.co',
            blocking=True,
            mode="json",
            data={
                'query': query,
                'variables': '{"userName": "' + user + '","page": ' + str(i) + '}'
            },
            oncomplete=resx.append
        )
        ani_res = resx[-1].json
        response['data']['Page']['mediaList'].extend(
            ani_res['data']['Page']['mediaList']
        )
        if not ani_res['data']['Page']['pageInfo']['hasNextPage']:
            break
        
    response = response['data']['Page']['mediaList']
    res = {}
    
    for i in response:
        i = i['media']
        
        try:
            startDate = time.mktime(
                datetime(
                    i['startDate']['year'],
                    i['startDate']['month'],
                    i['startDate']['day'],
                ).timetuple()
            )
        except:
            startDate = float('inf')
        
        res[str(i['id'])] = {
            'start': startDate,
            'title': i['title']['english'] if i['title']['english'] else i['title']['romaji'],
            'format': i['format'],
            'relations': [str(n['id']) for n in i['relations']['nodes'] if n['format'] in ['TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']],
        }

    return res

def get_tree(id, recur = []):
    out = ANIME[id]['relations']
    recur.append(id)
    for i in ANIME[id]['relations']:
        if (i in ANIME) and (i not in recur):
            out.extend(get_tree(i, recur))
    out = sorted(list(set(out)), key = lambda z: ANIME.get(z, {'start': float('inf')})['start'])
    return out

def get_ani_season_one(tree):
    out = -1
    for i in tree:
        out = out + 1
        if i in ANIME:
            if ANIME[i]['format'] == 'TV':
                return out
    return 0

def get_anime_stats(id):
    tree = list(set([id] + get_tree(id)))
    out = {
        'name': ANIME[id]['title'],
        'TV': 0,
        'TV_SHORT': 0,
        'MOVIE': 0,
        'SPECIAL': 0,
        'OVA': 0,
        'ONA': 0,
        'MUSIC': 0,
        'NONE': 0,
    }
    for i in tree:
        if i in ANIME:
            try:
                out[ANIME[i]['format']] = out[ANIME[i]['format']] + 1
            except:
                pass
    del out['NONE']
    _out = out.copy()
    for n,v in out.items():
        if v == 0:
            del _out[n]
    if (len(_out) == 2):
        for i in _out:
            if i not in ['name', 'TV']:
                _out[i] = ''
    return _out

def process_overwrite():
    global _ANIME, overwrite
    _ANIME = ANIME.copy()
    overwrite = { }
    for i in ANIME:
        tree = get_tree(i)
        k = get_ani_season_one(tree)
        if len(tree) != 0:
            if tree[k] in overwrite:
                try:
                    tree.remove(overwrite[tree[k]])
                except ValueError:
                    pass
                if overwrite[tree[k]]:
                    tree = [overwrite[tree[k]]] + tree
            for n in (tree[:k] + tree[k + 1:]):
                if n in _ANIME:
                    del _ANIME[n]

def create_list():
    global ListData
    ListData = []
    for i in _ANIME:
        ani = get_anime_stats(i)
        sdata = ' '.join([
                '',
                '|',
                str(ani.get('TV', '')) + 'S' if 'TV' in ani else '',
                str(ani.get('MOVIE', '')) + 'MOVIE' if 'MOVIE' in ani else '',
                str(ani.get('TV_SHORT', '')) + 'SHORT' if 'TV_SHORT' in ani else '',
                str(ani.get('OVA', '')) + 'OVA' if 'OVA' in ani else '',
                str(ani.get('ONA', '')) + 'ONA' if 'ONA' in ani else '',
                str(ani.get('SPECIAL', '')) + 'SPE' if 'SPECIAL' in ani else '',
                str(ani.get('MUSIC', '')) + 'MUSIC' if 'MUSIC' in ani else '',
            ]).split()
        data = overwrite.get(ani['name'], ani['name']) + ' ' + ' '.join(sdata)
        if len(sdata) > 1:
            ListData.append(data)

def process_save_data(user):
    global anime_data, HEADING, sorted_anime_dict, md
    raw_anime_data = '\n'.join(sorted(ListData, key=lambda s: s.upper())).splitlines()
    md = ''
    HEADING = f'Watched Anime (@{user})'
    inf = '0'
    anime_data = {}
    for i in raw_anime_data:
        if not (i.strip().startswith('|') or len(i.strip()) == 0):
            anime_data[i.split('|')[0].strip()] = i.split('|')[1].strip()
    sorted_anime_dict = {}
    for i in [inf] + list('abcdefghijklmnopqrstuvwxyz'):
        sorted_anime_dict[i] = []
    for i in anime_data:
        if i[0].lower() in sorted_anime_dict:
            sorted_anime_dict[i[0].lower()].append(i)
        else:
            sorted_anime_dict[inf].append(i)  
    for n,v in sorted_anime_dict.items():
        sorted_anime_dict[n] = sorted(v)
    for n,v in sorted_anime_dict.items():
        x = []
        for i in v:
            x.append((i,'-'.join(anime_data[i].split())))
        sorted_anime_dict[n] = x

def gen_md():
    global md
    nx = '\n'
    md = md + f'<h1> {HEADING} - ' + str(len(anime_data)) + '</h1>' + nx
    for n,v in sorted_anime_dict.items():
        if len(v) != 0:
            md = md + '<h6>' + n.upper() + ' - ' + str(len(v)) + '</h6>' + nx
            md = md + '<ul>'
            for i in v:
                md = md + '<li><em>' + i[0] + '</em> - <strong>' + i[1] + '</strong>' + '</li>' + nx
            md = md + '</ul>'
            if n.upper() != 'Z': md = md + nx + '<hr>' + nx


def get_user_list(user):
    global ANIME, md
    ANIME = {}
    ANIME.update(get_user_completed(user), stat='COMPLETED')
    ANIME.update(get_user_completed(user, stat='REPEATING'))
    del ANIME['stat']
    process_overwrite()
    create_list()
    process_save_data(user)
    gen_md()
    url = f'https://raster.shields.io/badge/@{user}-Anime%20Watched-blueviolet?link=https://roamingcookie.github.io/?user={user}&style=for-the-badge&logoWidth=20&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAACXBIWXMAAAsSAAALEgHS3X78AAABCFBMVEVHcEz8/f4Eqf4Dqf7///7+/v7+/v4CqP/+/v79/f3+/v4Apf/q9/4Cqf8Ao/8AqP/+/v7+/v79/f35/P4Eqf4Fqv5uzf4Fqf4CqP/8/f79/f3+/v4CqP8Ao/8BqP8Aov///v77/f7+/v7+/v7y+v79/f0Cqf4Trv4CqP+B0/4Cqf4Ap/8AqP////7+/v7+/v7+/v79/f39/f79/f0Apf8AqP8ZsP5ty/4LrP73+/7+/v7g8/79/f0Apv/d8/77/f4Ajv8Ao//5/P7+/v4Fqv74/P6Z2/79/f35/P7///37/f3///1Bvv79/f0Aif/7/f7///8FvP8Aqv9Oyf81vf/+//+F1//X9f/JT/BYAAAAUHRSTlMAAQIBAgMBAQICGgEBFQIBOkgDAiApAjWSGQUpdjICJTS/Le4b1/ElAzPo2BE3Eot+Af438vAkB+Am0N/QJfvpMfDx0fEN8bpt8c377+EhLfyOTzcAAACSSURBVAjXY2AAAkYWHm5mBlxAUkFFXpQfzlUMsDZVE2FgB7E5GZSMAkJDTNQhXFYGgwAn7zBHMwiXwdAqwMMz3MWWQQOs1jjA1985wMcPLCfEoB8AAm4O5jpyQL6UaoCNu1eAnYW2lgyQKxigrMfgah8QHBQoAeRyCUgDTbfU1ZQV58V0IRsHB5AUZhHjY2JnAABRiROEPw2AbwAAAABJRU5ErkJggg=='
    url = catbox(url)
    md = md + f'''
    <br><br>
    <h1>Put These inside Your AniList Bio's</h1>
    <pre><code>[![@{user}]({url})](https://roamingcookie.github.io/?user={user})</code></pre>
    <a href="https://roamingcookie.github.io/?user={user}"><img src={url}></a>
    <br>
    or create your own by using any other image with this link <a href="https://roamingcookie.github.io/?user={user}">https://roamingcookie.github.io/?user={user}</a>
    '''
    return md