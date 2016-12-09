package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"github.com/ONSdigital/sdx-validate/schema"
	"github.com/xeipuuv/gojsonschema"
)

func main() {
	port := "5000"

	if v := os.Getenv("PORT"); len(v) > 0 {
		port = v
	}

	http.HandleFunc("/validate", validateHandler)
	http.HandleFunc("/healthcheck", healthcheckHandler)

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func healthcheckHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{status":"OK"}`))
}

func validateHandler(w http.ResponseWriter, r *http.Request) {

	defer r.Body.Close()
	j, _ := ioutil.ReadAll(r.Body)

	// Check input is actually json
	var v interface{}
	if err := json.Unmarshal(j, &v); err != nil {
		log.Printf("Failure decoding data json: %v", err)
		sendReply(false, http.StatusInternalServerError, w)
		return
	}

	// TODO extract version numner to get schema and fail if it's
	// not there or not valid

	schemaLoader := gojsonschema.NewStringLoader(schema.V0_0_1) // TODO remove hardcode
	docLoader := gojsonschema.NewStringLoader(string(j))

	result, err := gojsonschema.Validate(schemaLoader, docLoader)
	if err != nil {
		panic(err)
	}

	if result.Valid() {
		log.Println("msg=\"Document is valid\"")
		sendReply(true, http.StatusOK, w)
		return
	}

	for _, desc := range result.Errors() {
		log.Printf("%s\n", desc)
	}
	sendReply(false, http.StatusOK, w)
	return
}

func sendReply(ok bool, status int, w http.ResponseWriter) {
	log.Printf("Sending reply: %v %v", ok, status)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	reply, err := json.Marshal(map[string]bool{"valid": ok})
	if err != nil {
		log.Printf("Marshal fail: %v", err)
		reply = []byte(`{"valid":false}`)
	}
	w.Write(reply)
}
