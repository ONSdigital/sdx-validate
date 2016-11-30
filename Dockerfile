FROM golang:1.7

ADD . /go/src/github.com/ONSDigital/sdx-validate

RUN go install github.com/ONSDigital/sdx-validate

EXPOSE 5000

ENTRYPOINT /go/bin/sdx-validate