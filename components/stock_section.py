import streamlit as st
import altair as alt


class StockSection:
	def __init__(self, stock_df):
		self.stock_df = stock_df
		self.line_chart = None

	def display(self):
		st.subheader("MANU - Stock Price")
		st.info(
			"""
			**INFO**\n
			This tab shows a stock price chart for the ***previous*** trading day for **MANU** ticker.\n
			Currently, the chart price is shown with 30 minutes intervals. Still testing this tab and hope to move it to every 10 minutes.\n
			Since this shows the previous trading day's data, there will be no data displayed on Sunday and Monday, New York time.
			"""
		)
		if self.stock_df.empty:
			st.warning("No data for today. Check back **after** the next trading day.")
		else:
			# Check if the timezone is already set
			if self.stock_df["new_york_time"].dt.tz is not None:
				self.stock_df["new_york_time"] = self.stock_df["new_york_time"].dt.tz_convert("US/Eastern")
			else:
				self.stock_df["new_york_time"] = self.stock_df["new_york_time"].dt.tz_localize("US/Eastern")

			self.line_chart = (
				alt.Chart(self.stock_df)
				.mark_line()
				.encode(
					x=alt.X("new_york_time:T", title="Time"),
					y=alt.Y("price:Q", title="Price").scale(zero=False),
				)
			)

			st.altair_chart(self.line_chart, use_container_width=True)
