from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conftest import SQLITE_URL
from models import Driver, Customer, Destination, Package
from faker import Faker
import random
import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


class TestDriver:
    """Driver in models.py"""

    def test_has_attributes(self):
        """has attributes id, name, current_location."""

        engine = create_engine(SQLITE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        fake = Faker("en_US")
        driver = Driver(
            name=fake.unique.name(),
            start_location=Point(random.randint(1, 31), random.randint(1, 31)),
        )
        session.add(driver)
        session.commit()

        assert hasattr(driver, "id")
        assert hasattr(driver, "name")
        assert hasattr(driver, "start_location")

        session.query(Driver).delete()
        session.commit()

    # def test_has_many_reviews(self):
    #     """has an attribute "reviews" that is a sequence of Review records."""

    #     engine = create_engine(SQLITE_URL)
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     review_1 = Review(score=8, comment="Good game!")
    #     review_2 = Review(score=6, comment="OK game.")
    #     session.add_all([review_1, review_2])
    #     session.commit()

    #     game = Game(title="Metric Prime Reverb")
    #     game.reviews.append(review_1)
    #     game.reviews.append(review_2)
    #     session.add(game)
    #     session.commit()

    #     assert game.reviews
    #     assert review_1 in game.reviews
    #     assert review_2 in game.reviews

    #     session.query(Review).delete()
    #     session.query(Game).delete()
    #     session.commit()

    # def test_has_many_users(self):
    #     """has an attribute "users" that is a sequence of User records."""

    #     engine = create_engine(SQLITE_URL)
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     user_1 = User(name="Ben")
    #     user_2 = User(name="Prabhdip")
    #     session.add_all([user_1, user_2])
    #     session.commit()

    #     game = Game(title="Super Marvin 128")
    #     game.users.append(user_1)
    #     game.users.append(user_2)
    #     session.add(game)
    #     session.commit()

    #     assert game.users
    #     assert user_1 in game.users
    #     assert user_2 in game.users

    #     session.query(User).delete()
    #     session.query(Game).delete()
    #     session.commit()
