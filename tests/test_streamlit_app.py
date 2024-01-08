from streamlit.testing.v1 import AppTest

at = AppTest.from_file("streamlit_app.py", default_timeout=1000)
at.run()


def test_title_area():
	assert "Premier League Statistics / 2023-24" in at.title[0].value
	assert "Current Round: " in at.subheader[0].value


# Standings & Overivew
def test_tab_one():
	assert at.tabs[0].subheader[0].value == "League Statistics"
	assert at.tabs[0].subheader[1].value == "Current Standings"
	assert at.tabs[0].subheader[2].value == "Location of Stadiums"


# Top Teams & Scorers
def test_tab_two():
	assert at.tabs[1].subheader[0].value == "Top 5 Teams"
	assert at.tabs[1].subheader[2].value == "Point Progression throughout the Season"


# Fixtures
def test_tab_three():
	assert at.tabs[2].subheader[0].value == "Fixtures"


# Squads
def test_tab_four():
	assert at.tabs[3].subheader[0].value == "Team Squads"
	assert at.tabs[3].markdown[0].value == "**Note:** Double click on the player's photo to expand it."


# News & Highlights
def test_tab_five():
	assert at.tabs[4].header[0].value == "Recent News"
	assert at.tabs[4].header[1].value == "Recent Highlights"


# About
def test_tab_six():
	assert at.tabs[5].subheader[0].value == "About"
