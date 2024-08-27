package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/a-h/templ"
	"github.com/gin-gonic/gin"
)

type Recipe struct {
	Title            string   `json:"title"`
	Author           string   `json:"author"`
	CookTime         *int     `json:"cook_time,omitempty"`
	Host             string   `json:"host"`
	TotalTime        *int     `json:"total_time,omitempty"`
	Image            string   `json:"image"`
	Ingredients      []string `json:"ingredients"`
	Instructions     string   `json:"instructions"`
	InstructionsList []string `json:"instructions_list"`
	Language         string   `json:"language"`
	SiteName         string   `json:"site_name"`
}

func render(c *gin.Context, status int, template templ.Component) error {
	c.Status(status)
	return template.Render(c.Request.Context(), c.Writer)
}

func main() {
	r := gin.Default()

	r.GET("/", func(c *gin.Context) {
		render(c, 200, home())
	})

	r.GET("/recipe", func(c *gin.Context) {

		recipeUrl := c.Query("url")
		response, err := http.Get("http://127.0.0.1:8000/recipe?url=" + recipeUrl)

		if err != nil {
			log.Println(err)
			c.JSON(500, gin.H{
				"message": "error",
			})
			return
		}
		defer response.Body.Close()

		log.Println(response.Body)

		recipe := Recipe{}

		err = json.NewDecoder(response.Body).Decode(&recipe)

		if err != nil {
			log.Println(err)
			c.JSON(500, gin.H{
				"message": "error",
			})
			return
		}

		render(c, 200, recipe_tmpl(recipe))
	})
	r.Run(":8081")
}
