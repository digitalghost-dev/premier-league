import streamlit as st

class NewsSection:
	def __init__(self, news_df):
		self.news_df = news_df
	
	def display(self):
		st.header("Recent News")
		col1, col2, col3, col4 = st.columns(4)

		with col1:
			# Your code here
			with st.container():
				try:
					st.image(self.news_df.iloc[0, 2], use_column_width=True)
					st.subheader(self.news_df.iloc[0, 0])
					st.write(f"Publish time: {self.news_df.iloc[0, 3]}")
					st.markdown(
						f"<a href={(self.news_df.iloc[0, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col2:
			with st.container():
				try:
					st.image(self.news_df.iloc[1, 2], use_column_width=True)
					st.subheader(self.news_df.iloc[1, 0])
					st.write(f"Publish time: {self.news_df.iloc[1, 3]}")
					st.markdown(
						f"<a href={(self.news_df.iloc[1, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col3:
			with st.container():
				try:
					st.image(self.news_df.iloc[2, 2], use_column_width=True)
					st.subheader(self.news_df.iloc[2, 0])
					st.write(f"Publish time: {self.news_df.iloc[2, 3]}")
					st.markdown(
						f"<a href={(self.news_df.iloc[2, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col4:
			with st.container():
				try:
					st.image(self.news_df.iloc[3, 2], use_column_width=True)
					st.subheader(self.news_df.iloc[3, 0])
					st.write(f"Publish time: {self.news_df.iloc[3, 3]}")
					st.markdown(
						f"<a href={(self.news_df.iloc[3, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		st.divider()
