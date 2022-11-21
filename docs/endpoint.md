# ENDPOINTS


location at which api is present at [roamingcookie.pythonanywhere.com](https://roamingcookie.pythonanywhere.com), only HTTPS

<br><br>

# `/json/<string:userid>`
returns the data about the user stored at server in json format

<br><br>

# `/view/<string:userid>`
redirects to [jsonhero](https://jsonhero.io/) editor with the stored json data

<br><br>

# `/badge/<string:userid>`
redirects to [shields io](https://shields.io/) with provide and default parameters
allowed parapeters

`?message=` message on the right side supports [data replace](/docs/replace)

`?style=for-the-badge`  for-the-badge, social, flat-square, flat, plastic

`?label=default` Override the default left-hand-side text (URL-Encoding needed for spaces or special characters!)

`?logo=http://image` Insert one of the named logos from (bitcoin, dependabot, gitlab, npm, paypal, serverfault, stackexchange, superuser, telegram, travis) or simple-icons. Simple-icons are referenced using icon slugs which can be found on the simple-icons site or in the slugs.md file in the simple-icons repository.

`?logo=data:image/png;base64,…`	Insert custom logo image (≥ 14px high). There is a limit on the total size of request headers we can accept (8192 bytes). From a practical perspective, this means the base64-encoded image text is limited to somewhere slightly under 8192 bytes depending on the rest of the request header.

`?logoColor=ffffff` Set the color of the logo (hex, rgb, rgba, hsl, hsla and css named colors supported). Supported for named logos but not for custom logos.

`?logoWidth=40`	Set the horizontal space to give to the logo

`?link=http://left&link=http://right` Specify what clicking on the left/right of a badge should do. Note that this only works when integrating your badge in an<object> HTML tag, but not an<img> tag or a markup language.

`?labelColor=abcdef` Set background of the left part (hex, rgb, rgba, hsl, hsla and css named colors supported). The legacy name "colorA" is also supported.

`?color=fedcba`	Set background of the right part (hex, rgb, rgba, hsl, hsla and css named colors supported). The legacy name "colorB" is also supported.

<br><br>

# `/svg/<string:userid>`
returns SVG after repacing with [data replace](/docs/replace)

`?svg=URL_encoded_SVG_data` your valid svg file URL encoded