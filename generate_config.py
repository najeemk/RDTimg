import json

# listens for the client input
client_id = input("Enter your client_id: ")
client_secret = input("Enter your client_secret: ")
user_agent = 'imagine_client'

settings = {
    'cache_size': 10,
    'cache_location': 'cache/',
    'default_sub': 'wallpapers',
    "subreddits": ["wallpapers", "earthporn", "cozyplaces"]
}
praw_auth = {
    'client_id' : client_id,
    'client_secret' : client_secret,
    'user_agent' : user_agent
}

# generates master json
config_json = {
    "settings" : settings,
    "praw_auth" : praw_auth
}

# writes to JSON
with open("config/config.json", "w") as p: 
     json.dump(config_json, p, indent=4)