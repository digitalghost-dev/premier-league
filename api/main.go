package main

import (
	"os"
	"fmt"
	"log"
	"net/http"
	"github.com/gin-gonic/gin"
)

// data structure
type stadium struct {
	Team         string   `json:"team"`
	Stadium      string   `json:"stadium"`
	City         string   `json:"city"`
	Latitude     float64  `json:"latitude"`
	Longitude    float64  `json:"longitude"`
	Capacity     string   `json:"capacity"`
	Year_Opened  string   `json:"year_opened"`
}

var stadiums = []stadium{
	{Team: "Arsenal", Stadium: "Emirates Stadium", City: "London", Latitude: 51.554867, Longitude: -0.109112, Capacity: "60,704", Year_Opened: "2006"},
	{Team: "Aston Villa", Stadium: "Villa Park", City: "Birmingham", Latitude: 52.509090, Longitude: -1.885249, Capacity: "42,657", Year_Opened: "1897"},
	{Team: "Bournemouth", Stadium: "Vitality Stadium", City: "Bournemouth", Latitude: 50.7348, Longitude: -1.8391, Capacity: "11,307", Year_Opened: "1910"},
	{Team: "Brentford", Stadium: "Gtech Community Stadium", City: "London", Latitude: 51.490715, Longitude: -0.289048, Capacity: "17,250", Year_Opened: "2020"},
	{Team: "Brighton", Stadium: "Falmer Stadium", City: "Falmer", Latitude: 50.861782, Longitude: -0.084357, Capacity: "31,800", Year_Opened: "2011"},
	{Team: "Burnley", Stadium: "Turf Moor", City: "Burnley", Latitude: 53.789108, Longitude: -2.230575, Capacity: "21,944", Year_Opened: "1883"},
	{Team: "Chelsea", Stadium: "Stamford Bridge", City: "London", Latitude: 51.481834, Longitude: -0.191390, Capacity: "40,343", Year_Opened: "1877"},
	{Team: "Crystal Palace", Stadium: "Selhurst Park", City: "London", Latitude: 51.398338, Longitude: -0.086084, Capacity: "25,486", Year_Opened: "1924"},
	{Team: "Everton", Stadium: "Goodison Park", City: "Liverpool", Latitude: 53.438751, Longitude: -2.966681, Capacity: "39,414", Year_Opened: "1892"},
	{Team: "Fulham", Stadium: "Craven Cottage", City: "London", Latitude: 51.281799, Longitude: -0.131080, Capacity: "29,600", Year_Opened: "1896"},
	{Team: "Liverpool", Stadium: "Anfield", City: "Liverpool", Latitude: 53.430759, Longitude: -2.961425, Capacity: "53,394", Year_Opened: "1884"},
	{Team: "Luton Town", Stadium: "Kenilworth Road", City: "Luton", Latitude: 51.883829798, Longitude: -0.425664964, Capacity: "10,356", Year_Opened: "1905"},
	{Team: "Manchester City", Stadium: "Etihad Sadium", City: "Manchester", Latitude: 53.483135, Longitude: -2.200941, Capacity: "53,400", Year_Opened: "2003"},
	{Team: "Manchester United", Stadium: "Old Trafford", City: "Manchester", Latitude: 53.463493, Longitude: -2.292279, Capacity: "74,310", Year_Opened: "1910"},
	{Team: "Newcastle", Stadium: "St James' Park", City: "Newcastle upon Tyne", Latitude: 54.975170, Longitude: -1.622539, Capacity: "52,305", Year_Opened: "1892"},
	{Team: "Nottingham Forest", Stadium: "City Ground", City: "West Bridgford", Latitude: 52.939938, Longitude: -1.13287, Capacity: "30,332", Year_Opened: "1898"},
	{Team: "Sheffield United", Stadium: "Bramall Lane", City: "Sheffield", Latitude: 53.368831858, Longitude: -1.46916479, Capacity: "32,050", Year_Opened: "1855"},
	{Team: "Tottemham", Stadium: "Tottenham Hotspur Stadium", City: "London", Latitude: 51.604252, Longitude: -0.067007, Capacity: "62,850", Year_Opened: "2019"},
	{Team: "West Ham", Stadium: "London Stadium", City: "London", Latitude: 51.538811, Longitude: -0.017136, Capacity: "62,500", Year_Opened: "2012"},
	{Team: "Wolves", Stadium: "Molineux Stadium", City: "Wolverhampton", Latitude: 52.590382, Longitude: -2.130924, Capacity: "31,750", Year_Opened: "1889"},
}

// getStadium responds with the list of all stadiums as JSON.
func getStadium(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, stadiums)
}

// setting up the endpoint.
func main() {
	router := gin.Default()
	router.GET("/stadiums", getStadium)

	router.Run()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/v1/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "{status: 'running'}")
	})

	log.Println("listening on port", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Error launching REST API server: %v", err)
	}
}