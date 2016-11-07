# -*- coding: utf-8 -*-
{
    'name': "Facebook Messenger Base",
    'author': "Damien Bouvy",
    'summary': "Basic Facebook Messenger integration.",
    'description': """
This module adds the minimum necessary routes to create a new bot on Facebook Messenger.
If no other modules extends the bot's scopes, the bot simply says an introductory message
then repeats what you say to it.
    """,
    'version': '1.0',
    'depends': ['web', 'base_setup'],
    'data': ['views/fb_bot_views.xml'],
}
