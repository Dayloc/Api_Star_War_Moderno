from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    favoritos: Mapped[list["Favorito"]] = relationship("Favorito", back_populates="usuario", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favoritos": [fav.serialize() for fav in self.favoritos]
        }


class Personaje(db.Model):
    __tablename__ = "personaje"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    genero: Mapped[str] = mapped_column(String(120), nullable=False)
    nacimiento: Mapped[str] = mapped_column(String(120), nullable=False)

    favoritos: Mapped[list["Favorito"]] = relationship("Favorito", back_populates="personaje", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "genero": self.genero,
            "nacimiento": self.nacimiento
        }


class Planeta(db.Model):
    __tablename__ = "planeta"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    clima: Mapped[str] = mapped_column(String(120), nullable=False)
    terreno: Mapped[str] = mapped_column(String(120), nullable=False)

    favoritos: Mapped[list["Favorito"]] = relationship("Favorito", back_populates="planeta", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "clima": self.clima,
            "terreno": self.terreno
        }


class Favorito(db.Model):
    __tablename__ = "favorito"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    personaje_id: Mapped[int | None] = mapped_column(ForeignKey("personaje.id"), nullable=True)
    planeta_id: Mapped[int | None] = mapped_column(ForeignKey("planeta.id"), nullable=True)

    usuario: Mapped["User"] = relationship("User", back_populates="favoritos")
    personaje: Mapped["Personaje"] = relationship("Personaje", back_populates="favoritos")
    planeta: Mapped["Planeta"] = relationship("Planeta", back_populates="favoritos")

    def serialize(self):
        data = {"id": self.id}
        if self.personaje:
            data["type"] = "personaje"
            data["nombre"] = self.personaje.nombre
        elif self.planeta:
            data["type"] = "planeta"
            data["nombre"] = self.planeta.nombre
        return data
