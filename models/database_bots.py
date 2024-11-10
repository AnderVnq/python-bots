# from sqlalchemy import Column, Integer, String ,DateTime
# from _config.db_config import Base,engine
# import uuid
# from datetime import datetime
# from _config.db_config import get_db_session

# class RankingProduct(Base):
#     """
#     Clase que representa la tabla ranking_products en la base de datos
#     """

#     __tablename__ = "ranking_products"

#     id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
#     product_name=Column(String(100))
#     shop_name=Column(String(100))
#     position=Column(String(10))
#     page=Column(Integer)
#     created_at=Column(DateTime,default=datetime.now,nullable=False)
#     updated_at=Column(DateTime,default=datetime.now,nullable=False,onupdate=datetime.now)
#     last_position=Column(String(10))
#     last_page=Column(Integer)
#     keyword=Column(String(100),unique=True)


#     def __repr__(self):
#         return f"RankingProduct(id={self.id},product_name={self.product_name},shop_name={self.shop_name},position={self.position},page={self.page},created_at={self.created_at},updated_at={self.updated_at},last_position={self.last_position},last_page={self.last_page})"
    

#     def __str__(self):
#         return f"RankingProduct(id={self.id},product_name={self.product_name},shop_name={self.shop_name},position={self.position},page={self.page},created_at={self.created_at},updated_at={self.updated_at},last_position={self.last_position},last_page={self.last_page})"
    

#     @classmethod
#     def get_ranking(cls):
#         with get_db_session() as session:
#             return session.query(cls).all()
    
#     @classmethod
#     def get_ranking_by_id(cls, id):
#         with get_db_session() as session:
#             return session.query(cls).filter(cls.id == id).first()
    
#     @classmethod
#     def get_ranking_by_product_name(cls, product_name):
#         with get_db_session() as session:
#             return session.query(cls).filter(cls.product_name == product_name).all()
    
#     @classmethod
#     def get_ranking_by_shop_name(cls, shop_name):
#         with get_db_session() as session:
#             return session.query(cls).filter(cls.shop_name == shop_name).all()
    
#     @classmethod
#     def get_ranking_by_keyword(cls, keyword):
#         with get_db_session() as session:
#             return session.query(cls).filter(cls.keyword == keyword).all()

#     def crear_ranking(self):
#         with get_db_session() as session:
#             session.add(self)
#             return self 
    
#     @classmethod
#     def update_ranking_by_id(cls, session, id, **kwargs):
#         with get_db_session() as session:
#             # Buscar el registro en la base de datos
#             existing_ranking = session.query(cls).filter(cls.id == id).first()
            
#             if existing_ranking:
#                 # Actualizar los atributos del objeto existente con los valores de kwargs
#                 for key, value in kwargs.items():
#                     if hasattr(existing_ranking, key):
#                         setattr(existing_ranking, key, value)
                
#                 return existing_ranking
#             else:
#                 return None 
            
# Base.metadata.create_all(engine)