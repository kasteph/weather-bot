weather-bot
---------------
For Zulip. translation-bot's sibling. Made with [Victor Felder](http://github.com/vhf).

Uses [forecast.io](http://forecast.io) for getting the weather and [geocoder](https://github.com/DenisCarriere/geocoder)
for geocoding the locations.

usage
-----
`@**Weather** [when] in [location]` or `weather [when] in [location]` where `[when]`
is `now`, `today`, `tomorrow`, or `week`, and `location` is the name of the place.

If the query is only `@**Weather**`, `weather`, or `[@**Weather**|weather] [when]`,
it defaults to returning the weather of 455 Broadway, New York, NY.

[!Screenshot](http://i.imgur.com/YcOKZcV.png)
