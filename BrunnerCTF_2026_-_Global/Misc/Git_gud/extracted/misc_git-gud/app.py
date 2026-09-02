import subprocess
import os
import hashlib
import tempfile

from flask import Flask, request, render_template

app = Flask(__name__)

REPO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repos")


@app.route("/")
def index():
    return render_template("index.html")

def generate_random_name():
    rand_bytes = os.urandom(32)
    return hashlib.sha256(rand_bytes).hexdigest()

def untar_to_dir(tar_path: str, dest_root: str) -> bool:
    os.makedirs(dest_root, exist_ok=True)
    p = subprocess.run(
        ["tar", "-xf", tar_path, "-C", dest_root],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return p.returncode == 0

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "no file provided"}, 400

    uploaded = request.files["file"]
    if uploaded.filename == "":
        return {"error": "no file selected"}, 400

    if not uploaded.filename.endswith(".tar"):
        return {"message": "You must upload a tar file"}, 400
    
    tar_path = os.path.join(tempfile.gettempdir(), f"{generate_random_name()}.tar")
    uploaded.save(tar_path)

    rand_name = generate_random_name()
    user_repo_dir = os.path.join(REPO_DIR, rand_name)
    os.mkdir(user_repo_dir)

    untar_to_dir(tar_path, user_repo_dir)

    return {"message": "Git repo uploaded and saved", "id": rand_name}, 200


@app.route("/stats/<repo_id>")
def stats(repo_id):
    repo_dir = os.path.join(REPO_DIR, repo_id)

    if not os.path.isdir(repo_dir):
        return {"error": "unknown id"}, 404

    status_out, err = run_git_command(["status", "--porcelain"], repo_dir)
    if err is not None:
        return {"error": "git status failed", "detail": err}, 500

    log_out, err = run_git_command(
        ["log", "--numstat", "--date=iso-strict",
         "--format=commit%x1f%H%x1f%ad%x1f%an%x1f%ae"],
        repo_dir,
    )
    if err is not None:
        return {"error": "git log failed", "detail": err}, 500

    return {
        "id": repo_id,
        "repo_dir": repo_dir,
        "status": parse_git_status(status_out),
        "commits": parse_git_log(log_out),
    }, 200


def run_git_command(args: list, workdir: str):
    try:
        p = subprocess.run(
            ["git", "-C", workdir] + args,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return None, str(e)

    if p.returncode != 0:
        return None, p.stderr.decode(errors="replace").strip()

    return p.stdout.decode(errors="replace"), None


def parse_git_status(output: str) -> list:
    entries = []
    for line in output.splitlines():
        if not line:
            continue

        index_status, worktree_status = line[0], line[1]
        path = line[3:]
        old_path = None

        # Renames/copies are formatted as "old -> new".
        if " -> " in path:
            old_path, path = path.split(" -> ", 1)

        entries.append({
            "index": index_status,
            "worktree": worktree_status,
            "path": path,
            "old_path": old_path,
        })
    return entries


def parse_git_log(output: str) -> list:
    commits = []
    current = None

    for line in output.splitlines():
        if line.startswith("commit\x1f"):
            _, commit_id, date, author, email = line.split("\x1f", 4)
            current = {
                "id": commit_id,
                "date": date,
                "author": author,
                "email": email,
                "added": 0,
                "removed": 0,
            }
            commits.append(current)
        elif line.strip() and current is not None:
            cols = line.split("\t")
            if len(cols) < 2:
                continue
            added, removed = cols[0], cols[1]
            if added.isdigit():
                current["added"] += int(added)
            if removed.isdigit():
                current["removed"] += int(removed)

    return commits
