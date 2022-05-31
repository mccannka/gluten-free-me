"""Configuration"""
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


@app.route("/login", methods=["GET", "POST"])
def login_required():
    """
    Check whether the username exists in the database.
    If it does, check whether the input password matches
    the hashed password stored in the database for that username.
    If both are true, render the home page.
    If not, redirect to the login page with a message.
    """
    if request.method == "POST":
        # Check if username exists in db
        preidentified_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if preidentified_user:
            # Ensure hashed password matches user input
            if check_password_hash(
                preidentified_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back {}".format(request.form.get("username")))
                return redirect(url_for("user/personal"))
            else:
                # Invalid password match
                flash("Incorrect Username and/or Password.")
                return redirect(url_for("user/login"))

        else:
            # Username doesn't exist
            flash("Incorrect Username and/or Password.")
            return redirect(url_for("user/login"))

    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Define login functionality """
    if request.method == "POST":
        # check if username exists in db
        known_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if known_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    known_user["password"], request.form.get("password")):
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


def existing_user():
    """Existing member - Password validation"""
    return mongo.db.users.find_one(
        {"username": request.form.get("username").lower()})


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration for community member"""
    if request.method == "POST":
        if existing_user():
            flash("Oops, this username is not available!")
            return redirect(url_for("register"))

        initial_register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(initial_register)

        session["user"] = request.form.get("username").lower()
        return redirect(url_for("personal", username=session["user"]))

    return render_template("user/register.html")


def password_is_valid(identified_user):
    """Verify if valiad password input - existing user"""
    return check_password_hash(
        identified_user["password"], request.form.get("password"))


@app.route("/")
@app.route("/home")
def home():
    """Homepage endpoint"""
    return render_template("index.html")


@app.route("/about")
def about():
    """Define about option"""
    return render_template("about.html")


@app.route("/recipes")
def get_recipes():
    """Define homepage / recipes option"""
    return render_template("recipe/recipes.html")


@app.route("/recipe/<recipe_id>")
def specific_recipe(recipe_id):
    """Define recipe search page"""
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe/specific_recipes.html", recipe=recipe)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Recipe search functionality"""
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipe/recipes.html", recipes=recipes)


@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def personal(username):
    """Personalised recipe page"""
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session.get("user"):
        recipes = list(mongo.db.recipes.find().sort("_id", -1))
        return render_template(
            "user/personal.html", username=username, recipes=recipes)

    return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    """Logout validation path"""
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


def display_recipes(from_database):
    """Functionality to display recipes"""
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


@app.route("/recipe/add", methods=["GET", "POST"])
@login_required
def add_recipe():
    """Add recipe - logged in user"""
    if request.method == "POST":
        recipe = display_recipes(request)
        mongo.db.recipes.insert_one(recipe)
        flash("You've successfully shared your recipe")
        return redirect(url_for("personal", username=session["user"]))
    return render_template("recipe/add_recipes.html")


@app.route("/recipe/update/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    """Edit existing recipe - logged in user"""
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


@app.route("/recipe/delete/<recipe_id>")
@login_required
def delete_recipe(recipe_id):
    """Existing user - delete recope """
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


@app.errorhandler(404)
def page_not_found(error):
    """Error 404 error state"""
    print(error)
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Error 500 error state"""
    print(error)
    return render_template('errors/500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            # Note - change to debug=True for running locally
            debug=True)
