import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import os
import datetime

# conection_string = "mongodb+srv://rafly:dbrafly@cluster0.lweon5s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(conection_string)
# db = client.dbsparta

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def dashboard():
    fruits_coll = list(db.fruits.find().sort("_id", DESCENDING))
    return render_template("dashboard.html", fruits_coll=fruits_coll)


@app.route("/fruits")
def fruits():
    fruits_coll = list(db.fruits.find().sort("_id", DESCENDING))
    return render_template("fruits.html", fruits_coll=fruits_coll)


@app.route("/fruit/add", methods=["GET", "POST"])
def addfruit():
    if request.method == "GET":
        return render_template("add-fruit.html")
    else:
        name = request.form.get("name")
        price = int(request.form.get("price"))
        description = request.form.get("description")
        image = request.files["image"]

        if image:
            save_to = "static/uploads"
            if not os.path.exists(save_to):
                os.makedirs(save_to)

            ext = image.filename.split(".")[-1]
            file_name = (
                f"fruit-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.{ext}"
            )
            image.save(f"{save_to}/{file_name}")

        db.fruits.insert_one(
            {
                "name": name,
                "price": price,
                "description": description,
                "image": file_name,
            }
        )

        flash("Berhasil menambahkan data buah")
        return redirect(url_for("fruits"))


@app.route("/fruit/edit/<id>", methods=["GET", "POST"])
def editfruit(id):
    if request.method == "GET":
        fruit = db.fruits.find_one({"_id": ObjectId(id)})
        return render_template("edit-fruit.html", fruit=fruit)
    else:
        name = request.form.get("name")
        price = int(request.form.get("price"))
        description = request.form.get("description")
        image = request.files["image"]

        if image:
            save_to = "static/uploads"
            fruit = db.fruits.find_one({"_id": ObjectId(id)})
            target = f"static/uploads/{fruit['image']}"

            if os.path.exists(target):
                os.remove(target)

            ext = image.filename.split(".")[-1]
            file_name = (
                f"fruit-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.{ext}"
            )
            image.save(f"{save_to}/{file_name}")

            db.fruits.update_one({"_id": ObjectId(id)}, {"$set": {"image": file_name}})

    db.fruits.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "name": name,
                "price": price,
                "description": description,
            }
        },
    )

    flash("Berhasil mengubah data buah")
    return redirect(url_for("fruits"))


@app.route("/fruit/delete/<id>", methods=["POST"])
def delete(id):
    fruit = db.fruits.find_one({"_id": ObjectId(id)})
    target = f"static/uploads/{fruit['image']}"

    if os.path.exists(target):
        os.remove(target)

    db.fruits.delete_one({"_id": ObjectId(id)})
    flash("berhasil mengahapus")
    return redirect(url_for("fruits"))


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
