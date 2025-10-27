from flask import Flask, render_template, g, request, send_file, send_from_directory, url_for, redirect
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

        z = ZipFile("result.zip", "w", compression=ZIP_DEFLATED)
        z.write("result.jpg")
        z.write("summary.docx")
        z.close()
        os.remove("result.jpg")
        os.remove("summary.docx")
        return send_file("../result.zip")
    return render_template("index.html")

@app.errorhandler(404)
def error404(err):
    return redirect(url_for("index"))

@app.route("/style.css")
def style():
    return send_from_directory("../static/css/", "style.css")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4221)
