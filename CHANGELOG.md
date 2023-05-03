# Change Log
This change log provides version history for the Streamlit Dashboard.

View the Streamlit dasboard: https://premierleague.streamlit.app

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

* **MAJOR:** Any changes to the backend infrastructure that requires new methods of moving data.
* **MINOR:** Any changes to the Streamlit dashboard that adds a new interaction/feature or removal of one.
* **PATCH:** Any changes that fix bugs.

## [2.0.0] - 2023-05-02
Now using [Firestore](https://firebase.google.com/docs/firestore/) to store fixture data in a document format.

### **Added**
* Added `Fixtures` tab for all rounds in the current season. Updates 3 times a day and will add new rounds as they start.

## [1.3.0][1.3.0] - 2023-04-17

### **Added**

* Added page title.
* Added position number to teams in `Forms for the Rest of the League` section.

### **Fixed**

* Fixing capitalization for `Forms for the Rest of the League` subheader.

### **Removed**

* Removed Emojis from tab titles.

## [1.2.0][1.2.0] - 2023-04-16

### **Changed**

Top Teams Tab
* Renamed tab to: "⚽️ Top Teams & 🏃🏻‍♂️ Top Scorers".
* Changed `st.plotly_chart` to `st.line_chart`.
* Moved top scorers to this tab.

### **Removed**

Top Players Tab
* Removed this tab, combined with top teams tab.

## [1.1.0][1.1.0] - 2023-04-07

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
* Removed `LIMIT 5` from SQL query to pull all teams.

## [1.0.0][1.0.0] - 2023-04-05

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

[1.3.0]: https://github.com/digitalghost-dev/premier-league/commit/4b2063a3663f48e166f7b13cbe06e51b24fd2056#diff-4dc66906e3c3b7f7a82967d85af564f2d5a6e0bee5829aa5eda607dd9756c87d

[1.2.0]: https://github.com/digitalghost-dev/premier-league/commit/8d5fbb7cdf91263eb55f2bc7ecd09236d975a704#diff-4dc66906e3c3b7f7a82967d85af564f2d5a6e0bee5829aa5eda607dd9756c87d

[1.1.0]: https://github.com/digitalghost-dev/premier-league/commit/e99f1f4a6eab3ef967c30b6c21b4fffa109de8e9#diff-4dc66906e3c3b7f7a82967d85af564f2d5a6e0bee5829aa5eda607dd9756c87d

[1.0.0]: https://github.com/digitalghost-dev/premier-league/commit/429a6f3ca12bcdbb5bee4505d390838b25edb8bb#diff-4dc66906e3c3b7f7a82967d85af564f2d5a6e0bee5829aa5eda607dd9756c87d