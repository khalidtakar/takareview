from app.models.base import BaseModel
from datetime import datetime
from app.database import supabase

class TweetAnalysis(BaseModel):
    __tablename__ = 'tweet_analysis'

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.tweet_text = kwargs.get('tweet_text')
        self.sentiment = kwargs.get('sentiment')
        self.confidence = kwargs.get('confidence')
        # Parse the datetime string from Supabase
        created_at = kwargs.get('created_at')
        if isinstance(created_at, str):
            try:
                # Remove timezone info if present and parse
                created_at = created_at.replace('Z', '').split('+')[0]
                self.created_at = datetime.fromisoformat(created_at)
            except (ValueError, TypeError):
                self.created_at = datetime.utcnow()
        else:
            self.created_at = created_at or datetime.utcnow()

    @classmethod
    def get_recent_by_user(cls, user_id, limit=6):
        try:
            response = supabase.table(cls.__tablename__)\
                .select("*")\
                .eq("user_id", int(user_id))\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            analyses = []
            for item in response.data:
                analysis = cls(**item)
                if isinstance(analysis.confidence, str):
                    analysis.confidence = float(analysis.confidence)
                analyses.append(analysis)
            
            return analyses
        except Exception as e:
            print(f"Error in get_recent_by_user: {str(e)}")
            return []

    @classmethod
    def create_analysis(cls, user_id, tweet_text, sentiment, confidence):
        try:
            analysis_data = {
                'user_id': int(user_id),
                'tweet_text': tweet_text,
                'sentiment': sentiment,
                'confidence': float(confidence),
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = supabase.table(cls.__tablename__)\
                .insert(analysis_data)\
                .execute()
            
            if response.data:
                return cls(**response.data[0])
            return None
        except Exception as e:
            print(f"Error creating analysis: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full stack trace
            raise

    def __repr__(self):
        return f'<TweetAnalysis {self.tweet_text[:30]}...>'

    # Add properties to ensure consistent data access
    @property
    def confidence_percentage(self):
        try:
            return round(float(self.confidence) * 100, 2)
        except (TypeError, ValueError):
            return 0

    @property
    def formatted_date(self):
        """Return a formatted date string"""
        try:
            return self.created_at.strftime('%Y-%m-%d %H:%M')
        except (AttributeError, ValueError):
            return "N/A"

    @classmethod
    def get_all_by_user(cls, user_id):
        try:
            response = supabase.table(cls.__tablename__) \
                .select("*") \
                .eq("user_id", user_id) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting analyses for user {user_id}: {str(e)}")
            return [] 