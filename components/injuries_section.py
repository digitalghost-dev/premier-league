import streamlit as st


class InjuriesSection:
	def __init__(self, injuries_df):
		self.injuries_df = injuries_df
		self.teams = (
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
		)

	def display(self):
		st.divider()
		st.subheader("Recent Injuries")
		st.write("Select the teams you want to see recent injuries for.")
		popover = st.popover("Filter Teams")
		filtered_df = self.injuries_df.drop(columns=["team_id", "player_id"])
		team_checkboxes = {}

		for team in self.teams:
			team_checkboxes[team] = popover.checkbox(f"{team}", value=False)

		for team, is_checked in team_checkboxes.items():
			if is_checked:
				team_df = filtered_df[(filtered_df["team_name"] == team)]
				team_df = team_df.drop(columns=["team_name"])
				st.write(f"**{team}**")
				if team_df.empty:
					st.write("No recent injuries reported.")
					st.empty()
				else:
					st.dataframe(
						team_df,
						column_config={
							"player_name": "Player",
							"injury_type": "Injury Type",
							"injury_reason": "Reason",
							"injury_date": "Date",
						},
						hide_index=True,
						use_container_width=True,
					)
