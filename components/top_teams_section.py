import streamlit as st


class TopTeamsSection:
	def __init__(self, teams_df):
		self.teams_df = teams_df

	def generate_team_html(self, index):
		team = self.teams_df.iloc[index]
		return [
			f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{team.iloc[0]}'/>",
			f"<p style='text-align: center; padding-top: 0.8rem;'><b>{index + 1}st / Form (Last 5):</b> {team.iloc[1][-5:]}</p>",
			f"<p style='text-align: center;'><b>Clean Sheets:</b> {team.iloc[3]}</p>",
			f"<p style='text-align: center;'><b>Penalties Scored:</b> {team.iloc[4]}</p>",
			f"<p style='text-align: center;'><b>Penalties Missed:</b> {team.iloc[5]}</p>",
		]

	def display(self):
		with st.container():
			st.subheader("Top 5 Teams")
			columns = st.columns(5)

			for i, col in enumerate(columns):
				with col:
					markdown_list = self.generate_team_html(i)
					for item in markdown_list:
						st.markdown(item, unsafe_allow_html=True)
