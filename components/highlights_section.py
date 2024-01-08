import streamlit as st


class HighlightsSection:
	def __init__(self, highlights_df):
		self.highlights_df = highlights_df

	def display_first_row(self):
		st.header("Recent Highlights")
		columns = st.columns(3)

		for i, col in enumerate(columns):
			with col:
				try:
					st.image(self.highlights_df.iloc[i, 3], use_column_width="auto")
					st.subheader(self.highlights_df.iloc[i, 2])
					st.write(f"Publish time: {self.highlights_df.iloc[i, -1]}")
					st.markdown(
						f"<a href='{(self.highlights_df.iloc[i, 1])}'>Watch on YouTube</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

	def display_second_row(self):
		columns = st.columns(3)

		for i, col in enumerate(columns):
			with col:
				try:
					st.image(self.highlights_df.iloc[i + 3, 3], use_column_width="auto")
					st.subheader(self.highlights_df.iloc[i + 3, 2])
					st.write(f"Publish time: {self.highlights_df.iloc[i + 3, -1]}")
					st.markdown(
						f"<a href='{(self.highlights_df.iloc[i + 3, 1])}'>Watch on YouTube</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass
