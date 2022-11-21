from flask import Flask, send_file, request, redirect, send_from_directory, jsonify
from urllib.parse import urlencode
import os
import re
import json
import base64
from io import BytesIO

PATH = '/home/RoamingCookie/cookielist'
URL = 'https://roamingcookie.github.io/'
ICON = 'data:image/svg+xml;base64,' + base64.b64encode(open(os.path.join(PATH, 'image', 'anilist.svg')).read().encode()).decode()
SVG = open(os.path.join(PATH, 'image', 'default.svg')).read()
ALLOWED_ADDR = ['https://roamingcookie.github.io', 'https://roamingcookie.github.io/', 'roamingcookie.github.io']
SELF = 'https://roamingcookie.pythonanywhere.com'

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
        'AnimeWatched',
        'TitleWatched',
        'EpisodeWatched',
        'MinutesWatched',
        'WatchTime',
        'UnwatchDropped',
        'UnwatchNotReleased',
        'UnwatchAiring',
        'UnwatchPlausible',
        'TotalUnwatch',
    ]
    if parameter and data:
        return json.loads(data)
    try:
        with open(filePath(userid), 'r') as userFile:
            userData = json.loads(userFile.read())[userid]
            return dict(zip(keys, userData))
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
    data = get_data(userid, request.args.get('data', {}))
    badgeArgs = {}

    badgeArgs['style'] = 'for-the-badge'
    badgeArgs['color'] = 'ff69b4'
    badgeArgs['logo'] = ICON
    badgeArgs['message'] = 'Watched {& AnimeWatched &} Anime'
    badgeArgs['label'] = data.get('UserName', '')

    if not data:
        badgeArgs['label'] = 'You need to at least once visit'
        badgeArgs['message'] = f'{URL}?user=%23{userid}'

    badgeArgs.update(request.args)
    badgeArgs['message'] = replace(badgeArgs['message'], data)

    if request.args.get('png', 'false').lower() == 'true':
        subdomain = 'raster'
    else:
        subdomain = 'img'

    return redirect(f'https://{subdomain}.shields.io/static/v1' + ("?" + urlencode(badgeArgs) if badgeArgs else ''))


@app.route('/svg/<string:userid>', methods=['GET'])
def svg(userid):
    data = get_data(userid, request.args.get('data', {}))
    svg_content = replace(request.args.get('svg', SVG), data)

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

@app.route('/status', methods=['GET'])
def status():
    return str(request.remote_addr)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with, UserID"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, OPTIONS, PATCH, POST, PUT"
    return response