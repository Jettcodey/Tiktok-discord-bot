# Tiktok-discord-bot
A simple Discord bot that Scans a Discord channel for TikTok links and shows/saves them in a downloadable text file.

## Slash Commands

- `/search`: Kind of useless but still included, does almost the same as `/txt`.

- `/txt`: Searches by default 1000 messages for any TikTok link and puts them in a downloadable text file.

- `/download`: Give a link to a TikTok post and it will post the direct link to download them in the channel.


## Permissions

It should work with just the following permissions:
- 'Read Messages/View Channels'
- 'Read Message History'
- 'Send Messages'
- 'Manage Roles'
- 'Attach Files'
- 'Use Slash Commands'

Or just give it admin Permisions ;D (in a Private server ofc)

## Roadmap

- [x] Send Single Downloaded Video/Image Posts Without Watermark in Channel.
- [ ] Automatically generating a text file after a Specified amount of time has passed.
- [ ] Handle multiple request at once.

## Known Issues
Using the `/download` command with a Photo post sends a `"Media URL: None"` before sending all images in the channel.
