from app.database import supabase
from datetime import datetime

class BaseModel:
    @classmethod
    def create(cls, **kwargs):
        data = supabase.table(cls.__tablename__).insert(kwargs).execute()
        return data.data[0]

    @classmethod
    def get_by_id(cls, id):
        data = supabase.table(cls.__tablename__).select("*").eq("id", id).execute()
        return data.data[0] if data.data else None

    @classmethod
    def update(cls, id, **kwargs):
        data = supabase.table(cls.__tablename__).update(kwargs).eq("id", id).execute()
        return data.data[0]

    @classmethod
    def delete(cls, id):
        supabase.table(cls.__tablename__).delete().eq("id", id).execute() 