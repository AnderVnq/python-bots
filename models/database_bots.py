from sqlalchemy import Column, Integer, String ,DateTime
import uuid
from datetime import datetime
from sqlalchemy.orm import declarative_base
from _config.db_config import get_db_session,engine
from sqlalchemy import DECIMAL


# Definir la base para los modelos
Base = declarative_base()

class RankingProduct(Base):
    """
    Clase que representa la tabla ranking_products en la base de datos
    """
    __tablename__ = "ranking_products"

    id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    product_name=Column(String(100))
    shop_name=Column(String(100))
    position=Column(String(10))
    last_position = Column(String(10))
    last_page = Column(Integer)
    page=Column(Integer)
    created_at=Column(DateTime,default=datetime.now,nullable=False)
    updated_at=Column(DateTime,default=datetime.now,nullable=False,onupdate=datetime.now)
    sku_cf=Column(String(100),unique=True)
    precio_normal=Column(DECIMAL(10, 2))


    def __repr__(self):
        return f"RankingProduct(id={self.id},product_name={self.product_name},shop_name={self.shop_name},position={self.position},page={self.page},created_at={self.created_at},updated_at={self.updated_at}"
    

    def __str__(self):
        return f"RankingProduct(id={self.id},product_name={self.product_name},shop_name={self.shop_name},position={self.position},page={self.page},created_at={self.created_at},updated_at={self.updated_at}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "shop_name": self.shop_name,
            "position": self.position,
            "last_position": self.last_position,
            "last_page": self.last_page,
            "page": self.page,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "sku_cf": self.sku_cf,
            "precio_normal": float(self.precio_normal) if self.precio_normal else None,
        }
    @classmethod
    def get_ranking(cls):
        with get_db_session() as session:
            return [product.to_dict() for product in session.query(cls).all()]
    
    @classmethod
    def get_ranking_by_id(cls, id):
        with get_db_session() as session:
            ranking=session.query(cls).filter(cls.id == id).first()
            return ranking.to_dict()
    
    @classmethod
    def get_ranking_by_product_name(cls, product_name):
        with get_db_session() as session:
            rankings= session.query(cls).filter(cls.product_name == product_name).all()
            return [ranking.to_dict() for ranking in rankings]
    
    @classmethod
    def get_ranking_by_shop_name(cls, shop_name):
        with get_db_session() as session:
            rankings= session.query(cls).filter(cls.shop_name == shop_name).all()
            return [ranking.to_dict() for ranking in rankings]
    
    @classmethod
    def get_ranking_by_sku(cls, sku_cf):
        with get_db_session() as session:
            ranking=session.query(cls).filter(cls.sku_cf == sku_cf).first()
            return ranking.to_dict() if ranking else None

    def crear_ranking(self):
            try:
                with get_db_session() as session:
                    # Verificar si el producto con el mismo sku_cf ya existe
                    existing_ranking:RankingProduct = session.query(RankingProduct).filter(RankingProduct.sku_cf == self.sku_cf).first()
                    
                    if existing_ranking:
                        # Si el producto ya existe, actualizamos los campos que cambian
                        existing_ranking.last_position = existing_ranking.position 
                        existing_ranking.last_page = existing_ranking.page  

                        existing_ranking.product_name = self.product_name
                        existing_ranking.shop_name = self.shop_name
                        existing_ranking.position = self.position
                        existing_ranking.page = self.page
                        # Confirmar los cambios en la base de datos
                        session.commit()

                        # Validación: comprobar si se actualizó correctamente
                        updated_ranking = session.query(RankingProduct).filter(RankingProduct.id == existing_ranking.id).first()
                        if updated_ranking:
                            print(f"Producto actualizado correctamente: {updated_ranking}")
                            return updated_ranking  # Devolver el objeto actualizado
                        else:
                            print("Error: El producto no se actualizó correctamente.")
                            return None

                    else:
                        # Si el producto no existe, lo añadimos como nuevo
                        session.add(self)  # Añadir el objeto a la sesión
                        session.commit()  # Confirmar los cambios en la base de datos
                        
                        # Validación: comprobar si el objeto fue guardado correctamente
                        saved_ranking = session.query(RankingProduct).filter(RankingProduct.id == self.id).first()
                        if saved_ranking:
                            print(f"Producto guardado correctamente: {saved_ranking}")
                            return saved_ranking  # Devolver el objeto guardado
                        else:
                            print("Error: El producto no se guardó correctamente.")
                            return None

            except Exception as e:
                session.rollback()  # Si ocurre un error, revertir los cambios
                print(f"Error al guardar o actualizar el producto en la base de datos: {e}")
                return None

    @classmethod
    def update_ranking_by_id(cls, id, **kwargs):
        try:
            with get_db_session() as session:
                # Buscar el registro en la base de datos
                existing_ranking = session.query(cls).filter(cls.id == id).first()

                if existing_ranking:
                    # Actualizar los atributos del objeto existente con los valores de kwargs
                    for key, value in kwargs.items():
                        if hasattr(existing_ranking, key):
                            setattr(existing_ranking, key, value)

                    session.commit()  # Confirmar los cambios en la base de datos
                    
                    # Validación: comprobar si el objeto fue actualizado correctamente
                    updated_ranking = session.query(cls).filter(cls.id == id).first()
                    if updated_ranking:
                        print(f"Ranking actualizado correctamente: {updated_ranking}")
                        return updated_ranking  # Devolver el objeto actualizado
                    else:
                        print(f"Error: El ranking con id {id} no fue encontrado después de la actualización.")
                        return None
                else:
                    print(f"Ranking con id {id} no encontrado.")
                    return None

        except Exception as e:
            session.rollback()  # Si ocurre un error, revertir los cambios
            print(f"Error al actualizar el ranking en la base de datos: {e}")
            return None
            
#Base.metadata.create_all(engine)