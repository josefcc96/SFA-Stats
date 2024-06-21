import streamlit as st
import pandas as pd
import requests
import altair as alt

def request_spotify(type):
  url_base="https://generic.wg.spotify.com/audience-engagement-view/v1/artist/{}/{}"
  headers = {
    'Authorization': st.session_state.authorization,
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
      "from_date": st.session_state.start_date,
      "to_date": st.session_state.end_date
  }
  response = requests.get(url_base.format(st.session_state.artist_id, type), headers=headers, params=params)
  return response

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


st.session_state.artist_id = st.text_input(label="Artist ID", placeholder="3GzWXXXXXXXXXXXX")
st.session_state.authorization = st.text_input(label="Authorization Token", placeholder="Bearer XXXXXXXXXXX")
st.session_state.start_date = st.date_input('Start Date').strftime("%Y-%m-%d")
st.session_state.end_date = st.date_input('End Date').strftime("%Y-%m-%d")

def format_number(num_str):
  num = float(num_str)
  formatted_num = f"{num:,.0f}" if num.is_integer() else f"{num:,.3f}"
  return formatted_num

def get_options():
  data=[
          ["All active sources", "ALL_ACTIVE_SOURCES"],
          ["Artist profile and catalog", "ARTIST_PROFILE_AND_CATALOG"],
          ["Listener's own playlists and library", "LISTENERS_OWN_PLAYLIST_AND_LIBRARY"],
          ["Listener’s queue", "PLAY_QUEUE"],
          ["All programmed sources", "ALL_PROGRAMMED_SOURCES"],
          ["Editorial playlists", "EDITORIAL_PLAYLIST"],
          ["Algorithmic playlists and mixes", "ALGORITHMIC_PLAYLISTS"],
          ["Personalized editorial playlists", "PERSONALIZED_EDITORIAL_PLAYLIST"],
          ["Other listeners’ playlists", "OTHER_LISTENERS_PLAYLISTS"],
          ["Radio and autoplay", "AUTOPLAY_AND_RADIO"],
          ["Charts", "CHARTS"],
          ["Other", "OTHER"],
        ]
  df = pd.DataFrame(data, columns=["Label", "Key"])
  return df

def get_stats():
  response = request_spotify("stats")
  if response.status_code==200:
    stats=response.json()
    stats_keys=list(stats.keys())
    for key in stats_keys:
      fulltime_serie=[]
      for timeserie in stats[key]["current_period_timeseries"]:
        fulltime_serie.append(timeserie)
      df_raw = pd.DataFrame(fulltime_serie)
      df_raw.reset_index(drop=True, inplace=True)
      df_raw['y'] = pd.to_numeric(df_raw.y)
      df_raw=df_raw.rename(columns={"x":"date", "y":key})
      stats[key]["df"] = df_raw
    st.session_state["stats"]=stats
  elif response.status_code==401:
    st.error(response.text)
    st.stop()
  else:
    try:
      st.json(response.json())
    except:
      st.error(str(response))

  response=request_spotify("segmented_stats")
  if response.status_code==200:
    st.session_state["seg_stats"]=response.json()
  elif response.status_code==401:
    st.error(response.text)
  else:
    try:
      st.json(response.json())
    except:
      st.error(str(response))


def mul_sel_cb(key):
  df = st.session_state["stats"][key]["df"]
  sel_options=st.session_state["mul_sel_"+key]
  df_options= get_options()
  options_keys= df_options[df_options['Label'].isin(sel_options)]['Key']
  st.session_state["seg_stats"]



st.button(
        label="Get Stats",
        type="primary",
        on_click=get_stats,
    )


if "stats" in st.session_state:
  stats=st.session_state["stats"]
  stats_keys=list(stats.keys())
  for index, tab in enumerate(st.tabs(stats_keys)):
    key=stats_keys[index]
    col1, col2= tab.columns(2)
    col1.metric(f"Current Period {st.session_state.start_date} - {st.session_state.end_date}", format_number(stats[key]['current_period_agg']), str(format_number(stats[key]['period_change_pct']))+"%")
    col2.metric("Previous Period", format_number(stats[key]['previous_period_agg']))
   
    if key in ("streams", "listeners", "streams_per_listener"):
      options = tab.multiselect(
        "Segmentation",
        get_options(),
        None, key="mul_sel_"+key, on_change=mul_sel_cb, args=(key,))

    df_chart_wide = st.session_state["stats"][key]["df"]
      

    max=int(1.2*(df_chart_wide[key].max()))

    df_chart = df_chart_wide.melt('date', var_name='stat', value_name='value')
    # Display chart    
    brush = alt.selection_interval(encodings=['x'])
    base = alt.Chart(df_chart).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date', timeUnit='yearmonthdate'),
        y=alt.Y('value', type="quantitative", title=None),
        color= alt.Color("stat:N"),
        tooltip= ['x:T', "value:Q", "stat:N"]
    )
    upper = base.encode(alt.X('date:T', title='Date', timeUnit='yearmonthdate').scale(domain=brush),
                        alt.Y('value', type="quantitative", title=None).scale(domainMax=max),
                        color= alt.Color("stat:N"),
                        tooltip=['date:T', "value:Q", "stat:N"])

    lower = base.properties(height=80).add_params(brush)
    tab.altair_chart(upper & lower, use_container_width=True)
    # Display DataFrame
    tab.dataframe(df_chart_wide)



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
