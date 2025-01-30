import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# Streamlit app setup
st.set_page_config(
    page_title="Live Cricket Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and description
st.title("🏏 Live Cricket Dashboard ")
st.markdown("This dashboard fetches live cricket match updates from ESPNcricinfo with a latency of approximately 10 minutes.")

# Function to fetch live match data from ESPNcricinfo
@st.cache_data(ttl=600)
def fetch_match_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    url = "https://www.espncricinfo.com/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    matches = []
    cards = soup.find_all('div', {'class': 'slick-slide' or 'slick-slide slick-active'}, {'style': 'outline:none'})

    for card in cards:
        match = {}
        match_status = card.find('span', class_='ds-text-tight-xs ds-font-bold ds-uppercase ds-leading-5')
        match['status'] = match_status.text.strip() if match_status else None
        
        details = card.find('span', class_='ds-text-tight-xs ds-text-typo-mid2')
        match['details'] = details.text.strip() if details else None
        
        teams = []
        all_teams = card.find_all('div', class_=('ci-team-score ds-flex ds-justify-between ds-items-center ds-text-typo', 'ci-team-score ds-flex ds-justify-between ds-items-center ds-text-typo ds-opacity-50'))
        
        for team in all_teams:
            team_name = team.find('p', class_=('ds-text-tight-s ds-font-bold ds-capitalize ds-truncate', 'ds-text-tight-s ds-font-bold ds-capitalize ds-truncate !ds-text-typo-mid3'))
            team_name = team_name.text.strip() if team_name else None
            
            team_flag = team.find('div', class_='ds-flex ds-items-center ds-min-w-0 ds-mr-1')
            img_tag = team_flag.find('img') if team_flag else None
            flag_url = img_tag['src'] if img_tag else None
            
            team_score_tag = team.find('div', class_='ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap')
            team_score = team_score_tag.text.strip() if team_score_tag else None
            
            if team_name:  # Only add valid team data
                teams.append({'name': team_name, 'flag_url': flag_url, 'score': team_score})
        
        match['teams'] = teams
        
        today_details = card.find('div', class_='ds-text-tight-xs ds-text-right')
        match['other_details'] = today_details.text.strip() if today_details else None
        
        result_details = card.find('div', class_='ds-h-3')
        match['result'] = result_details.text.strip() if result_details else None
        
        if match['status'] and match['teams']:  # Ignore empty matches
            matches.append(match)

    return matches

# Sidebar refresh option
refresh_interval = st.sidebar.slider("Select refresh interval (seconds):", min_value=10, max_value=600, value=60, step=10)
st.sidebar.write("The data refreshes every", refresh_interval, "seconds.")

# Fetch and display live match data
match_data = fetch_match_data()

if match_data:
    st.markdown("### Live Matches")
    st.markdown('<div style="display: flex; overflow-x: auto;">', unsafe_allow_html=True)
    
    for match in match_data:
        with st.container():
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 10px; width: 250px; display: inline-block; text-align: center;">
                    <h4>{match['status']}</h4>
                    <p>{match['details']}</p>
                    <hr>
                """,
                unsafe_allow_html=True
            )
            
            for team in match['teams']:
                flag_html = f'<img src="{team["flag_url"]}" width="30px">' if team["flag_url"] else ""
                st.markdown(
                    f"<p>{flag_html} <strong>{team['name']}</strong>: {team['score']}</p>",
                    unsafe_allow_html=True
                )
            
            st.markdown(
                f"<p style='color: green;'>{match['result']}</p></div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.write("No live matches available right now.")

st.write("Last updated at:", time.strftime("%Y-%m-%d %H:%M:%S"))

time.sleep(refresh_interval)
