import streamlit as st
import plotly.graph_objects as go


class PointSliderSection:
	def __init__(self, standings_df):
		self.standings_df = standings_df

	def display(self):
		st.subheader("Points per Team:")
		# Creating the slider.
		points = self.standings_df["points"].tolist()
		points_selection = st.slider(
			"Select a Range of Points:", min_value=min(points), max_value=max(points), value=(min(points), max(points))
		)
		# Picking colors to use for the bar chart.
		colors = [
			"indigo",
		] * 20
		# Making sure the bar chart changes with the slider.
		mask = self.standings_df["points"].between(*points_selection)
		amount_of_teams = self.standings_df[mask].shape[0]

		df_grouped = self.standings_df[mask]
		df_grouped = df_grouped.reset_index()
		lowest_number = df_grouped["points"].min()
		st.markdown(f"Number of teams with {lowest_number} or more points: {amount_of_teams}")
		# Creating the bar chart.
		points_chart = go.Figure(
			data=[
				go.Bar(
					x=df_grouped["team"],
					y=df_grouped["points"],
					marker_color=colors,
					text=df_grouped["points"],
					textposition="auto",
				)
			]
		)
		# Rotating x axis lables.
		points_chart.update_layout(
			xaxis_tickangle=-35,
			autosize=False,
			margin=dict(
				l=0,  # left
				r=0,  # right
				b=0,  # bottom
				t=0,  # top
			),
		)

		st.plotly_chart(points_chart, use_container_width=True)
