import json
import requests as rq
from secrets import spotify_user_id, spotify_token
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine


class GetPlayedSong:
    def __init__(self, limit):
        self.user_id = spotify_user_id  # my user info login
        self.limit = limit  # the number of results that are stored in dataframe

    def spotify_request(self):
        limit_str = str(self.limit)
        query = "https://api.spotify.com/v1/me/player/recently-played?limit=" + limit_str.format(self.user_id)
        response = rq.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        return response_json

    def get_song_list(self, json):

        song_info = {}
        songs = []
        artists = []
        albums = []
        timePlayed = []

        for i in range(self.limit):

            songs.append(json["items"][i]["track"]["name"])

            artists_raw = json["items"][i]["track"]["artists"]
            artist_song = [str(artists_raw[a]["name"]) for a in range(len(artists_raw))]
            artists.append(artist_song)

            albums.append(json["items"][i]["track"]["album"]["name"])

            timePlayed.append(json["items"][i]["played_at"])

        song_info["song"] = songs
        song_info["artists"] = artists
        song_info["album"] = albums
        song_info["time_played"] = timePlayed

        return song_info

def clean_data(clean_df):
    clean_df["time_played"] = pd.to_datetime(clean_df["time_played"]).dt.round("s") + pd.Timedelta(-8, unit="H")   # PST
    clean_df = clean_df.astype({"song": str, "artists": str, "album": str})
    clean_df["artists"] = clean_df["artists"].str.replace("'", "")

    return clean_df


class DataFrame(object):
    def __init__(self, new_df, lastSong):
        self.new_df = new_df
        self.lastSong = lastSong

    def find_index(self, index, size):
        for index in range(size-1,-1,-1):
            find = DataFrame.is_match(self, index)

            if find and index > 0:  # base case 1: where match is found
                print("FOUND")
                return index
            elif find and index == 0:  # base case 2: where most recent song is last song
                print("This song has already been added to the database")
                return -1
            elif not find and index == 0:  # base case 3: where song is not in DF, must expand size
                print("Song not in recently played list, must expand size")
                return -2
        return index

    def is_match(self, index):
        row = pd.DataFrame(self.new_df.iloc[[index]])
        row = row.reset_index(drop=True)
        print("\nTHE SONG BEING COMPARED:\n ", row)
        print("\nTHE LAST SONG:\n ", self.lastSong)

        equal = row.isin(self.lastSong).transpose()
        print(equal)
        total = sum(equal[0])
        print("TOTAL MATCHING ENTRIES: ", total)  # PRINT TOTAL MATCHING COLUMNS
        if total == 4:
            print("SUCCESS\n")
            return True
        else:
            return False

    def cut_song_df(self, size):
        start = size - 1
        ind = DataFrame.find_index(self, start, size)  # WHERE TO START LOOKING
        if ind > 0:  # starts from top and truncates at ind
            final_df = pd.DataFrame(self.new_df.iloc[0:ind])
            print("THE FINAL_DF THAT IS STORED IN DB:\n ", final_df)

        else:
            final_df = pd.DataFrame()

        return final_df


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(user="root", password="password",
                                           host="localhost",
                                           database="songs")
        self.cursor = self.conn.cursor(buffered=True)
        self.engine = create_engine("mysql://root:[password]@localhost:3306/songs", echo=False)

    def create_connection(self):
        try:
            if self.conn:
                print("connected")
                return self.conn

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        return conn

    def check_empty(self):
        check = (
                """
                SELECT * FROM songs LIMIT 1
                """
        )
        self.cursor.execute(check)
        status = self.cursor.fetchone()
        print("STATUS:", status)

        if status:
            return False
        else:
            return True

    def get_last_song(self):
        query = (
            """
            SELECT song, artists, album, time_played
            FROM songs t1 
            INNER JOIN(
                SELECT MAX(time_played) MaxTime 
                FROM songs
            ) t2 
            ON t1.time_played = t2.MaxTime
            """
        )

        self.cursor.execute(query)
        final_song = pd.DataFrame(self.cursor.fetchone()).transpose()
        pd.set_option('display.max_columns', None)
        final_song.columns = ["song", "artists", "album", "time_played"]

        final_song["time_played"] = pd.to_datetime(final_song["time_played"], format= "%Y-%m-%d %H:%M:%S", utc=True)
        final_song = final_song.astype({"artists": str})

        return final_song

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

    def insert_data(self, df):
        conn2 = self.engine.connect()
        df.to_sql(name="songs", con=conn2, if_exists="append", index=False)
        conn2.close()


if __name__  == "__main__":
    db = Database()
    conn = db.create_connection()

    empty = db.check_empty()
    print("empty:", empty)

    size = 50  # CHANGE SIZE FOR NUMBER OF SONGS TO STORE
    get_song = GetPlayedSong(size)
    song_df = pd.DataFrame(get_song.get_song_list(get_song.spotify_request()))

    pd.set_option('display.max_columns', None)
    song_df = clean_data(song_df)
    print(song_df)

    if not empty:
        last_song = pd.DataFrame(db.get_last_song())
        print("THE LAST SONG:\n ", last_song)

        data = DataFrame(song_df, last_song)
        final_df = data.cut_song_df(size)

    else:
        final_df = song_df

    db.close_connection()

    if not final_df.empty:
        db.insert_data(final_df)
    else:
        print("nothing inserted, check error message above.....exiting")
