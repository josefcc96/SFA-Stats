import streamlit as st

import requests

# Page title
st.set_page_config(page_title='Spotify For Artist Stats', page_icon='📊')
st.title('📊 Spotify For Artist Stats')

with st.expander('How its work'):
  st.markdown('**What can this app do?**')
  st.info('This app uses and Spotify For Artist account to get the stats reported on the dashboard')
  st.markdown('**How to use the app?**')
  st.markdown('You will need to important things:')
  st.markdown('1. **Artist ID**: You can find this on the URL of the Spotify for Artists (SFA) dashboard. For example: `https://artists.spotify.com/c/artist/XXXXXXXXXXXXXXXXX/audience/`\n    - The xxxxxxxxxxxx represent the artist ID')
  st.markdown(""" 2. **Access Token**: This token is sent in requests to the Spotify backend server. 
    - To obtain this token, open the developer tools in your browser and navigate to the **network** tab.
    - Once in the network tab, reload the page. You will see all the requests being made to the server.
    - In the list of requests, select the one that starts with 'stats?...'.
    - Then, navigate to the **headers** section and copy the entire content of the **authorization** field from the request header.
    - The authorization content should look like `Bearer BQBS148ZiH...`""")


artist_id = st.text_input(label="Artist ID", placeholder="3GzWXXXXXXXXXXXX")
authorization = st.text_input(label="Authorization ", placeholder="Bearer XXXXXXXXXXX")
start_date = st.date_input('Start Date')
end_date = st.date_input('End Date')

URL_BASE=f"https://generic.wg.spotify.com/audience-engagement-view/v1/artist/{artist_id}/stats"
st.session_state.response=''

def get_stats(artist_id, authorization, start_date, end_date):
  headers = {
    'Authorization': authorization,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Grpc-Timeout": "10S",
    "Accept-Language":"en-US",
    "App-Platform":"Browser",
    "accept": "application/json",
    "origin": "https://artists.spotify.com",
    "referer": "https://artists.spotify.com/",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "spotify-app-version": "1.0.0.7f78fca",
  }
  params = {
      "from_date": start_date.strftime("%Y-%m-%d"),
      "to_date": end_date.strftime("%Y-%m-%d")
  }
  response = requests.get(URL_BASE.format(artist_id), headers=headers, params=params)
  print(response)
  st.session_state.response='rtttt'

st.button(
        label="Get Stats",
        type="primary",
        on_click=get_stats,
        args=(artist_id, authorization, start_date, end_date),
    )

st.text(st.session_state.response)
if st.session_state.response!='':
  st.json(st.session_state.response)
else:
  print(st.session_state.response)



# st.subheader('Which Movie Genre performs ($) best at the box office?')

# Load data
# df = pd.read_csv('data/movies_genres_summary.csv')
# df.year = df.year.astype('int')

# Input widgets
## Genres selection
# genres_list = df.genre.unique()
# genres_selection = st.multiselect('Select genres', genres_list, ['Action', 'Adventure', 'Biography', 'Comedy', 'Drama', 'Horror'])

## Year selection
# year_list = df.year.unique()
# year_selection = st.slider('Select year duration', 1986, 2006, (2000, 2016))
# year_selection_list = list(np.arange(year_selection[0], year_selection[1]+1))

# df_selection = df[df.genre.isin(genres_selection) & df['year'].isin(year_selection_list)]
# reshaped_df = df_selection.pivot_table(index='year', columns='genre', values='gross', aggfunc='sum', fill_value=0)
# reshaped_df = reshaped_df.sort_values(by='year', ascending=False)


# Display DataFrame

# df_editor = st.data_editor(reshaped_df, height=212, use_container_width=True,
#                             column_config={"year": st.column_config.TextColumn("Year")},
#                             num_rows="dynamic")
# df_chart = pd.melt(df_editor.reset_index(), id_vars='year', var_name='genre', value_name='gross')

# Display chart
# chart = alt.Chart(df_chart).mark_line().encode(
#             x=alt.X('year:N', title='Year'),
#             y=alt.Y('gross:Q', title='Gross earnings ($)'),
#             color='genre:N'
#             ).properties(height=320)
# st.altair_chart(chart, use_container_width=True)
