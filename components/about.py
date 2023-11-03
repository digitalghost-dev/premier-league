import streamlit as st


class AboutSection:
	def __init__(self):
		pass

	def display(self):
		st.subheader("About")
		st.write(
			"""
            This project is created by maintained by [myself](https://github.com/digitalghost-dev) to practice my skills in Data Engineering to one day break into the field.

            I chose using data for Premier League because I am a huge fan of the sport and I am always interested in learning more about the game.

            This is the only project that I'm currently working on and plan to continue to add more features and tools to it as I learn more about Data Engineering.
            """
		)
