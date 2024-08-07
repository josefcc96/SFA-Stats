import streamlit as st
import pandas as pd
import requests
import altair as alt
import datetime


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
st.set_page_config(page_title='Spotify For Artist Stats', page_icon='📈', layout="wide")
st.title('📈 Spotify For Artist Stats ')

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
date_max= datetime.datetime.now()-datetime.timedelta(days=30)
# st.session_state.start_date = st.date_input('Start Date',date_max, max_value=date_max).strftime("%Y-%m-%d")
dates = st.date_input('Date Filter', [date_max, date_max+datetime.timedelta(days=28)], max_value=date_max+datetime.timedelta(days=28))
if len(dates)>1:
  start_date, end_date=dates
  st.session_state.end_date=end_date.strftime("%Y-%m-%d")
  st.session_state.start_date=start_date.strftime("%Y-%m-%d")

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
    return
  else:
    try:
      st.json(response.json())
    except:
      st.error(str(response))

  response=request_spotify("segmented-stats")
  if response.status_code==200:
    seg_response=response.json()
    st.session_state["seg_stats"]=seg_response["segmentsMap"]
  elif response.status_code==401:
    st.error(response.text)
  else:
    try:
      st.json(response.json())
    except:
      st.error(str(response))


def mul_sel_cb(key):
  df_key= "df_mul_sel_"+key
  df_options= get_options()
  if "mul_sel_"+key in st.session_state:
    sel_options = st.session_state["mul_sel_"+key]
    options_keys= df_options[df_options['Label'].isin(sel_options)]['Key']
    if len(options_keys) == 0 and df_key in st.session_state:
      del st.session_state[df_key]
      return
    df_seg = pd.DataFrame()
    for option in options_keys:
      data = st.session_state["seg_stats"][option][key]['current_period_timeseries']
      wide=pd.DataFrame(data)
      wide.reset_index(drop=True, inplace=True)
      wide['y'] = pd.to_numeric(wide.y)
      wide = wide.rename(columns={"x":"date", "y":option})
      wide = wide.melt('date', var_name='stat', value_name='value')
      df_seg= pd.concat([df_seg ,wide], axis=0)
    st.session_state[df_key] = df_seg

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
        None, key="mul_sel_"+key)
    mul_sel_cb(key)
    wide = st.session_state["stats"][key]["df"]
    max=int(1.2*(wide[key].max()))

    if "df_mul_sel_"+key in st.session_state:
      wide=wide.rename(columns={key:("total_"+key).upper()})
      chart_long = wide.melt('date', var_name='stat', value_name='value')
      df_chart = pd.concat([chart_long, st.session_state["df_mul_sel_"+key]], axis=0)
    else:
      df_chart = wide.melt('date', var_name='stat', value_name='value')
    
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
    tab.dataframe(df_chart.pivot(index='date', columns='stat', values='value').reset_index())
