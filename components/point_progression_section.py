import pandas as pd
import plotly.graph_objects as go
import streamlit as st


class PointProgressionSection:
	def __init__(self, teams_df, standings_df):
		self.teams_df = teams_df
		self.standings_df = standings_df

	def calculate_points(self):
		team_forms = [[], [], [], [], []]
		forms = [self.teams_df.iloc[i, 1] for i in range(5)]

		for count, form in enumerate(forms):
			points = 0
			for char in form:
				if char == "W":
					points += 3
				elif char == "D":
					points += 1
				else:
					points += 0

				team_forms[count].append(points)

		return team_forms

	def create_dataframe(self, team_forms):
		headers = [str(self.standings_df.iloc[i, 3]) for i in range(5)]
		zipped = list(zip(*team_forms))  # Transpose the list of lists
		return pd.DataFrame(zipped, columns=headers)

	def display(self):
		team_forms = self.calculate_points()
		df = self.create_dataframe(team_forms)

		st.subheader("Point Progression throughout the Season")

		labels = [str(f"{self.standings_df.iloc[i, 3]} - {self.standings_df.iloc[i, 1]} points") for i in range(5)]
		colors = ["#1e90ff", "#ff4500", "#ffd700", "#228b22", "#000000"]

		fig = go.Figure()

		for i in range(5):
			fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:, i], name=labels[i], line=dict(color=colors[i], width=2)))

		# add markers
		fig.update_traces(mode="markers+lines", marker=dict(size=8, line=dict(width=2)))

		fig.update_layout(
			xaxis_title="Gameweek",
			yaxis_title="Points",
			legend_title="Team",
			legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
			height=600,
		)

		st.plotly_chart(fig, use_container_width=True)
