# Sur Kharvaa

**Category:** misc

Sûr kharvaa - archery. You loose one arrow of Python at the target and it tells
you what the arrow did.

## The range

An *arrow* is a program. You loose it by POSTing its raw bytes to `/shoot`:

```sh
curl --data-binary @arrow.py https://sur-kharvaa.<host>/shoot
```

The target reads the arrow, judges it, and - if it lets the arrow fly - runs it
in a throwaway sandbox and returns whatever it printed on stdout.

## The target

`target.py` in this handout is the whole of the target, served live at
`/target.py`. It is exactly what runs. Nothing about the first puzzle is hidden:
read it.

## Two marks

Striking the target is the first mark. The second is the range itself: it
belongs to the keeper, and only the keeper may read the day's record. What you
need for the second mark is on the range once you are standing on it.

The flag is minted fresh for whoever reads the record, so it is yours alone.
