from __init__ import app, db
import logging
from sqlalchemy.exc import IntegrityError


class Length(db.Model):
    __tablename__ = 'lengths'


    # Columns
    id = db.Column(db.Integer, primary_key=True)
    video_length = db.Column(db.Float, nullable=False)  # in seconds or minutes
    engagement = db.Column(db.Integer, nullable=False)  # likes + comments + shares, etc.


    # Constructor
    def __init__(self, video_length, engagement):
        self.video_length = video_length
        self.engagement = engagement


    # Create method
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating length entry: {e}")
            raise e


    # Delete method
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting length entry: {e}")
            raise e


    # Serialize method for JSON output
    def serialize(self):
        return {
            'id': self.id,
            'video_length': self.video_length,
            'engagement': self.engagement
        }


    def read(self):
        return self.serialize()


    # Optional update method
    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self


        video_length = inputs.get("video_length", None)
        engagement = inputs.get("engagement", None)


        if video_length is not None:
            self.video_length = float(video_length)
        if engagement is not None:
            self.engagement = int(engagement)


        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self


    # Optional restore method for seeding data
    @staticmethod
    def restore(data):
        entries = {}
        for entry_data in data:
            _ = entry_data.pop('id', None)
            video_length = entry_data.get("video_length", None)
            engagement = entry_data.get("engagement", None)
            existing = Length.query.filter_by(video_length=video_length, engagement=engagement).first()
            if existing:
                existing.update(entry_data)
            else:
                new_entry = Length(**entry_data)
                new_entry.create()
        return entries


# Function to initialize and optionally seed with test data
def initLength():
    try:
        db.create_all()


        if not Length.query.first():
            test_data = [
                Length(video_length=15.0, engagement=5000),
                Length(video_length=30.0, engagement=7500),
                Length(video_length=45.0, engagement=6200)
            ]
            for entry in test_data:
                entry.create()


        logging.info("Length table initialized and seeded successfully.")
    except Exception as e:
        logging.error(f"Error initializing Length table: {e}")
        raise e



