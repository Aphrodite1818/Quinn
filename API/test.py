#----------------------------#
#   RENDER  DATABASE SETUP 
#----------------------------#


from sqlalchemy import create_engine #this connects your python app to the database
from sqlalchemy.ext.declarative import declarative_base #this creates the base class for the models basically tables
from sqlalchemy.orm import sessionmaker #actually allows us talk to the database
from dotenv import load_dotenv
import os


load_dotenv()

RENDER_DATABASE_URL = os.getenv("RENDER_DATABASE_URL")
engine = create_engine(RENDER_DATABASE_URL)

RenderSession = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
#sessionmaker always returns a class making RenderSession a class
Base = declarative_base()


print(type(RenderSession))




