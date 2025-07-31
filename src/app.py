"""
API Server con rutas para usuarios, personajes, planetas y favoritos.
"""
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Personaje, Planeta, Favorito

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
       
# Inicialización de extensiones
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Manejo de errores personalizado
@app.errorhandler(APIException)
def handle_api_exception(error):
    return jsonify(error.to_dict()), error.status_code

# Ruta para sitemap automático
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ----------- USUARIOS -----------

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException("Usuario no encontrado", status_code=404)

    favoritos = Favorito.query.filter_by(usuario_id=user_id).all()
    resultado = []
    for fav in favoritos:
        item = {"id": fav.id}
        if fav.personaje:
            item["type"] = "personaje"
            item["data"] = {
                "id": fav.personaje.id,
                "nombre": fav.personaje.nombre,
                "descripcion": fav.personaje.descripcion
            }
        elif fav.planeta:
            item["type"] = "planeta"
            item["data"] = {
                "id": fav.planeta.id,
                "nombre": fav.planeta.nombre,
                "descripcion": fav.planeta.descripcion
            }
        resultado.append(item)

    return jsonify(resultado), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        raise APIException("Email y contraseña son obligatorios", status_code=400)

    if User.query.filter_by(email=data["email"]).first():
        raise APIException("Ya existe un usuario con ese email", status_code=409)

    new_user = User(
        email=data["email"],
        password=data["password"],
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado exitosamente", "user": new_user.serialize()}), 201

# ----------- PERSONAJES -----------

@app.route('/people', methods=['GET'])
def get_people():
    people = Personaje.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route('/people/<int:person_id>', methods=['GET'])
def get_single_person(person_id):
    person = Personaje.query.get(person_id)
    if not person:
        raise APIException("Personaje no encontrado", status_code=404)
    return jsonify(person.serialize()), 200

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    new_person = Personaje(
        nombre=data.get('nombre'),
        genero=data.get('genero'),
        nacimiento=data.get('nacimiento')
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201     

@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    data = request.get_json()
    person = Personaje.query.get(person_id)
    if not person:
        raise APIException('Personaje no encontrado', status_code=404)

    person.nombre = data.get('nombre', person.nombre)
    person.genero = data.get('genero', person.genero)
    person.nacimiento = data.get('nacimiento', person.nacimiento)
    db.session.commit()
    return jsonify(person.serialize()), 200

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    person = Personaje.query.get(person_id)
    if not person:
        raise APIException('Personaje no encontrado', status_code=404)

    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Personaje eliminado"}), 200

# ----------- PLANETAS -----------

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planeta.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planeta.query.get(planet_id)
    if not planet:
        raise APIException("Planeta no encontrado", status_code=404)
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    new_planet = Planeta(
        nombre=data.get('nombre'),
        clima=data.get('clima'),
        terreno=data.get('terreno')
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = Planeta.query.get(planet_id)
    if not planet:
        raise APIException('Planeta no encontrado', status_code=404)

    planet.nombre = data.get('nombre', planet.nombre)
    planet.clima = data.get('clima', planet.clima)
    planet.terreno = data.get('terreno', planet.terreno)
    db.session.commit()
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planeta.query.get(planet_id)
    if not planet:
        raise APIException('Planeta no encontrado', status_code=404)

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planeta eliminado"}), 200



# ----------- FAVORITOS -----------

@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['POST'])
def add_fav_planet(user_id, planet_id):
    planet = Planeta.query.get(planet_id)
    if not planet:
        raise APIException("Planeta no encontrado", 404)

    existing = Favorito.query.filter_by(usuario_id=user_id, planeta_id=planet_id).first()
    if existing:
        return jsonify({"message": "Planeta ya está en favoritos"}), 200

    favorito = Favorito(usuario_id=user_id, planeta_id=planet_id)
    db.session.add(favorito)
    db.session.commit()
    return jsonify(favorito.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_person(people_id):
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        raise APIException("User ID requerido como query param (?user_id=)", 400)

    person = Personaje.query.get(people_id)
    if not person:
        raise APIException("Personaje no encontrado", 404)

    existing = Favorito.query.filter_by(usuario_id=user_id, personaje_id=people_id).first()
    if existing:
        return jsonify({"message": "Personaje ya está en favoritos"}), 200

    favorito = Favorito(usuario_id=user_id, personaje_id=people_id)
    db.session.add(favorito)
    db.session.commit()
    return jsonify(favorito.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(planet_id):
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        raise APIException("User ID requerido como query param (?user_id=)", 400)

    favorito = Favorito.query.filter_by(usuario_id=user_id, planeta_id=planet_id).first()
    if not favorito:
        raise APIException("Favorito no encontrado", 404)

    db.session.delete(favorito)
    db.session.commit()
    return jsonify({"message": "Favorito eliminado"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_person(people_id):
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        raise APIException("User ID requerido como query param (?user_id=)", 400)

    favorito = Favorito.query.filter_by(usuario_id=user_id, personaje_id=people_id).first()
    if not favorito:
        raise APIException("Favorito no encontrado", 404)

    db.session.delete(favorito)
    db.session.commit()
    return jsonify({"message": "Favorito eliminado"}), 200

# ----------- MAIN -----------

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
