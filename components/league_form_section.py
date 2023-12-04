import streamlit as st


class LeagueFormsSection:
	def __init__(self, teams_df):
		self.teams_df = teams_df

	def generate_team_html(self, team_indices):
		markdown_list = []
		for index in team_indices:
			team_info = self.teams_df.iloc[index]
			markdown_list.append(
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{team_info.iloc[0]}'/>"
			)
			markdown_list.append(
				f"<p style='text-align: center; padding-top: 0.8rem;'>{index + 1}th / {team_info.iloc[1][-5:]}</p>"
			)
		return markdown_list

	def display(self):
		st.subheader("Forms for the Rest of the League")
		columns = st.columns(5)

		for i, col in enumerate(columns):
			with col:
				team_indices = [i + 5, i + 10, i + 15]
				markdown_list = self.generate_team_html(team_indices)
				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)
