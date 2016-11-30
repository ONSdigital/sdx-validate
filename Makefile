build:
		go generate ./...
		go build -o build/sdx-validate

.PHONY: build