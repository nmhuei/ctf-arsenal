from flask import Flask, request, render_template
from utils import restricted_loads, make_request

app = Flask(__name__)
app.config.from_object("config.Config")

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/office")
def office():
  return render_template("office.html")

@app.route("/office-process", methods = ["POST"])
def process():
  if request.method == "POST":
    uploaded_file = request.files['file']
    restricted_loads(uploaded_file.read())
    
    return "It works!", 200

@app.route("/healthcheck")
def healthcheck():
  method = request.args.get("method", "GET")
  url = request.args.get("url", "")
  headers = request.args.get("headers", '{}')

  statuscode = make_request(method=method, url=url, headers=headers)
  return f"{statuscode}"


