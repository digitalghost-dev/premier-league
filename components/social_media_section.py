import streamlit as st
import streamlit.components.v1 as components


class SocialMediaSection:
	def __init__(self):
		self.social_links = [
			{
				"url": "https://hub.docker.com/r/digitalghostdev/premier-league/tags",
				"icon_url": "https://storage.googleapis.com/premier_league_bucket/icons/companies/docker.svg",
				"alt_text": "Docker",
			},
			{
				"url": "https://github.com/digitalghost-dev/",
				"icon_url": "https://storage.googleapis.com/premier_league_bucket/icons/companies/github.svg",
				"alt_text": "GitHub",
			},
		]

	def generate_html(self):
		html = ""
		for link in self.social_links:
			html += f"""
                <a target="_blank" rel="noopener noreferrer" href="{link['url']}">
                    <img src="{link['icon_url']}" alt="{link['alt_text']}" width="40" height="40" style='padding-right: 1rem'>
                </a>
            """
		return f"<div style='display: flex; flex-direction: row;'>{html}</div>"

	def display(self):
		st.divider()
		st.subheader("Social")
		social_html = self.generate_html()
		components.html(social_html)
