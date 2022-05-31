# Imports & Config
from functools import wraps
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Login required
# Requires login for enhanced functionality


def login_required(f):
    @wraps(f)
    def login(*args, **kwargs):
        if "user" in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged to proceed!")
            return redirect(url_for("login"))
    return login


# Define homepage / login option
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("personal", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("user/login.html")


# Community member - Password validation
def existing_user():
    return mongo.db.users.find_one(
        {"username": request.form.get("username").lower()})


# Registration for community member
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if existing_user():
            flash("Oops, this username is not available!")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        return redirect(url_for("personal", username=session["user"]))

    return render_template("user/register.html")


def password_is_valid(existing_user):
    return check_password_hash(
        existing_user["password"], request.form.get("password"))


# Define homepage / index option
@app.route("/")
def index():
    return render_template("index.html")


# Define homepage / about option
@app.route("/about")
def about():
    return render_template("about.html")


#  Define homepage / recipes option
@app.route("/recipes")
def get_recipes():
    return render_template("recipe/recipes.html")


# Standalone recipe page
@app.route("/recipe/<recipe_id>")
def specific_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe/specific_recipes.html", recipe=recipe)


# Recipe search functionality
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipe/recipes.html", recipes=recipes)


# Personalised recipe page
@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def personal(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session.get("user"):
        recipes = list(mongo.db.recipes.find().sort("_id", -1))
        return render_template(
            "user/personal.html", username=username, recipes=recipes)

    return redirect(url_for("login"))


# Log out
@app.route("/logout")
@login_required
def logout():
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Functionality to display recipes
def display_recipes(request):
    return {
        "recipe_name": request.form.get("recipe_name"),
        "recipe_overview": request.form.get("recipe_overview"),
        "recipe_preparation_time": request.form.get(
            "recipe_preparation_time"),
        "recipe_servings": request.form.get("recipe_servings"),
        "recipe_ingredients": request.form.getlist("recipe_ingredients"),
        "recipe_instruction": request.form.getlist("recipe_instruction"),
        "recipe_image_1": request.form.get("recipe_image_1"),
        "recipe_image_2": request.form.get("recipe_image_2"),
        "recipe_created_by": session["user"]
    }


# Add recipe
@app.route("/recipe/add", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        recipe = display_recipes(request)
        mongo.db.recipes.insert_one(recipe)
        flash("You've successfully shared your recipe")
        return redirect(url_for("personal", username=session["user"]))
    return render_template("recipe/add_recipes.html")


# Edit recipe
@app.route("/recipe/update/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    if "user" in session:

        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        if session["user"] == 'admin':

            if request.method == "POST":
                save = display_recipes(request)
                mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, save)
                flash("Your recipe has been updated successfully")
                return redirect(url_for("personal", username=session["user"]))
            recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
            return render_template(
                "recipe/edit_recipes.html", recipe=recipe)

        elif session["user"].lower() == recipe["recipe_created_by"].lower():

            if request.method == "POST":
                save = display_recipes(request)
                mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, save)
                flash("Your recipe has been updated successfully")
                return redirect(url_for("personal", username=session["user"]))
                
            recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
            return render_template(
                "recipe/edit_recipes.html", recipe=recipe)

        flash("Oops, you can't edit other user's recipes.")
        return redirect(url_for("index"))

    flash("Oops, you can't edit other user's recipes.")
    return redirect(url_for("index"))


# Delete recipe
@app.route("/recipe/delete/<recipe_id>")
@login_required
def delete_recipe(recipe_id):
    if "user" in session:

        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        if session["user"] == 'admin':
            mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
            flash("Your recipe has been deleted successfully")
            return redirect(url_for("recipes"))

        elif session["user"].lower() == recipe["recipe_created_by"].lower():
            mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
            flash("Your recipe has been deleted successfully")
            return redirect(url_for("recipes"))

    flash("Oops, you can't edit other user's recipes.")
    return redirect(url_for("index"))


# Error states
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
