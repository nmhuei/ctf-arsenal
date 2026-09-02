package main

import (
	"bufio"
	"encoding/base64"
	"fmt"
	"os"
	"regexp"
	"strings"
	"unicode/utf8"

	"github.com/microcosm-cc/bluemonday"
)

func sanitizer(msg string) (string, error) {
	if len(msg) > 128 {
		return "", fmt.Errorf("too long message")
	}

	if utf8.ValidString(msg) == false {
		return "", fmt.Errorf("invalid character")
	}

	sanitized := bluemonday.StrictPolicy().Sanitize(msg)
	sanitized = strings.ReplaceAll(sanitized, "&lt;", "<")
	sanitized = strings.ReplaceAll(sanitized, "&gt;", ">")
	reHTML := regexp.MustCompile(`<(/)?\w+`)
	sanitized = reHTML.ReplaceAllString(sanitized, "")

	return sanitized, nil
}

func main() {
	sc := bufio.NewScanner(os.Stdin)
	sc.Buffer(make([]byte, 1024), 1024*1024)
	for sc.Scan() {
		raw, err := base64.StdEncoding.DecodeString(sc.Text())
		if err != nil {
			fmt.Printf("ERR\t%s\n", base64.StdEncoding.EncodeToString([]byte(err.Error())))
			continue
		}
		out, err := sanitizer(string(raw))
		if err != nil {
			fmt.Printf("ERR\t%s\n", base64.StdEncoding.EncodeToString([]byte(err.Error())))
			continue
		}
		fmt.Printf("OK\t%s\n", base64.StdEncoding.EncodeToString([]byte(out)))
	}
	if err := sc.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "scan: %v\n", err)
		os.Exit(1)
	}
}
