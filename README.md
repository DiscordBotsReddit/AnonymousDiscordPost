# AnonymousDiscordPost
Allows users to send anonymous posts to a channel you set.  Option for a 'mod_channel' that outputs the non-anonymous version.

## Setup
All commands are slash commands.  To be able to use the slash commands if you self-host this bot, you must set the `PREFIX` in `config.json` to whatever you want (By default, it is set to `anon>`), then run `anon>sync` in your server.  This command only needs to be ran once at the start of your bot in your server.

`/setup` contains the 2 commands to `set_anonymous_channel`(required) and `set_mod_channel`(optional)

If you set a mod channel, a non-anonymous version of `anon_post`s will be sent to that channel.  *USERS ARE NOTIFIED IF THIS HAPPENS*

## Use
`/anon_post content` sends whatever is in the `content` variable as an embed to the channel you specify in `set_anonymous_channel`.  No identifying information is sent, other than users may see the `User is typing...` notification by the chat bar.  No way to hide this with this implementation.
