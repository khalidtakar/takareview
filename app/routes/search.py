from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from transformers import pipeline
import torch
from app.forms import TweetAnalysisForm
from app.models.tweet_analysis import TweetAnalysis

search_bp = Blueprint('search', __name__)

# Initialize the sentiment analysis pipeline
pipe = pipeline("text-classification", 
               model="cardiffnlp/twitter-roberta-base-sentiment-latest",
               return_all_scores=True)

def analyze_sentiment(text):
    # Get sentiment analysis results
    results = pipe(text)[0]
    
    # Convert label scores to our format
    sentiment_scores = {
        score['label'].lower(): score['score'] 
        for score in results
    }
    
    sentiment = max(sentiment_scores, key=sentiment_scores.get)
    confidence = sentiment_scores[sentiment]
    
    return sentiment, confidence

@search_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = TweetAnalysisForm()
    recent_analyses = TweetAnalysis.get_recent_by_user(current_user.id)
    
    if form.validate_on_submit():
        tweet_text = form.tweet_text.data
        sentiment, confidence = analyze_sentiment(tweet_text)
        
        try:
            analysis = TweetAnalysis.create_analysis(
                user_id=current_user.id,
                tweet_text=tweet_text,
                sentiment=sentiment,
                confidence=confidence
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'sentiment': sentiment,
                    'confidence': round(confidence * 100, 2),
                    'id': analysis.id if analysis else None
                })
            
            # Refresh the recent analyses after adding new one
            recent_analyses = TweetAnalysis.get_recent_by_user(current_user.id)
            
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to save analysis'}), 500
    
    return render_template('search/search.html', form=form, recent_analyses=recent_analyses) 