package main

import "fmt"

func main() {
    for _, s := range []string{
        "target: null\nintegrations: [edge]\n",
        "target: {}\nintegrations: [edge]\n",
        "target:\n  plane: null\nintegrations: [edge]\n",
        "target: !!null null\nintegrations: [edge]\n",
    } {
        c, err := decodeSite(s)
        fmt.Printf("%q => plane=%q sa=%q aud=%q err=%v\n", s, c.Target.Plane, c.serviceAccountName(), c.audience(), err)
    }
}
