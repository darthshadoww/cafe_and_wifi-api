from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def get_random_cafe():
    # Get the total number of cafes in the database
    total_cafes = db.session.query(Cafe).count()
    # Generate a random index within the range of cafe IDs
    rand_id = random.randint(1, total_cafes)
    # Get the cafe with the randomly generated ID
    rand_cafe = Cafe.query.get(rand_id)

    if rand_cafe is not None:
        # Create a dictionary representation of the cafe
        cafe_data = {
            "name": rand_cafe.name,
            "map_url": rand_cafe.map_url,
            "img_url": rand_cafe.img_url,
            "location": rand_cafe.location,
            "seats": rand_cafe.seats,
            "has_toilet": rand_cafe.has_toilet,
            "has_wifi": rand_cafe.has_wifi,
            "has_sockets": rand_cafe.has_sockets,
            "can_take_calls": rand_cafe.can_take_calls,
            "coffee_price": rand_cafe.coffee_price
        }
        return jsonify(cafe_data)
    else:
        return jsonify({"message": "No cafes found."}), 404
## HTTP GET - Read Record
@app.route("/all", methods=["GET"])
def get_all_cafes():
    # Get all cafe records from the database
    all_cafes = Cafe.query.all()

    # Create a list to hold the data for all cafes
    cafes_data = []

    # Loop through each cafe record and create a dictionary representation
    for cafe in all_cafes:
        cafe_data = {
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        }
        cafes_data.append(cafe_data)

    # Return the list of cafe data as a JSON response
    return jsonify(cafes_data)

## HTTP POST - Create Record
@app.route("/search", methods=["GET"])
def search_cafes():
    # Get the 'loc' query parameter from the URL
    location = request.args.get('loc', '').strip()

    if not location:
        return jsonify({"message": "Please provide a valid 'loc' parameter."}), 400

    # Search for cafes at the specified location in the database
    cafes_at_location = Cafe.query.filter_by(location=location).all()

    # Create a list to hold the data for cafes at the specified location
    cafes_data_at_location = []

    # Loop through each cafe record and create a dictionary representation
    for cafe in cafes_at_location:
        cafe_data = {
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        }
        cafes_data_at_location.append(cafe_data)

    # Return the list of cafe data at the specified location as a JSON response
    return jsonify(cafes_data_at_location)
## HTTP PUT/PATCH - Update Record


from sqlalchemy.exc import IntegrityError

@app.route("/add", methods=["GET", "POST"])
def add_a_cafe():
    print("Request JSON Data:", request.get_json())  # Add this line to print the JSON data received in the request
    try:
        data = request.get_json()
        new_cafe = Cafe(
            name=data.get("name"),
            map_url=data.get("map_url"),
            img_url=data.get("img_url"),
            location=data.get("location"),
            seats=data.get("seats"),
            has_toilet=bool(data.get("has_toilet")),
            has_wifi=bool(data.get("has_wifi")),
            has_sockets=bool(data.get("has_sockets")),
            can_take_calls=bool(data.get("can_take_calls")),
            coffee_price=data.get("coffee_price")
        )
        db.session.add(new_cafe)
        db.session.commit()

        return jsonify(response={"success": "Successfully added the new cafe"})
    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e.orig)
        return jsonify(response={"error": error_msg}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(response={"error": str(e)}), 500


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])  # Note the <int:cafe_id> to convert the parameter to an integer
def update(cafe_id):
    data = request.get_json()
    print(data)
    new_price = data.get("new_price")  # Get the new_price from the request JSON data
    print(new_price)
    # Find the cafe record with the given cafe_id in the database
    cafe = Cafe.query.get(cafe_id)

    if cafe:
        # Update the coffee_price of the cafe
        cafe.coffee_price = new_price

        # Commit the changes to the database
        db.session.commit()

        return jsonify(response={"success": "Coffee price updated successfully."})
    else:
        return jsonify(response={"error": "Cafe not found."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def deleting(cafe_id):
    api_key = request.args.get("api-key")  # Use query parameter for api-key
    cafe = Cafe.query.get(cafe_id)
    if api_key == "123":  # Note the api_key is a string, so compare it with a string
        if cafe:
            # Delete the cafe record from the database
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Cafe deleted successfully."}), 200
        else:
            return jsonify(response={"error": "Cafe not found."}), 404
    else:
        return jsonify(response={"error": "You are not allowed to do that."}), 403

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
