"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Personajes, Planetas, Favoritos_Personajes, Favoritos_Planetas
from sqlalchemy import insert, delete

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# Endpoint para traer todos los datos de la tabla Personajes
@app.route('/people', methods=['GET'])
def get_people():

    # Creamos las variables para los personajes de la tabla Personajes
    people=Personajes.query.all()
    all_people = [character.serialize() for character in people]

    # Retornamos todos los personajes de la tabla Personajes
    return jsonify(all_people), 200

# Endpoint para traer los datos de un personaje en concreto
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):

    # Creamos las variables para el personaje indicado de la tabla Personajes
    character_query=Personajes.query.filter_by(id = people_id).all()
    character = [character.serialize() for character in character_query]

    # Retornamos el personaje indicado de tabla Personajes
    return jsonify(character), 200

# Endpoint para traer todos los datos de la tabla Planetas
@app.route('/planets', methods=['GET'])
def get_planets():

    # Creamos las variables para los planetas de la tabla Planetas
    planets=Planetas.query.all()
    all_planets = [planet.serialize() for planet in planets]

    # Retornamos todos los planetas de la tabla Planetas
    return jsonify(all_planets), 200

# Endpoint para traer los datos de un planeta en concreto
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):

    # Creamos las variables para el planeta indicado de la tabla Planetas
    planet_query=Planetas.query.filter_by(id = planet_id).all()
    planet = [planet.serialize() for planet in planet_query]

    # Retornamos el planeta indicado de tabla Planetas
    return jsonify(planet), 200

@app.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    new_person = Personajes(
        name=data['name'],
        hair_color=data['hair_color'],
        eye_color=data['eye_color'],
        skin_color=data['skin_color'],
        gender=data['gender'],
        height=data['height'],
        birth_year=data['birth_year'],
        mass=data['mass']
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.get_json()
    new_planet = Planetas(
        name=data['name'],
        climate=data['climate'],
        gravity=data['gravity'],
        diameter=data['diameter'],
        population=data['population'],
        orbital_period=data['orbital_period'],
        rotation_period=data['rotation_period'],
        terrain=data['terrain']
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

# Endpoint para traer todos los datos de la tabla User
@app.route('/users', methods=['GET'])
def get_users():

    # Creamos las variables para los usuarios de la tabla User
    users=User.query.all()
    all_users = [user.serialize() for user in users]

    # Retornamos todos los usuarios de la tabla User
    return jsonify(all_users), 200

# Endpoint para traer todos los datos de la tabla User
@app.route('/users/favorites', methods=['GET'])
def get_favoritos():

    # Creamos las variables para los personajes favoritos de los usuarios de la tabla Favoritos_Personajes
    f_personajes=Favoritos_Personajes.query.all()
    all_f_personajes = [fav.serialize() for fav in f_personajes]

    # Creamos las variables para los planetas favoritos de los usuarios de la tabla Favoritos_Planetas
    f_planetas=Favoritos_Planetas.query.all()
    all_f_planetas = [fav.serialize() for fav in f_planetas]

    # Retornamos tanto los personajes como los planetas favoritos de los usuarios
    return jsonify(all_f_planetas, all_f_personajes), 200



# Endpoint para añadir un planeta favorito a un usuario
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    # Recojemos el body
    data = request.get_json()

    # Recuperamos el planeta de la base de datos
    planet = Planetas.query.get(planet_id)
    
    # Verificamos si el planeta existe
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    # Indicamos la inserción que deseamos hacer en la base de datos
    favorite_planet = Favoritos_Planetas(user_id=data['user_id'], planetas_id=planet_id)

    # Realizamos la inserción
    db.session.add(favorite_planet)

    # Actualizamos la base de datos
    db.session.commit()

    # Retornamos los datos añadidos, incluyendo los detalles del planeta
    favorite_planet_serialize = favorite_planet.serialize()

    # Incluir detalles del planeta en la respuesta
    planet_details = planet.serialize()

    # Unir los datos del favorito con los detalles del planeta
    response = {
        "favorite_planet": favorite_planet_serialize,
        "planet_details": planet_details
    }

    return jsonify(response), 200


# Endpoint para añadir un perosnaje favorito a un usuario
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def post_favorite_people(people_id):

    # Recojemos el body
    data = request.get_json()

    # Indicamos la inserccion que deseamos hacer en la base de datos
    personaje = Favoritos_Personajes(user_id = data['user_id'], personajes_id = people_id)

    # Realizamos la insercion
    db.session.add(personaje)

    # Actualizamos la base de datos
    db.session.commit()

    # Retornamos los datos añadidos
    personaje_serialize = personaje.serialize()
    return jsonify(personaje_serialize), 200

# Endpoint para eliminar un planeta favorito de un usuario
@app.route('/favorite/planet/<int:favorito_id>', methods=['DELETE'])
def delete_favorite_planet(favorito_id):

    # Registramos el id del registro de la tabla Favoritos_Planetas a borrar
    planet = Favoritos_Planetas.query.get(favorito_id)

    # Borramos el registro
    db.session.delete(planet)

    # Actualizamos la base de datos
    db.session.commit()
    return jsonify("Done"), 200

# Endpoint para eliminar un personaje favorito de un usuario
@app.route('/favorite/people/<int:favorito_id>', methods=['DELETE'])
def delete_favorite_people(favorito_id):

    # Registramos el id del registro de la tabla Favoritos_Personajes a borrar
    personaje = Favoritos_Personajes.query.get(favorito_id)

    # Borramos el registro
    db.session.delete(personaje)

    # Actualizamos la base de datos
    db.session.commit()
    return jsonify("Done"), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)