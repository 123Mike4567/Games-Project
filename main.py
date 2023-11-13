from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8hvgbhgvhgvg676887b'
Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///top_games.db'
db = SQLAlchemy()
db.init_app(app)

client_id = "Your_Client_ID"
access_token = "353fjm07n8smtadru23wchpvyw57oe"

# Set the URL for the IGDB API endpoint
api_url = "https://api.igdb.com/v4/games"

# Define the headers with the Client-ID and Authorization (Bearer token)
headers = {
    "Client-ID": "uunbhlj9ueil6dbxjyza9jktvgfird",
    "Authorization": f"Bearer {access_token}"
}
# Define the fields you want to retrieve
fields = "age_ratings,aggregated_rating,aggregated_rating_count,alternative_names,artworks,bundles,category,checksum,collection,collections,cover,created_at,dlcs,expanded_games,expansions,external_games,first_release_date,follows,forks,franchise,franchises,game_engines,game_localizations,game_modes,genres,hypes,involved_companies,keywords,language_supports,multiplayer_modes,name,parent_game,platforms,player_perspectives,ports,rating,rating_count,release_dates,remakes,remasters,screenshots,similar_games,slug,standalone_expansions,status,storyline,summary,tags,themes,total_rating,total_rating_count,updated_at,url,version_parent,version_title,videos,websites"

# Define the data payload as a string
data = f"fields {fields};"


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class RateGamesForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


# adding games
class AddGames(FlaskForm):
    title = StringField("Game Title", validators=[DataRequired()])
    submit = SubmitField("Add Game")


# ADDING NEW ENTRIES
""""

with app.app_context():
    new_game = Games(
        title="Dragon Ball Z: Budokai Tenkaichi",
        year=2005,
        description="Dragon Ball Z: Budokai Tenkaichi is a 3D fighting game based on the Dragon Ball Z series, featuring a wide range"
                    " of characters and intense battles with special moves and transformations ",
        rating=7.5,
        ranking=8,
        review="my favourte character was Vegeta",
        img_url="https://image.ceneostatic.pl/data/products/11401223/i-dragon-ball-z-budokai-tenkaichi-3-gra-ps2.jpg"
    )

    second_game = Games(
        title="uncharted:Thief's end",
        year=2007,
        description="Uncharted is an action-adventure video game franchise published by Sony Interactive Entertainment and developed by Naughty Dog. Created by Amy Hennig, the Uncharted franchise follows a group of treasure hunters who travel across the world to uncover various historical mysteries.",
        rating=9.0,
        ranking=6,
        review="my favourte character was Nathan Drake ",
        img_url="https://ocdn.eu/sport-images-transforms/1/8HBk9lBaHR0cHM6Ly9vY2RuLmV1L3B1bHNjbXMvTURBXy85ZThlOTNkMjY2YTk2OTk0YjExOTBjNjA3NTkwYmYxYy5qcGeTlQMAAM0DFM0Bu5MFzQSwzQJ0kwmmZDQxZDhjBt4AAqEwAaExAQ"
    )

    third_game = Games(
        title="Horizon zero Dawn ",
        year=2009,
        description="Horizon Zero Dawn is an action role-playing game played from a third-person view. Players take control of Aloy, a hunter who ventures through a post-apocalyptic land ruled by robotic creatures. ",
        rating=9.5,
        ranking=7,
        review="my favourte character was Aloy",
        img_url="https://i.guim.co.uk/img/media/c08abe837fb1b2ed9a41225fb4f0356c3c1dad27/0_0_955_573/master/955.png?width=1200&height=900&quality=85&auto=format&fit=crop&s=6f0ebce6a1d753fa8c2ef792c8d9fbe1"
    )
    # db.session.add(new_game)
    db.session.add(second_game)
    db.session.add(third_game)
    db.session.commit()
"""


# URL Home Page
@app.route("/")
def home():
    result = db.session.execute(db.select(Games))
    all_games = result.scalars().all()

    for i in range(len(all_games)):
        all_games[i].ranking = len(all_games) - i
    db.session.commit()
    return render_template("index.html", games=all_games)


@app.route("/edit", methods=["GET", "POST"])
def rate_game():
    form = RateGamesForm()
    game_id = request.args.get("id")
    game = db.get_or_404(Games, game_id)
    if form.validate_on_submit():
        game.rating = float(form.rating.data)
        game.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", game=game, form=form)


@app.route("/delete")
def delete_game():
    game_id = request.args.get("id")
    game_to_delete = db.get_or_404(Games, game_id)
    db.session.delete(game_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def add_game():
    form = AddGames()
    if form.validate_on_submit():
        game_title = form.title.data
        response = requests.post(api_url, headers=headers, data=data)
        game_data = response.json()

        # Extract names directly from the list of dictionaries
        options = [{"id": game["id"], "name": game.get("name", "No Name")} for game in game_data]

        return render_template("select.html", options=options)  # Pass the list of names to the template
    return render_template("add.html", form=form)


@app.route("/find", methods=["GET"])
def find_game():
    game_api_id = request.args.get("id")

    if game_api_id:
        # Construct the URL to fetch game details from the API
        game_api_url = f"{api_url}/{game_api_id}"

        # Make a GET request to the API to fetch game details
        response = requests.get(game_api_url, headers=headers)

        if response.status_code == 200:
            dataa = response.json()

            if dataa and len(dataa) > 0:
                game_data = dataa[0]  # Assuming you are interested in the first game's data
                img_url = game_data.get("cover", {}).get("url", "https://example.com/default-image.jpg")

                new_game = Games(
                    title=game_data.get("name", "No Title"),
                    year=game_data.get("first_release_date"),
                    img_url=img_url,
                    description=game_data.get("summary", "No summary available"),
                )
                db.session.add(new_game)
                db.session.commit()
                return redirect(url_for("rate_game", id=new_game.id))

    return render_template("error.html", error_message="Failed to retrieve game data from the API or no game found")


if __name__ == '__main__':
    app.run(debug=True)
