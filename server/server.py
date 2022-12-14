from flask import Flask, send_file, request, redirect, send_from_directory, jsonify, render_template_string
from urllib.parse import urlencode
import os
import re
import json
import base64
import datetime
import time
from io import BytesIO

PATH = '/home/RoamingCookie/cookielist'
URL = 'https://roamingcookie.github.io'
ICON = 'data:image/svg+xml;base64,' + base64.b64encode(open(os.path.join(PATH, 'image', 'anilist.svg')).read().encode()).decode()
SVG = open(os.path.join(PATH, 'image', 'default.svg')).read()
ALLOWED_ADDR = ['https://roamingcookie.github.io', 'https://roamingcookie.github.io/', 'roamingcookie.github.io']
SELF = 'https://roamingcookie.pythonanywhere.com'
MAINTENANCE = False

app = Flask(__name__)
regex = re.compile(r"((?<!\\)\{(?<!\\)&(\s+)?(.*?)(\s+)?(?<!\\)&(?<!\\)\})", re.DOTALL)

def replace(string, data):
    data = {k.upper():str(v) for k,v in data.items()}
    substitution = lambda match: data.get(match.group(3).replace('\n', '').replace(' ', '').upper(), '')
    return regex.sub(substitution, string)

filePath = lambda userid: os.path.join(PATH, 'count', str(userid) + '.json')

def get_data(userid, data, parameter=True):
    keys = [
        'UserId',
        'UserName',
        'UserSiteUrl',
        'UserAvatar',
        'UserAvatarB64',
        'AnimeWatched',
        'MangaRead',
        'TitleWatched',
        'TitleRead',
        'EpisodeWatched',
        'ChaptersRead',
        'MinutesWatched',
        'MinutesRead',
        'WatchTime',
        'ReadTime',
        'UnwatchDropped',
        'UnReadDropped',
        'UnwatchNotReleased',
        'UnReadNotReleased',
        'UnwatchAiring',
        'UnReadAiring',
        'UnwatchPlausible',
        'UnReadPlausible',
        'TotalUnwatch',
        'TotalUnRead',
        'LastUpdateTimestamp',
    ]
    if parameter and data:
        return json.loads(data)
    try:
        with open(filePath(userid), 'r') as userFile:
            userData = json.loads(userFile.read())[userid]
            output = dict(zip(keys, userData))
            update_ago = time.time() - output['LastUpdateTimestamp']
            ago = '{} {}'
            if update_ago < (60):
                ago = ago.format(int(update_ago), "second")
            elif update_ago < (60 * 60):
                ago = ago.format(int(update_ago/(60)), "minute") 
            elif update_ago < (60 * 60 * 24):
                ago = ago.format(int(update_ago/(60 * 60)), "hour")  
            else:
                ago = ago.format(int(update_ago/(60 * 60 * 24)), "day")
            output['LastUpdated'] = ago
            return output
    except Exception:
        return {}

@app.route('/')
def index():
    return redirect(URL + ("?" + urlencode(request.args) if request.args else ""))

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(PATH, 'image'), 'favicon.ico')

@app.route('/json/<string:userid>', methods=['GET'])
def Json(userid):
    data = get_data(userid, request.args.get('data', {}))
    if not data:
        return jsonify({'error': f'you need to at least once visit {URL}?user=%23{userid}'})
    return jsonify(data)

@app.route('/view/<string:userid>')
def view(userid):
    data = get_data(userid, request.args.get('data', {}))
    if not data:
        return f'<html><h1>you need to at least once visit <a href="{URL}?user=%23{userid}">{URL}?user=%23{userid}</a></h1></html>'
    return redirect('https://jsonhero.io/new?' + urlencode({'url': f'{SELF}/json/{userid}'}))

@app.route('/badge/<string:userid>', methods=['GET'])
def badge(userid):
    if MAINTENANCE:
        return redirect(f'{SELF}/maintenance')
    data = get_data(userid, request.args.get('data', {}))
    badgeArgs = {}

    badgeArgs['style'] = 'for-the-badge'
    badgeArgs['color'] = 'ff69b4'
    badgeArgs['logo'] = ICON
    badgeArgs['message'] = 'Anime: {{ AnimeWatched }} | Manga: {{ MangaRead }}'
    badgeArgs['label'] = data.get('UserName', '')
    badgeArgs['link'] = f'https://anilist.co/user/{userid}'
    
    if not data:
        badgeArgs['label'] = 'You need to at least once visit'
        badgeArgs['message'] = f'{URL}?user=%23{userid}'

    badgeArgs.update(request.args)
    badgeArgs['message'] = render_template_string(badgeArgs['message'], **data)

    if request.args.get('png', 'false').lower() == 'true':
        subdomain = 'raster'
    else:
        subdomain = 'img'

    return redirect(f'https://{subdomain}.shields.io/static/v1' + ("?" + urlencode(badgeArgs) if badgeArgs else ''))


@app.route('/svg/<string:userid>', methods=['GET'])
def svg(userid):
    if MAINTENANCE:
        return redirect(f'{SELF}/maintenance')
    jinja_data = {k[5:]:v for k,v in dict(request.args).items() if k.startswith('jinja_')}
    data = get_data(userid, request.args.get('data', {}))
    svgdata = request.args.get('svg', SVG)
    if svgdata == 'default':
        svgdata = SVG
        
    svg_content = render_template_string(svgdata, **data)

    if not data:
        svg_content =f'<svg xmlns="http://www.w3.org/2000/svg" height="90"><text x="10" y="20" style="fill:red;">you need to at least once visit {URL}?user=%23{userid}</text></svg>'

    svg_io = BytesIO()
    svg_io.write(svg_content.encode())
    svg_io.seek(0)

    return send_file(svg_io, mimetype='image/svg+xml', download_name=userid + ".svg")

@app.route('/update/<string:userid>', methods=['GET', 'POST'])
def update(userid):
    if request.method == 'GET':
        return redirect(URL)

    data = json.dumps(request.json)
    UserID = str(request.headers['UserID'])

    if UserID != userid:
        return 'UserID Header Not Present', 401

    if request.headers.get('Origin', '') not in ALLOWED_ADDR:
        return 'Invalid Origin', 401

    try:
        with open(filePath(userid), 'w') as userFile:
            userFile.write(data)
        return 'Success', 200
    except Exception:
        return 'Too Many Request', 529

@app.route('/placeholder/<string:user>', methods=['GET'])
def status(user):
    badgeArgs = {}
    badgeArgs['style'] = 'for-the-badge'
    badgeArgs['color'] = 'ff69b4'
    badgeArgs['logo'] = ICON
    badgeArgs['message'] = 'Watched [LOADING] Anime'
    badgeArgs['label'] = f'@{user}'
    return redirect(f'https://img.shields.io/static/v1' + ("?" + urlencode(badgeArgs) if badgeArgs else ''))

@app.route('/maintenance', methods=['GET'])
def maintenance():
    badgeArgs = {}
    badgeArgs['style'] = 'for-the-badge'
    badgeArgs['color'] = 'f71631'
    badgeArgs['logo'] = ICON
    badgeArgs['message'] = 'server is under a maintenance break'
    badgeArgs['label'] = 'MAINTENANCE'
    return redirect(f'https://img.shields.io/static/v1' + ("?" + urlencode(badgeArgs) if badgeArgs else ''))

@app.route('/users', methods=['GET'])
def users():
    user_html = list(map(lambda user: f'<br><a href="https://anilist.co/user/{user}" target="_blank"><object type="image/svg+xml" data="{SELF}/badge/{user}?jinja_b64=false"></object></a><br>', map(lambda name: name[:-5], sorted(filter(lambda name: name.endswith('.json'), os.listdir(os.path.join(PATH, 'count'))), key=lambda name: os.path.getmtime(os.path.join(PATH, 'count', name)), reverse=True))))
    return ''.join(['<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>', f'<center><font face="sans-serif" color="#666666"><h1>{len(user_html)} Users</h1></font></center>', *user_html, '</html></body>'])
    
@app.route('/userids', methods=['GET'])
def userids():
    data = list(map(lambda user: str(user), map(lambda name: name[:-5], sorted(filter(lambda name: name.endswith('.json'), os.listdir(os.path.join(PATH, 'count'))), key=lambda name: os.path.getmtime(os.path.join(PATH, 'count', name)), reverse=True))))
    return jsonify({'users': data})
    
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with, UserID"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, OPTIONS, PATCH, POST, PUT"
    return response
