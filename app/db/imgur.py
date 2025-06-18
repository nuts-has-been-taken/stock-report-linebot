from app.core.config import postgress_db
from app.model.postgresql import ImgurToken

import datetime

Session = postgress_db.SESSION

def get_token():
    session = Session()
    try:
        result = session.query(ImgurToken).order_by(ImgurToken.date.desc()).first()
        if result:
            return result
        else:
            return None
    finally:
        session.close()

def save_token(refresh_token, access_token, date=None):
    session = Session()
    try:
        if date is None:
            date = datetime.datetime.now(datetime.timezone.utc)
        
        new_token = ImgurToken(
            refresh_token=refresh_token,
            access_token=access_token,
            date=date
        )
        
        session.add(new_token)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()