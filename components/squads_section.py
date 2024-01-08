import streamlit as st


class SquadSection:
	def __init__(self, squads_df):
		self.squads_df = squads_df
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

	def display(self, team_name):
		(
			col1,
			col2,
		) = st.columns(2)
		with col1:
			top_positions = ["Goalkeeper", "Midfielder"]
			for position in top_positions:
				filtered_df = self.squads_df[
					(self.squads_df["team_name"] == team_name) & (self.squads_df["player_position"] == position)
				]
				filtered_df = filtered_df.drop(columns=["team_id", "team_name", "player_id", "player_position"])

				st.write(f"**{position}s**")
				st.data_editor(
					filtered_df,
					column_config={
						"player_name": st.column_config.TextColumn("Player Name"),
						"player_photo": st.column_config.ImageColumn("Photo", width="small"),
					},
					hide_index=True,
					key=f"{team_name}-{position}",
				)

		with col2:
			bottom_positions = ["Defender", "Attacker"]
			for position in bottom_positions:
				filtered_df = self.squads_df[
					(self.squads_df["team_name"] == team_name) & (self.squads_df["player_position"] == position)
				]
				filtered_df = filtered_df.drop(columns=["team_id", "team_name", "player_id", "player_position"])

				st.write(f"**{position}s**")
				st.data_editor(
					filtered_df,
					column_config={
						"player_name": st.column_config.TextColumn("Player Name"),
						"player_photo": st.column_config.ImageColumn("Photo", width="small"),
					},
					hide_index=True,
					key=f"{team_name}-{position}",
				)
