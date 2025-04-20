import os
import google.generativeai as genai
from config import GOOGLE_API_KEY
import json
import logging
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
def init_gemini():
    try:
        if not GOOGLE_API_KEY:
            print("No API key found")
            raise ValueError("Gemini API key not found in environment variables")
            
        # Configure the API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # List available models to debug
        try:
            models = genai.list_models()
            print("Available models:", [model.name for model in models])
        except Exception as e:
            print(f"Error listing models: {str(e)}")
        
        # Initialize the model with an available model version
        try:
            model = genai.GenerativeModel(model_name='models/gemini-2.0-flash-thinking-exp-01-21')
            
            # Test the model with a simple prompt
            response = model.generate_content("Test message")
            print("Test response successful")
            return model
            
        except Exception as e:
            print(f"Error initializing model: {str(e)}")
            raise e
            
    except Exception as e:
        print(f"Error in init_gemini: {str(e)}")
        return None

def get_system_prompt():
    return """As Takar, your role is to:
1. Explain sentiment analysis results clearly and professionally
2. Focus on the specific words and patterns that influence sentiment scores
3. Provide constructive insights about social media communication
4. Help users understand the nuances of sentiment analysis

When responding:
- Be concise but thorough
- Use professional but accessible language
- Stay focused on sentiment analysis
- Provide specific examples when relevant"""

def get_chat_response(model, message, analyses):
    try:
        if not model:
            return "I apologize, but I'm currently unable to process requests. Please try again later."
            
        # Prepare context about the analyses
        context = prepare_analysis_context(analyses)
        
        # Create the prompt with context and system prompt
        prompt = f"""You are Takar, an AI assistant specializing in sentiment analysis.
        
        {get_system_prompt()}
        
        Here is the context about the user's sentiment analyses:
        {context}
        
        User message: {message}
        
        Please provide a helpful response based on the sentiment analysis data."""
        
        # Generate response with error handling
        try:
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                return response.text
            else:
                print("Invalid response format:", response)
                return "I apologize, but I couldn't generate a proper response."
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return "I apologize, but I encountered an error generating the response."
            
    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return "I apologize, but I encountered an error. Please try again."

def analyze_sentiment_details(model, analysis):
    try:
        if not model:
            return "I apologize, but I'm currently unable to analyze tweets. Please try again later."
            
        # Extract confidence from the analysis data
        confidence = float(analysis.get('confidence', 0)) * 100
        sentiment = analysis.get('sentiment', 'neutral')
        tweet_text = analysis.get('tweet_text', '')
        
        # Create a simpler prompt that doesn't rely too heavily on the model
        prompt = f"""Tweet: "{tweet_text}"
        Sentiment: {sentiment}
        Confidence: {confidence:.2f}%

        Please explain why this tweet was classified as {sentiment}. Focus on:
        1. Key words and phrases
        2. Overall tone
        3. Context clues"""
        
        # Generate response with error handling
        try:
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                return response.text
            else:
                print("Invalid response format:", response)
                return "Unable to analyze this tweet at the moment."
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return "Unable to analyze this tweet at the moment."
            
    except Exception as e:
        print(f"Error in analyze_sentiment_details: {str(e)}")
        return "Unable to analyze this tweet at the moment."

def prepare_analysis_context(analyses):
    if not analyses:
        return "No sentiment analyses available."
    
    try:
        total = len(analyses)
        sentiment_counts = {
            'positive': sum(1 for a in analyses if a.get('sentiment') == 'positive'),
            'negative': sum(1 for a in analyses if a.get('sentiment') == 'negative'),
            'neutral': sum(1 for a in analyses if a.get('sentiment') == 'neutral')
        }
        
        context = f"""Total analyses: {total}
        Positive tweets: {sentiment_counts['positive']} ({sentiment_counts['positive']/total*100:.1f}%)
        Negative tweets: {sentiment_counts['negative']} ({sentiment_counts['negative']/total*100:.1f}%)
        Neutral tweets: {sentiment_counts['neutral']} ({sentiment_counts['neutral']/total*100:.1f}%)
        
        Recent tweets:"""
        
        # Add 3 most recent tweets as examples
        recent = sorted(analyses, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        for tweet in recent:
            confidence = float(tweet.get('confidence', 0)) * 100
            context += f"\n- {tweet.get('tweet_text')} (Sentiment: {tweet.get('sentiment')}, Confidence: {confidence:.1f}%)"
        
        return context
        
    except Exception as e:
        print(f"Error in prepare_analysis_context: {str(e)}")
        return "Error preparing analysis context."

class Chatbot:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            genai.configure(api_key=self.api_key)
            
            # Configure the model
            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name="models/gemini-2.0-flash-thinking-exp-01-21",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Test the model
            self._test_model()
            
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {str(e)}")
            raise
    
    def _test_model(self):
        """Test the model with a simple prompt to ensure it's working"""
        try:
            response = self.model.generate_content("Hello")
            if not response or not response.text:
                raise ValueError("Model test failed: Empty response")
            logger.info("Model test successful")
        except Exception as e:
            logger.error(f"Model test failed: {str(e)}")
            raise
    
    def get_response(self, message):
        """Get a response from the chatbot"""
        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Generate response
            response = chat.send_message(message)
            
            if not response or not response.text:
                raise ValueError("Empty response from model")
            
            return jsonify({
                "response": response.text,
                "error": None
            })
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            return jsonify({
                "response": error_message,
                "error": str(e)
            }) 