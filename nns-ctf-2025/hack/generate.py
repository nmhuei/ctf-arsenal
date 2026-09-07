#!/usr/bin/env python3

import requests
import os

challenges = requests.get("https://nnsc.tf/api/challenges").json()

for challenge in challenges:
    category = challenge["categories"][0]
    name = challenge["name"]
    dir = f"writeups/{category}/{name}"
    os.makedirs(dir, exist_ok=True)

    display_name = challenge["displayName"]
    description = challenge["description"]
    author = challenge["author"]
    category_header = "Category" if len(challenge["categories"]) < 2 else "Categories"
    categories = ", ".join(challenge["categories"])

    md = f"""
# {display_name}

- **Author:** {author}
- **{category_header}:** {categories}

## Description

{description}
    """.strip()

    with open(f"{dir}/README.md", "w") as f:
        f.write(md)
