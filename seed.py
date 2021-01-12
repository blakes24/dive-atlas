"""Seed file to make sample data for dive db."""

from config import config
from app import app
from models import db, connect_db, User, Dive_site, Bucket_list_site

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

app.config.from_object(config['development'])


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


connect_db(app)


# Drop then create all tables
db.drop_all()
db.create_all()

# Add user
diver1 = User.signup(username="diver1", email="diver1@test.com", password="testerpw")

diver1.confirmed = True

# Add new objects to session
db.session.add(diver1)

# Commit changes
db.session.commit()

lighthouse = Dive_site(
    name="The Blue Hole - Lighthouse Atoll",
    id=23265,
    lng=-87.555542,
    lat=17.245744,
    description="The Blue Hole is a giant marine sinkhole off the coast of Belize. This deep dive offers views of massive stalactites and divers often spot  nurse sharks, reef sharks, black tip sharks, and giant groupers.",
    location="Lighthouse Atoll, Belize",
)

db.session.add(lighthouse)

db.session.commit()

bl_site = Bucket_list_site(dive_site_id=lighthouse.id, user_id=diver1.id)

db.session.add(bl_site)
db.session.commit()
