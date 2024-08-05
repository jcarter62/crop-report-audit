from app import db

class CropReport2010Data(db.Model):
    __tablename__ = 'CropReport2010Data'
    CropYear = db.Column(db.String, primary_key=True)
    # Add other columns here as needed

class CropCodes(db.Model):
    __tablename__ = 'CropCodes'
    CropCode = db.Column(db.String, primary_key=True)
    # Add other columns here as needed

class Fields(db.Model):
    __tablename__ = 'Fields'
    Field_ID = db.Column(db.String, primary_key=True)
    # Add other columns here as needed

class Name(db.Model):
    __tablename__ = 'Name'
    NAME_ID = db.Column(db.String, primary_key=True)
    # Add other columns here as needed

