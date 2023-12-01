from streamlit.testing.v1 import AppTest

at = AppTest.from_file("streamlit_app.py", default_timeout=1000)
at.secrets["mapbox"] = {"mapbox_key": "<test api key>"}
at.run()


def test_title_area():
	assert "Premier League Statistics / 2023-24" in at.title[0].value
	assert "Current Round: " in at.subheader[0].value


def test_tab_one():
	assert at.tabs[0].subheader[0].value == "League Statistics"
	assert at.tabs[0].subheader[1].value == "Current Standings"
	assert at.tabs[0].subheader[2].value == "Location of Stadiums"


def test_tab_two():
	assert at.tabs[1].subheader[0].value == "Top 5 Teams"
	assert at.tabs[1].subheader[2].value == "Point Progression thoughout the Season"
