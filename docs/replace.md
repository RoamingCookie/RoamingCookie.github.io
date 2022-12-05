# Data Replace Guide

enables JINJA with the following variables
these can be put inside `/badge?message=` and `/svg?svg=` [endpoints](/docs/endpoint.md)

these variables are suported
{% raw %}
```{{ UserId }}```   -   AniList ID of the user

```{{ UserName }}```   -   AniList User Name of the user

```{{ UserSiteUrl }}```   -   users anilist profile link

```{{ UserAvatar }}```   -   anilist user avatar

```{{ UserAvatarB64 }}```   -   base64 encoded UserAvatar image to use inside SVG data uri image

```{{ AnimeWatched }}```   -   total number of anime watched (calculated)

```{{ TitleWatched }}```   -   number of titles watched (displayed on anilist)

```{{ EpisodeWatched }}```   -   number of episodes watched

```{{ MinutesWatched }}```   -   minutes watched

```{{ WatchTime }}```   -   watch time (formated to days or hours accordingly)

```{{ UnwatchDropped }}```   -   unwatched anime series (in accordance to series watched) which are marked as dropped

```{{ UnwatchNotReleased }}```   -   unwatched anime series (in accordance to series watched) which are not released yet

```{{ UnwatchAiring }}```   -   unwatched anime series (in accordance to series watched) which are marked as dropped

```{{ UnwatchPlausible }}```   -   unwatched anime series (in accordance to series watched) which are either not in list or marked as planning

```{{ TotalUnwatch }}```   -   total number of unwatched anime series (in accordance to series watched)

```{{ LastUpdateTimestamp }}```   -   timestamp of when the data at server were updated last

```{{ LastUpdated }}```   -   LastUpdateTimestamp but formated to human readable format

{% endraw %}
