# Data Replace Guide

enables [JINJA](https://documentation.bloomreach.com/engagement/docs/jinja-syntax) with the following variables
these can be put inside `/badge?message=` and `/svg?svg=` [endpoints](/docs/endpoint.md)

these variables are suported

{% raw %}

```{{ UserId }}```   -   AniList ID of the user

```{{ UserName }}```   -   AniList User Name of the user

```{{ UserSiteUrl }}```   -   users anilist profile link

```{{ UserAvatar }}```   -   anilist user avatar

```{{ UserAvatarB64 }}```   -   base64 encoded UserAvatar image to use inside SVG data uri image

```{{ AnimeWatched }}```   -   total number of anime watched (calculated)

```{{ MangaRead }}```   -   total number of manga read (calculated)

```{{ TitleWatched }}```   -   number of titles watched (displayed on anilist)

```{{ TitleRead }}```   -   number of titles read (displayed on anilist)

```{{ EpisodeWatched }}```   -   number of episodes watched

```{{ ChaptersRead }}```   -   number of chapters read

```{{ MinutesWatched }}```   -   minutes watched

```{{ MinutesRead }}```   -   minutes read (average)

```{{ WatchTime }}```   -   watch time (formated to days or hours accordingly)

```{{ ReadTime }}```   -   read time (formated to days or hours accordingly)

```{{ UnwatchDropped }}```   -   unwatched anime series (in accordance to series watched) which are marked as dropped

```{{ UnReadDropped }}```   -   unread manga series (in accordance to series read) which are marked as dropped

```{{ UnwatchNotReleased }}```   -   unwatched anime series (in accordance to series watched) which are not released yet

```{{ UnReadNotReleased }}```   -   unread manga series (in accordance to series read) which are not released yet

```{{ UnwatchAiring }}```   -   unwatched anime series (in accordance to series watched) which are currently airing

```{{ UnReadAiring }}```   -   unread manga series (in accordance to series read) which are currently airing

```{{ UnwatchPlausible }}```   -   unwatched anime series (in accordance to series watched) which are either not in list or marked as planning

```{{ UnReadPlausible }}```   -   unread manga series (in accordance to series read) which are either not in list or marked as planning

```{{ TotalUnwatch }}```   -   total number of unwatched anime series (in accordance to series watched)

```{{ TotalUnRead }}```   -   total number of unread manga series (in accordance to series read)

```{{ LastUpdateTimestamp }}```   -   timestamp of when the data at server were updated last

```{{ LastUpdated }}```   -   LastUpdateTimestamp but formated to human readable format

{% endraw %}
