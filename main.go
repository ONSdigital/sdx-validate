package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"regexp"
)

// Survey is the incomming survey data to validate
type Survey struct {
	Type        string `json:"type"`
	Version     string `json:"version"`
	TXID        string `json:"tx_id"`
	Origin      string `json:"origin"`
	SurveyID    string `json:"survey_id"`
	SubmittedAt string `json:"submitted_at"`
	Collection  struct {
		Period       string `json:"period"`
		ExerciseSID  string `json:"exercise_sid"`
		InstrumentID string `json:"instrument_id"`
	} `json:"collection"`
	MetaData map[string]interface{} `json:"metadata"`
	Data     map[string]interface{} `json:"data"`
	Paradata map[string]interface{} `json:"paradata"`
}

var (
	validSurveyIDs = map[string]bool{
		"0":   true,
		"023": true,
	}

	validInstruments = map[string]bool{
		"hh2016": true,
		"ce2016": true,
		"0203":   true,
		"0213":   true,
		"0205":   true,
		"0215":   true,
		"0102":   true,
		"0112":   true,
	}
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
	var s Survey
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&s); err != nil {
		log.Printf("Failure decoding data json: %v", err)
		sendReply(false, http.StatusInternalServerError, w)
		return
	}
	defer r.Body.Close()

	// Do the actual validation!
	// Currently using the slightly clunky "manual validation" - should
	// ideally use json schema properly (current python doesn't)

	// Validate version
	if s.Version != "0.0.1" {
		log.Printf("Version '%v' not valid", s.Version)
		failValidation(w)
		return
	}

	// Validate survey id
	if _, ok := validSurveyIDs[s.SurveyID]; ok == false {
		log.Printf("Survey ID '%v' not valid", s.SurveyID)
		failValidation(w)
		return
	}

	// Validate instrument id
	if _, ok := validInstruments[s.Collection.InstrumentID]; ok == false {
		log.Printf("Instrument ID '%v' not valid", s.Collection.InstrumentID)
		failValidation(w)
		return
	}

	// Validate transaction id is a valid guid (if specified - it's optional otherwise)
	if s.TXID != "" {
		uuid := regexp.MustCompile("^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[8|9|aA|bB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$")
		if !uuid.MatchString(s.TXID) {
			log.Printf("Transaction ID '%v' not valid", s.TXID)
			failValidation(w)
			return
		}
	}

	sendReply(true, http.StatusOK, w)
}

func failValidation(w http.ResponseWriter) {
	sendReply(false, http.StatusOK, w)
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
