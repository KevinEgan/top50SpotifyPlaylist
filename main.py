import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

# enter your details here
CLIENT_ID = ""
CLIENT_SECRET = ""

song_artist_dict = {}
song_uris = []


def validate_date(date_string):
    # regex pattern for DD-MM-YYYY format
    pattern = r'^\d{2}-\d{2}-\d{4}$'

    # Check if the input matches the pattern
    if re.match(pattern, date_string):
        # validate user's date
        day, month, year = map(int, date_string.split('-'))

        if day < 1 or day > 31:
            return False

        if month < 1 or month > 12:
            return False

        # Chart data goes back as far as 14-11-1952
        if datetime(year, month, day) < datetime(1952, 11, 14):
            print("No music chart data available before 14-11-1952 :( ")
            return False

        return True

    return False


# take in user input
usr_date = input("Enter a date (DD-MM-YYYY): ")

# proceed once user's date is valid
while not validate_date(usr_date):
    print("Invalid date.")
    usr_date = input("Please try again (DD-MM-YYYY): ")

# format user's date so it can be implemented into the url
format_date = usr_date.split("-")
reverse_string = "".join(format_date[::-1])

irish_charts_url = f"https://www.officialcharts.com/charts/singles-chart/{reverse_string}/7501/"

response = requests.get(irish_charts_url)
irish_charts_website = response.text

soup = BeautifulSoup(irish_charts_website, "html.parser")

x = soup.find_all('div', class_="title-artist")

# extract songs and artists from redundant information & white space
for anchor in x:
    temp_songs = anchor.get_text().replace("\n", " ")
    list_temp_songs = temp_songs.split("  ")
    song_artist_dict[list_temp_songs[1]] = list_temp_songs[2].strip()

# authorisation step
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                                    redirect_uri="http://example.com", scope="playlist-modify-public user-library-modify",
                                                    show_dialog=True, cache_path="token.txt"
                                                    ))

user_id = spotify.current_user()["id"]

# pp = pprint.PrettyPrinter(indent=1)

# using songs and artists from webscrape, obtain uris. Prettyprint comes in handy when trying to extract uris from
# the quantity of information returned from the search
for key, value in song_artist_dict.items():
    try:
        searched_song = spotify.search(q=f"track: {value} artist: {key} year: {format_date[-1]}")
        # pp.pprint(searched_song)
        song_uri = searched_song['tracks']['items'][0]['uri']
        song_uris.append(song_uri)
    except IndexError:
        print(f"{value} by {key} not found :(")

print("uris obtained")
# create playlist & add songs to it
new_playlist = spotify.user_playlist_create(user=user_id, name=f"Irish Top 50: {usr_date}")
new_playlist_id = new_playlist["id"]
spotify.playlist_add_items(playlist_id=new_playlist_id, items=song_uris)
