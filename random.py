import time
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_card import card
from streamlit_autorefresh import st_autorefresh
def get_match_cards():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    url = "https://www.espncricinfo.com/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    matches = []
    cards = soup.find_all('div', {'class' : 'slick-slide' or 'slick-slide slick-active'}, {'style' : 'outline:none'})
    for card in cards:
        match = {}
        match_status = card.find('span', class_='ds-text-tight-xs ds-font-bold ds-uppercase ds-leading-5')
        match['status'] = match_status.text.strip() if match_status else ""
        details = card.find('span', class_='ds-text-tight-xs ds-text-typo-mid2')
        match['details'] = details.text.strip() if details else ""
        teams = []
        all_teams = card.find_all('div', class_=('ci-team-score ds-flex ds-justify-between ds-items-center ds-text-typo' , 'ci-team-score ds-flex ds-justify-between ds-items-center ds-text-typo ds-opacity-50'))
        for team in all_teams:
            team_name = team.find('p', class_=('ds-text-tight-s ds-font-bold ds-capitalize ds-truncate' , 'ds-text-tight-s ds-font-bold ds-capitalize ds-truncate !ds-text-typo-mid3'))
            team_name = team_name.text.strip() if team_name else ""
            team_flag = team.find('div', class_='ds-flex ds-items-center ds-min-w-0 ds-mr-1')
            img_tag = team_flag.find('img') if team_flag else None
            flag_url = img_tag['src'] if img_tag else None
            team_score_tag = team.find('div', class_='ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap')
            team_score = team_score_tag.text.strip() if team_score_tag else ""
            teams.append({'name': team_name, 'flag_url': flag_url, 'score': team_score})
        match['teams'] = teams
        today_details = card.find('div', class_='ds-text-tight-xs ds-text-right')
        match['other_details'] = today_details.text if today_details else ""
        result_details = card.find('div', class_='ds-h-3')
        match['result'] = result_details.text.strip() if result_details else ""
        matches.append(match)
    return matches
st.title('Today Matches - ESPN CRIC INFO')
st.markdown('Live updates every five minutes.')
match_data = get_match_cards()
count = st_autorefresh(interval=300000, key="autorefresh_key")
time.sleep(2)
for match in match_data:
    st.subheader(f"{match['status']} {match['details']}")
    for team in match['teams']:
        st.write(f"{team['name']} {team['score']}")
    st.caption(match['result'])
    st.write(f"**{match['other_details']}**")
    st.markdown('---')