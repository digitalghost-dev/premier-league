import streamlit as st


class TopScorersSection:
	def __init__(self, top_scorers_df):
		self.top_scorers_df = top_scorers_df

	def generate_scorer_html(self, index):
		scorer = self.top_scorers_df.iloc[index]
		return [
			f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{scorer.iloc[5]}'/>",
			f"<p style='text-align: center; padding-top: 0.8rem;'><b>{scorer.iloc[0]}</b></p>",
			f"<p style='text-align: center;'><b>Goals:</b> {scorer.iloc[1]}</p>",
			f"<p style='text-align: center;'><b>Assists:</b> {scorer.iloc[3]}</p>",
			f"<p style='text-align: center;'><b>Team:</b> {scorer.iloc[2]}</p>",
			f"<p style='text-align: center;'><b>Nationality:</b> {scorer.iloc[4]}</p>",
		]

	def display(self):
		with st.container():
			st.subheader("Top 5 Scorers")
			columns = st.columns(5)

			for i, col in enumerate(columns):
				with col:
					markdown_list = self.generate_scorer_html(i)
					for item in markdown_list:
						st.markdown(item, unsafe_allow_html=True)
