from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from app.forms import TweetAnalysisForm
from app.models.tweet_analysis import TweetAnalysis
from datetime import datetime

analyse_bp = Blueprint('analyse', __name__)

# Initialize model and tokenizer separately to avoid loading issues
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Initialize the pipeline with pre-loaded model and tokenizer
pipe = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=True,
    device=-1  # Use CPU, change to 0 if you want to use GPU
)

def analyze_sentiment(text):
    try:
        results = pipe(text)[0]
        sentiment_scores = {
            score['label'].lower(): score['score'] 
            for score in results
        }
        sentiment = max(sentiment_scores, key=sentiment_scores.get)
        confidence = sentiment_scores[sentiment]
        return sentiment, confidence
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutral", 0.5

@analyse_bp.route('/analyse', methods=['GET', 'POST'])
@login_required
def analyse():
    form = TweetAnalysisForm()
    
    try:
        recent_analyses = TweetAnalysis.get_recent_by_user(current_user.id)
    except Exception as e:
        print(f"Error fetching recent analyses: {str(e)}")
        recent_analyses = []

    if form.validate_on_submit():
        tweet_text = form.tweet_text.data
        sentiment, confidence = analyze_sentiment(tweet_text)
        
        try:
            # Create analysis with proper data structure
            analysis_data = {
                "user_id": int(current_user.id),  # Convert to int
                "tweet_text": tweet_text,
                "sentiment": sentiment,
                "confidence": float(confidence),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Create the analysis in Supabase
            analysis = TweetAnalysis.create(**analysis_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'sentiment': sentiment,
                    'confidence': round(float(confidence) * 100, 2),
                    'id': analysis.get('id') if analysis else None
                })
            
            # Refresh recent analyses
            recent_analyses = TweetAnalysis.get_recent_by_user(current_user.id)
            
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to save analysis'}), 500
    
    return render_template('analyse/analyse.html', form=form, recent_analyses=recent_analyses) 