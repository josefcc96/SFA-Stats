# 📀📈 Spotify For Artist Scrapper

**What can this app do?**

This app uses and Spotify For Artist account to get the stats reported on the dashboard

**How to use the app?**
You will need to important things:
1. **Artist ID**: You can find this on the URL of the Spotify for Artists (SFA) dashboard. For example: `https://artists.spotify.com/c/artist/XXXXXXXXXXXXXXXXX/audience/`\n    - The xxxxxxxxxxxx represent the artist ID
2. **Access Token**: This token is sent in requests to the Spotify backend server. 
    - To obtain this token, open the developer tools in your browser and navigate to the **network** tab.
    - Once in the network tab, reload the page. You will see all the requests being made to the server.
    - In the list of requests, select the one that starts with 'stats?...'.
    - Then, navigate to the **headers** section and copy the entire content of the **authorization** field from the request header.
    - The authorization content should look like `Bearer BQBS148ZiH...`

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://interactive-data-explorer-template.streamlit.app/)

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/josefcc96/SFA-Stats?quickstart=1)

  
