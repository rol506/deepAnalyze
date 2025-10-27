from flask import Flask, abort, render_template, g, request, send_file, send_from_directory, url_for, redirect
from testShapes import processPair
from zipfile import ZIP_DEFLATED, ZipFile
import os
import logging
import sys

DEBUG = True

logging.basicConfig(encoding="utf-8", level=logging.DEBUG, 
                    format="%(levelname)s %(asctime)s %(message)s",
                    handlers=[logging.FileHandler("log.txt", ("w" if DEBUG else "w+")), logging.StreamHandler(sys.stdout)])

app = Flask(__name__)
app.config["DEBUG"] = DEBUG
app.template_folder = "../templates/"
app.static_folder = "../static/"

@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        request.files["first"].save("first.jpg")
        request.files["second"].save("second.jpg")

        processPair("first.jpg", "second.jpg")
        os.remove("first.jpg")
        os.remove("second.jpg")

        return redirect("/result")
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/resultDoc")
def resdoc():
    if os.path.exists("summary.docx"):
        return send_file("../summary.docx")
    else:
        return abort(403)

@app.route("/resultImg")
def resimg():
    if os.path.exists("result.jpg"):
        return send_file("../result.jpg", as_attachment=True)
    else:
        return abort(403)

@app.errorhandler(403)
def error403(err):
    return redirect(url_for("index"))

@app.errorhandler(404)
def error_404(err):
    return render_template("error_404.html")

@app.route("/style.css")
def style():
    return send_from_directory("../static/css/", "style.css")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4221)
