# Change Log
This change log provides version history for the Streamlit app itself, not for any backend/infrastructure changes.

View the Streamlit dasboard: https://premierleague.streamlit.app

## [1.1.0] - 2023-04-07

### **Added**

Top Teams Tab
* Added `logo` and `form` for the rest of the league.

### **Changed**

Top Teams Tab
* Center aligning `logo`, `form (last 5)`, `clean sheets`, `penalties scored`, and `penalties missed` in their containers.
* Setting `logo` width for top 5 teams to `150px`.

Top Players Tab
* Center aligning `photo`, `name`, `goals`, `team`, and `nationality` in their containers.
* Setting `photo` width for top 5 players to `150px`.

### **Removed**
* Removing `LIMIT 5` from SQL query to pull all teams.

## [1.0.0] - 2023-04-05

### **Added**

Overview Tab
* View the current standings for the league for the current season.
* An adjustable slider gives control to focus in on teams that fit within a certain number of points.
* A bar chart with teams (x-axis) and points (y-axis) adjusts accordingly to the slider.
* A map with plots for the stadium locations for each team in the current season.

Top Teams Tab
* Shows the `logo`, `form (last 5)`, `clean sheets`, `penalties scored`, and `penalties missed` for the current top five teams in the league.
* A line graph depicts the rise in points over each matchday.

Top Players Tab
* Shows the `portrait`, `goals`, `team`, and `nationality` of the current top five goal scorers in the league.