package main

import (
	"os"
	"fmt"
	"log"
	"net/http"
	"github.com/gin-gonic/gin"
)

 // location represents data about a stadium's location.
 type location struct {
     Team     string  `json:"team"`
     Stadium  string  `json:"stadium"`
     Latitude float64  `json:"latitude"`
     Longitude  float64 `json:"longitude"`
 }

 // locations slice to seed record album data.
 var locations = []location{
 	{Team: "Arsenal", Stadium: "Emirates Stadium", Latitude: 51.554867, Longitude: -0.109112},
 	{Team: "Aston Villa", Stadium: "Villa Park", Latitude: 52.509090, Longitude: -1.885249},
 	{Team: "Bournemouth", Stadium: "Vitality Stadium", Latitude: 50.7348, Longitude: -1.8391},
 	{Team: "Brighton", Stadium: "Falmer Stadium", Latitude: 50.861782, Longitude: -0.084357},
	{Team: "Brentford", Stadium: "Gtech Community Stadium", Latitude: 51.490715, Longitude: -0.289048},
 	{Team: "Chelsea", Stadium: "Stamford Bridge", Latitude: 51.481834, Longitude: -0.191390},
 	{Team: "Crystal Palace", Stadium: "Selhurst Park", Latitude: 51.398338, Longitude: -0.086084},
 	{Team: "Everton", Stadium: "Goodison Park", Latitude: 53.438751, Longitude: -2.966681},
 	{Team: "Fulham", Stadium: "Craven Cottage", Latitude: 51.281799, Longitude: -0.131080},
 	{Team: "Leeds", Stadium: "Elland Road", Latitude: 53.777782, Longitude: -1.573049},
 	{Team: "Leicester", Stadium: "King Power Stadium", Latitude: 52.620640, Longitude: -1.142770},
 	{Team: "Liverpool", Stadium: "Anfield", Latitude: 53.430759, Longitude: -2.961425},
    {Team: "Manchester City", Stadium: "Etihad Sadium", Latitude: 53.483135, Longitude: -2.200941},
    {Team: "Manchester United", Stadium: "Old Trafford", Latitude: 53.463493, Longitude: -2.292279},
 	{Team: "Newcastle", Stadium: "St James' Park", Latitude: 54.975170, Longitude: -1.622539},
 	{Team: "Nottingham Forest", Stadium: "City Ground", Latitude: 52.939938, Longitude: -1.13287},
 	{Team: "Southampton", Stadium: "Saint Mary's Stadium", Latitude: 50.906052, Longitude: -1.391692},
 	{Team: "Tottemham", Stadium: "Tottenham Hotspur Stadium", Latitude: 51.604252, Longitude: -0.067007},
 	{Team: "West Ham", Stadium: "London Stadium", Latitude: 51.538811, Longitude: -0.017136},
 	{Team: "Wolves", Stadium: "Molineux Stadium", Latitude: 52.590382, Longitude: -2.130924},
 }

 // getLocations responds with the list of all locations as JSON.
 func getLocations(c *gin.Context) {
     c.IndentedJSON(http.StatusOK, locations)
 }

 // setting up the root endpoint.
 func main() {
    router := gin.Default()
    router.GET("/locations", getLocations)

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