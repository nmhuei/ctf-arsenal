package main

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/microcosm-cc/bluemonday"
)

func main() {
	payloads := []string{
		"<<script>",
		"a<b",
		"a<b>c",
		"<",
		"<!x>",
		"<!--x-->",
		"<αβγ>",
		"<\nscript>",
		"<\tscript>",
		"&lt;!x&gt;",
		"&lt;!--&gt;",
		"&lt;!&lt;script&gt;&gt;",
		"&lt;!x&gt;&lt;script&gt;alert(1)&lt;/script&gt;",
	}
	for _, p := range payloads {
		s1 := bluemonday.StrictPolicy().Sanitize(p)
		s2 := strings.ReplaceAll(s1, "&lt;", "<")
		s2 = strings.ReplaceAll(s2, "&gt;", ">")
		re := regexp.MustCompile(`<(/)?\w+`)
		s3 := re.ReplaceAllString(s2, "")
		fmt.Printf("IN: %q -> OUT: %q\n", p, s3)
	}
}
