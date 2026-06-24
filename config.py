import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'online-voting-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///voting.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
