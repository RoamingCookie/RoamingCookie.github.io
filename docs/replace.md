# Data Replace Guide

replaces the following text which matches this regex (DOTALL and CASEINSENSETIVE enabled)

```regex
((?<!\\)\{(?<!\\)&(\s+)?(.*?)(\s+)?(?<!\\)&(?<!\\)\})
```

ie. in this format `{& VARIABLE_NAME &}` every thing between `{&` and `&}`

these can be put inside `/badge?message=` and `/svg?svg=` [endpoints](/docs/endpoint.md)

these variables are suported

```{& UserId &}```   -   AniList ID of the user

```{& UserName &}```   -   AniList User Name of the user

```{& UserSiteUrl &}```   -   users anilist profile link

```{& UserAvatar &}```   -   anilist user avatar

```{& AnimeWatched &}```   -   total number of anime watched (calculated)

```{& TitleWatched &}```   -   number of titles watched (displayed on anilist)

```{& EpisodeWatched &}```   -   number of episodes watched

```{& MinutesWatched &}```   -   minutes watched

```{& WatchTime &}```   -   watch time (formated to days or hours accordingly)

```{& UnwatchDropped &}```   -   unwatched anime series (in accordance to series watched) which are marked as dropped

```{& UnwatchNotReleased &}```   -   unwatched anime series (in accordance to series watched) which are not released yet

```{& UnwatchAiring &}```   -   unwatched anime series (in accordance to series watched) which are marked as dropped

```{& UnwatchPlausible &}```   -   unwatched anime series (in accordance to series watched) which are either not in list or marked as planning

```{& TotalUnwatch &}```   -   total number of unwatched anime series (in accordance to series watched)