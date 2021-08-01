from os import join, abspath, curdir

code_file = open(join(abspath(curdir), 'auth_code.txt'), 'r')

spotify_token = code_file.read()

spotify_user_id = "sinistersandwich"

# Recent Song Documentation: https://developer.spotify.com/documentation/web-api/reference/player/get-recently-played/

