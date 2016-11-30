package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	. "github.com/smartystreets/goconvey/convey"
)

var (
	goodData = `{
       "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
       "type": "uk.gov.ons.edc.eq:surveyresponse",
       "origin": "uk.gov.ons.edc.eq",
       "survey_id": "023",
       "version": "0.0.1",
       "collection": {
         "exercise_sid": "hfjdskf",
         "instrument_id": "0203",
         "period": "0216"
       },
       "submitted_at": "2016-03-12T10:39:40Z",
       "metadata": {
         "user_id": "789473423",
         "ru_ref": "12345678901A"
       },
       "data": {
         "11": "01/04/2016",
         "12": "31/10/2016",
         "20": "1800000",
         "51": "84",
         "52": "10",
         "53": "73",
         "54": "24",
         "50": "205",
         "22": "705000",
         "23": "900",
         "24": "74",
         "25": "50",
         "26": "100",
         "21": "60000",
         "27": "7400",
         "146": "some comment"
       },
       "paradata": {}
    }`
)

func sendToEndpoint(data string) (code int, valid bool, err error) {
	log.Println("[test] POSTING to endpoint")
	req, err := http.NewRequest("POST", "/validate", bytes.NewBufferString(data))
	if err != nil {
		log.Fatal("Unable to create new HTTP request")
		return
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(validateHandler)

	handler.ServeHTTP(rr, req)

	body := rr.Body.Bytes()
	if body == nil {
		err = errors.New("Empty body returned from endpoint")
		log.Printf("%v", err)
		return
	}

	r := make(map[string]bool)
	err = json.Unmarshal(body, &r)
	if err != nil {
		log.Fatalf("Failed to unmarshal reply: %v", err)
		return
	}

	code = rr.Code
	valid = r["valid"]
	return
}

func amendSurveyValue(data, key string, value interface{}) (string, error) {

	var surveyMap map[string]interface{}
	So(json.Unmarshal([]byte(data), &surveyMap), ShouldBeNil)

	// Deal with the key being nested
	for i, k := range strings.Split(key, ".") {
		switch {
		case i == strings.Count(key, "."):
			switch value {
			case nil:
				delete(surveyMap, k) // if requested 'nil' then delete the key
			default:
				surveyMap[k] = value
			}
		default:
			surveyMap = surveyMap[k].(map[string]interface{})
		}
	}

	amended, err := json.Marshal(surveyMap)
	if err != nil {
		return "", err
	}
	return string(amended), nil
}

func TestFailSends500(t *testing.T) {
	Convey("Should return 500 when sent non-JSON data", t, func() {
		code, valid, err := sendToEndpoint(`rubbish`)
		if err != nil {
			t.Fatalf("Test to endpoint failed: %v [%v %v]", err, code, valid)
		}
		So(code, ShouldEqual, http.StatusInternalServerError)
		So(valid, ShouldBeFalse)
	})
}

func TestOKWithValidJSON(t *testing.T) {
	Convey("Should return valid when data is valid", t, func() {
		code, valid, err := sendToEndpoint(goodData)
		if err != nil {
			t.Fatalf("Sending to endpoint failed: %v", err)
		}
		So(code, ShouldEqual, http.StatusOK)
		So(valid, ShouldBeTrue)
	})
}

func TestFailWhenDataEmpty(t *testing.T) {
	Convey("When data is empty", t, func() {
		code, valid, err := sendToEndpoint("")
		if err != nil {
			t.Fatalf("Sending to endpoint failed: %v", err)
		}
		So(code, ShouldEqual, http.StatusInternalServerError) // TODO should this be 500? Or should it be 200 OK?
		So(valid, ShouldBeFalse)
	})
}

func TestTransactionIDIsOptional(t *testing.T) {
	Convey("When sending data without transaction id (tx_id)", t, func() {

		sa, err := amendSurveyValue(goodData, "tx_id", nil)
		if err != nil {
			t.Fatalf("Error attempting to delete tx_id from survey data")
		}

		code, valid, err := sendToEndpoint(sa)
		if err != nil {
			t.Fatalf("Sending to endpoint failed: %v", err)
		}
		So(code, ShouldEqual, http.StatusOK)
		So(valid, ShouldBeTrue)
	})
}

func TestInvalidItems(t *testing.T) {

	type invalidItemTestSet struct {
		Name   string
		Field  string
		Values []string
	}

	ts := []invalidItemTestSet{
		invalidItemTestSet{
			Name:   "version",
			Field:  "version",
			Values: []string{"0.0.0", "9.9.9"},
		},
		invalidItemTestSet{
			Name:   "survey ids",
			Field:  "survey_id",
			Values: []string{"999", "029"},
		},
		invalidItemTestSet{
			Name:   "instrument ids",
			Field:  "collection.instrument_id",
			Values: []string{"999", "111"},
		},
	}

	Convey("When using invalid values", t, func() {
		for _, set := range ts {
			Convey(fmt.Sprintf("For %v", set.Name), func() {

				for _, value := range set.Values {
					sl, err := amendSurveyValue(goodData, set.Field, value)

					if err != nil {
						t.Fatalf("Error attempting to amend survey value: %v", err)
					}

					code, valid, err := sendToEndpoint(sl)
					if err != nil {
						t.Fatalf("Error returned from endpoint: %v", err)
					}

					Convey(fmt.Sprintf("With %s set to %s", set.Field, value), func() {
						So(code, ShouldEqual, http.StatusOK)
						So(valid, ShouldBeFalse)
					})
				}
			})
		}
	})
}

func TestNonGUIDTransactionIDIsInvalid(t *testing.T) {
	Convey("When submitting data", t, func() {
		for _, v := range []string{
			"999", // Bad
			"f81d4fae-7dec-11d0-a765-00a0c91e6bf",  // Last char missing
			"f81d4fae-7dec-11d0-z765-00a0c91e6bf6", // Wrong char in 17th position}
		} {
			Convey(fmt.Sprintf("With tx_id of '%v'", v), func() {
				sa, err := amendSurveyValue(goodData, "tx_id", v)
				if err != nil {
					t.Fatalf("Error attempting to set tx_id to %v", v)
				}
				code, valid, err := sendToEndpoint(sa)
				if err != nil {
					t.Fatalf("Error returned from endpoint: %v", err)
				}
				So(code, ShouldEqual, http.StatusOK)
				So(valid, ShouldBeFalse)
			})
		}
	})
}
