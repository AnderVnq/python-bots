# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from contextlib import contextmanager
# #from models.database_bots import RankingProduct

# DATABASE_URL="mysql+pymysql://root:heaveny2@localhost/record_products_cf"



# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
# Base.metadata.create_all(engine)
# @contextmanager
# def get_db_session():
#     session = SessionLocal()
#     try:
#         yield session
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         print(f"Error en la base de datos: {e}")
#         raise
#     finally:
#         session.close()