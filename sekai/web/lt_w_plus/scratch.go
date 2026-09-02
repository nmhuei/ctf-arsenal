package main

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/microcosm-cc/bluemonday"
)

func sanitizer(msg string) string {
	sanitized := bluemonday.StrictPolicy().Sanitize(msg)
	sanitized = strings.ReplaceAll(sanitized, "&lt;", "<")
	sanitized = strings.ReplaceAll(sanitized, "&gt;", ">")
	var reHTML = regexp.MustCompile(`<(/)?\w+`)
	sanitized = reHTML.ReplaceAllString(sanitized, "")
	return sanitized
}

func main() {
	payloads := []string{
		// Test various entity forms for < and >
		"<script>alert(1)</script>",
		"&lt;script&gt;alert(1)&lt;/script&gt;",
		"&#60;script&#62;alert(1)&#60;/script&#62;",
		"&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;",

		// Without semicolon variations
		"&lt script&gt;alert(1)",
		"&LT script&gt;alert(1)",

		// Uppercase without semicolon
		"&LTscript&gt;alert(1)&LT/script&gt;",
		"&LTimg src=x onerror=alert(1)&GT;",
		"&LTsvg onload=alert(1)&GT;",

		// Only uppercase without semicolons
		"&LTscript&GTalert(1)&LT/script&GT",

		// Mixed: LT without ; for opening, lt; for closing
		"&LTimg src=x onerror=alert(1)&gt;",

		// Validate if &LT (no ;) gets decoded by bluemonday
		"test &LT stuff",

		// What about &#x3C (without ;)
		"&#x3Cimg src=x onerror=alert(1)&#x3E",
	}

	fmt.Println("=== RAW BLUEMONDAY ===")
	for _, p := range payloads {
		r := bluemonday.StrictPolicy().Sanitize(p)
		fmt.Printf("INPUT:  %q\n", p)
		fmt.Printf("OUTPUT: %q\n\n", r)
	}

	fmt.Println("\n=== FULL SANITIZER ===")
	for _, p := range payloads {
		r := sanitizer(p)
		fmt.Printf("INPUT:  %q\n", p)
		fmt.Printf("OUTPUT: %q\n\n", r)
	}
}
