# Automatic-Spotify-Database-Compiler
A convenient tool that uses Spotify's Web API, Python, and SQL to manage a user's recently played songs.

## How Does It Work
It extracts the recent songs using Spotify's Web API and automatically parses and updates a database using a recursive algorithm. This maintains a database that stores a user's listening history with the simple execution of a script. This feature is not currently incorporated into the Spotify app.  

## What Information is Required
A user's username and an authentification token that can be acquired using Spotify's Web API. 

## Current Limitations
The Spotify Web API can only currently retrieve a user's 50 most recent songs. There is no way to maintain the database if the user has listened to more than 50 songs since the script has been last executed.

## Next Steps
There are plans to expand this project using various machine learning algorithms and adding functionalities such as a recommendation system.
