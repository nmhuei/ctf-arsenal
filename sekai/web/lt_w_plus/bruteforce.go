package main

import (
	"fmt"
	"regexp"
	"strings"
	"os"
	"github.com/microcosm-cc/bluemonday"
)

func sani(msg string) string {
	if len(msg) > 128 { return "" }
	s1 := bluemonday.StrictPolicy().Sanitize(msg)
	s2 := strings.ReplaceAll(s1, "&lt;", "<")
	s2 = strings.ReplaceAll(s2, "&gt;", ">")
	return regexp.MustCompile(`<(/)?\w+`).ReplaceAllString(s2, "")
}

func main() {
	// Key idea: what if the challenge solution involves 
	// creating a < followed by non-ASCII letter that HTML 
	// treats differently due to CHROME-SPECIFIC quirks?
	
	// Test: what if we use Unicode subscripts/superscripts 
	// that LOOK like ASCII letters?
	
	js := "console.log(document.cookie)"
	
	// Collect ALL non-ASCII characters that could be confused with ASCII letters
	// after a < to form a valid tag in Chrome
	
	// Script-like non-ASCII "s" chars
	s_variants := []string{
		"s",  // ASCII - should be stripped
		"ş", // ş (latin small letter s with cedilla)
		"š", // š (latin small letter s with caron)
		"ѕ", // ѕ (cyrillic small letter dze)
		"ʃ", // ʃ (ezh, looks like s)
		"ⅴ", // ⅴ (small roman numeral six - actually looks different)
	}
	
	for _, s := range s_variants {
		payload := "&lt;" + s + "cript&gt;" + js + "&lt;/" + s + "cript&gt;"
		out := sani(payload)
		fmt.Printf("s=%q (U+%04X) -> %q\n", s, []rune(s)[0], out)
		// Check if it survived
		if strings.Contains(out, s) || strings.Contains(out, "<") {
			fmt.Printf("  ^^^ SURVIVED!\n")
		}
	}
	
	// Test with all Unicode letters after <
	fmt.Println("\n--- All Unicode categories after <?")
	for _, r := range []rune{
		'à', // à (latin small letter a with grave)
		'á', // á
		'â', // â
		'ä', // ä
		'é', // é
		'è', // è
		'ü', // ü
		'ā', // ā
		'ɑ', // ɑ (latin small letter alpha)
		'α', // α (greek small letter alpha)
		'а', // а (cyrillic small letter a)
		'ａ', // ａ (fullwidth latin small letter a)
		'ᴀ', // ᴀ (latin letter small capital a)
	} {
		payload := "&lt;" + string(r) + "&gt;test"
		out := sani(payload)
		fmt.Printf("r=%q (U+%04X) -> %q\n", r, r, out)
		if strings.Contains(out, "<") {
			fmt.Printf("  ^^^ SURVIVED!\n")
		}
	}
	
	fmt.Println("\n--- What about numeric entities for punctuation? ---")
	
	// Can we use entities for chars like /, =, etc. to affect parsing?
	// &sol; = /, &equals; = =
	for _, test := range []struct{input, label string} {
		{"&lt;script&sol;&gt;alert(1)&lt;&sol;script&gt;", "slash"},
		{"&lt;script&NewLine;&gt;alert(1)&lt;&sol;script&gt;", "newline"},
		{"&lt;script&Tab;&gt;alert(1)&lt;&sol;script&gt;", "tab"},
		{"&lt;script&gt;alert(1)&lt;&sol;script&gt;", "normal"},
	} {
		out := sani(test.input)
		fmt.Printf("%s: %q\n", test.label, out)
	}

	os.Exit(0)
}
