from streamlit.testing.v1 import AppTest

at = AppTest.from_file("streamlit_app.py", default_timeout=1000)
at.run()


def test_main_page():
	assert at.title[0].value == "Premier League Statistics / 2023-24"
	assert "Current Round: " in at.subheader[0].value
	assert at.subheader[-1].value == "Social"


# Standings & Overivew
def test_tab_one():
	assert at.tabs[0].subheader[0].value == "League Statistics"
	assert at.tabs[0].subheader[1].value == "Current Standings"
	assert at.tabs[0].subheader[2].value == "Location of Stadiums"


# Teams Statistics
def test_tab_two():
	assert at.tabs[1].subheader[0].value == "Top 5 Teams"
	assert at.tabs[1].subheader[1].value == "Point Progression throughout the Season"
	assert at.tabs[1].subheader[2].value == "Points per Team:"
	assert at.tabs[1].subheader[3].value == "Forms for the Rest of the League"


# Players & Injuries Statistics
def test_tab_three():
	assert at.tabs[2].subheader[0].value == "Top 5 Scorers"

	# Column 1
	assert "Goals:" in at.tabs[2].markdown[2].value
	assert "Assists:" in at.tabs[2].markdown[3].value
	assert "Team:" in at.tabs[2].markdown[4].value
	assert "Nationality:" in at.tabs[2].markdown[5].value

	# Column 2
	assert "Goals:" in at.tabs[2].markdown[8].value
	assert "Assists:" in at.tabs[2].markdown[9].value
	assert "Team:" in at.tabs[2].markdown[10].value
	assert "Nationality:" in at.tabs[2].markdown[11].value

	# Column 3
	assert "Goals:" in at.tabs[2].markdown[14].value
	assert "Assists:" in at.tabs[2].markdown[15].value
	assert "Team:" in at.tabs[2].markdown[16].value
	assert "Nationality:" in at.tabs[2].markdown[17].value

	# Column 4
	assert "Goals:" in at.tabs[2].markdown[20].value
	assert "Assists:" in at.tabs[2].markdown[21].value
	assert "Team:" in at.tabs[2].markdown[22].value
	assert "Nationality:" in at.tabs[2].markdown[23].value

	# Column 5
	assert "Goals:" in at.tabs[2].markdown[26].value
	assert "Assists:" in at.tabs[2].markdown[27].value
	assert "Team:" in at.tabs[2].markdown[28].value
	assert "Nationality:" in at.tabs[2].markdown[29].value

	assert at.tabs[2].subheader[1].value == "Recent Injuries"


# Fixtures
def test_tab_four():
	assert at.tabs[3].subheader[0].value == "Fixtures"


# Squads
def test_tab_five():
	assert at.tabs[4].subheader[0].value == "Team Squads"
	assert at.tabs[4].markdown[0].value == "**Note:** Double click on the player's photo to expand it."
	assert at.tabs[4].selectbox[0].label == "Use the dropdown menu to select a team:"
	assert at.tabs[4].selectbox[0].placeholder == "Please make a selection"
	assert at.tabs[4].selectbox[0].options == [
		"Arsenal",
		"Aston Villa",
		"Bournemouth",
		"Brentford",
		"Brighton",
		"Burnley",
		"Chelsea",
		"Crystal Palace",
		"Everton",
		"Fulham",
		"Liverpool",
		"Luton",
		"Manchester City",
		"Manchester United",
		"Newcastle",
		"Nottingham Forest",
		"Sheffield Utd",
		"Tottenham",
		"West Ham",
		"Wolves",
	]


# News & Highlights
def test_tab_six():
	assert at.tabs[5].header[0].value == "Recent News"
	assert at.tabs[5].header[1].value == "Recent Highlights"


# MANU Stock Price
def test_tab_seven():
	assert at.tabs[6].subheader[0].value == "MANU - Stock Price"


# About
def test_tab_eight():
	assert at.tabs[7].subheader[0].value == "About"
