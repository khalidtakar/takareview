from flask import Blueprint, render_template, jsonify, request, send_file, current_app, url_for
from flask_login import login_required, current_user
from app.models.tweet_analysis import TweetAnalysis
from datetime import datetime, timedelta
import json
from dateutil import parser
from collections import Counter
import re
import pandas as pd
from io import BytesIO, StringIO
import html
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Circle, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from app.chatbot import init_gemini, get_chat_response, analyze_sentiment_details
from werkzeug.utils import secure_filename
import os
from supabase import create_client, Client
import traceback
import time

main_bp = Blueprint('main', __name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Initialize Gemini model at module level
gemini_model = None

def initialize_gemini():
    global gemini_model
    print("Initializing Gemini model...")
    gemini_model = init_gemini()
    if gemini_model:
        print("Gemini model initialized successfully")
    else:
        print("Failed to initialize Gemini model")

# Initialize on module load
initialize_gemini()

UPLOAD_FOLDER = 'app/static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main_bp.route('/')
def index():
    return render_template('index.html')

def format_timestamp(timestamp_str):
    """Format timestamp to remove milliseconds and timezone"""
    try:
        dt = parser.parse(timestamp_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return timestamp_str

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get all analyses for the current user
        all_analyses = TweetAnalysis.get_all_by_user(current_user.id)
        print(f"Retrieved {len(all_analyses)} analyses")
        
        # Format timestamps in recent responses
        for analysis in all_analyses:
            if 'created_at' in analysis:
                analysis['created_at'] = format_timestamp(analysis['created_at'])
        
        # Calculate sentiment percentages
        total = len(all_analyses)
        if total > 0:
            sentiment_counts = {
                'positive': sum(1 for a in all_analyses if a.get('sentiment') == 'positive'),
                'negative': sum(1 for a in all_analyses if a.get('sentiment') == 'negative'),
                'neutral': sum(1 for a in all_analyses if a.get('sentiment') == 'neutral')
            }
            
            sentiment_percentages = {
                key: round((count / total) * 100, 1)
                for key, count in sentiment_counts.items()
            }
            
            # Simplified radar metrics with just sentiment percentages
            radar_metrics = {
                'positive': sentiment_percentages['positive'],
                'negative': sentiment_percentages['negative'],
                'neutral': sentiment_percentages['neutral']
            }
            
            # Get recent responses (last 3)
            recent_responses = sorted(
                all_analyses, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )[:3]
            
            # Calculate trend data for different time ranges
            trend_data = {
                'daily': calculate_trend_data(all_analyses, 'daily'),
                'weekly': calculate_trend_data(all_analyses, 'weekly'),
                'monthly': calculate_trend_data(all_analyses, 'monthly')
            }
            
        else:
            sentiment_percentages = {'positive': 0, 'negative': 0, 'neutral': 0}
            radar_metrics = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            recent_responses = []
            trend_data = {
                'daily': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []},
                'weekly': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []},
                'monthly': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []}
            }
        
        return render_template(
            'main/dashboard.html',
            sentiment_percentages=sentiment_percentages,
            recent_responses=recent_responses,
            trend_data=json.dumps(trend_data),
            radar_metrics=json.dumps(radar_metrics)
        )
        
    except Exception as e:
        print(f"Error fetching dashboard data: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template(
            'main/dashboard.html',
            error="Failed to load dashboard data"
        )

def get_word_frequencies(analyses, sentiment_type):
    """Get word frequencies for a specific sentiment type"""
    words = []
    for analysis in analyses:
        if analysis.get('sentiment') == sentiment_type:
            # Get the tweet text and clean it
            text = analysis.get('tweet_text', '').lower()
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text)
            # Remove mentions and hashtags
            text = re.sub(r'@\w+|\#\w+', '', text)
            # Remove special characters and split
            words.extend(re.findall(r'\b\w+\b', text))
    
    # Remove common stop words
    stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 
                 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
                 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 
                 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
                 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
                 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
                 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
                 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
                 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
                 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
                 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
                 'give', 'day', 'most', 'us'}
    
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Get word frequencies
    word_freq = Counter(words).most_common(20)
    return {word: count for word, count in word_freq}

@main_bp.route('/details')
@login_required
def sentiment_details():
    try:
        # Get all analyses for the current user
        all_analyses = TweetAnalysis.get_all_by_user(current_user.id)
        print(f"Details page - Retrieved {len(all_analyses)} analyses")
        
        # Calculate sentiment percentages
        total = len(all_analyses)
        if total > 0:
            sentiment_counts = {
                'positive': sum(1 for a in all_analyses if a.get('sentiment') == 'positive'),
                'negative': sum(1 for a in all_analyses if a.get('sentiment') == 'negative'),
                'neutral': sum(1 for a in all_analyses if a.get('sentiment') == 'neutral')
            }
            print(f"Details page - Sentiment counts: {sentiment_counts}")
            
            sentiment_percentages = {
                key: round((count / total) * 100, 1)
                for key, count in sentiment_counts.items()
            }
            print(f"Details page - Sentiment percentages: {sentiment_percentages}")
            
            # Calculate trend data for different time ranges
            trend_data = {
                'daily': calculate_trend_data(all_analyses, 'daily'),
                'weekly': calculate_trend_data(all_analyses, 'weekly'),
                'monthly': calculate_trend_data(all_analyses, 'monthly')
            }
            print(f"Details page - Trend data sample: {trend_data['daily']['labels'][:5]}")
            print(f"Details page - Full trend data: {trend_data}")

            # Get word frequencies for each sentiment
            word_clouds = {
                'positive': get_word_frequencies(all_analyses, 'positive'),
                'negative': get_word_frequencies(all_analyses, 'negative'),
                'neutral': get_word_frequencies(all_analyses, 'neutral')
            }
            print(f"Details page - Word cloud sample: {list(word_clouds['positive'].items())[:5]}")
            print(f"Details page - Full word clouds: {word_clouds}")
        else:
            sentiment_percentages = {'positive': 0, 'negative': 0, 'neutral': 0}
            trend_data = {
                'daily': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []},
                'weekly': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []},
                'monthly': {'labels': [], 'positive': [], 'negative': [], 'neutral': [], 'confidence': []}
            }
            word_clouds = {
                'positive': {},
                'negative': {},
                'neutral': {}
            }
            print("Details page - No analyses found")
            
        return render_template('details.html', 
                             sentiment_percentages=sentiment_percentages,
                             trend_data=trend_data,
                             word_clouds=word_clouds)
    except Exception as e:
        print(f"Error fetching details data: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('details.html', error="Failed to load details data")

def calculate_trend_data(analyses, time_range):
    now = datetime.utcnow()
    
    if time_range == 'daily':
        intervals = 24
        start_time = now - timedelta(days=1)
        format_string = '%H:00'
        delta = timedelta(hours=1)
    elif time_range == 'weekly':
        intervals = 7
        start_time = now - timedelta(days=7)
        format_string = '%Y-%m-%d'
        delta = timedelta(days=1)
    else:  # monthly
        intervals = 30
        start_time = now - timedelta(days=30)
        format_string = '%Y-%m-%d'
        delta = timedelta(days=1)

    trend_data = {
        'labels': [],
        'positive': [],
        'negative': [],
        'neutral': [],
        'confidence': []
    }

    try:
        for i in range(intervals):
            current_time = start_time + (delta * i)
            next_time = current_time + delta
            
            # Filter analyses for this time period
            period_analyses = []
            for analysis in analyses:
                try:
                    # Parse the datetime and make it timezone-naive
                    analysis_time = parser.parse(analysis.get('created_at', ''))
                    if analysis_time.tzinfo is not None:
                        analysis_time = analysis_time.replace(tzinfo=None)
                    
                    if current_time <= analysis_time < next_time:
                        period_analyses.append(analysis)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing date: {e}")
                    continue
            
            trend_data['labels'].append(current_time.strftime(format_string))
            
            if period_analyses:
                # Calculate average confidence for each sentiment
                positive_analyses = [a for a in period_analyses if a.get('sentiment') == 'positive']
                negative_analyses = [a for a in period_analyses if a.get('sentiment') == 'negative']
                neutral_analyses = [a for a in period_analyses if a.get('sentiment') == 'neutral']
                
                total_analyses = len(period_analyses)
                
                trend_data['positive'].append(
                    sum(float(a.get('confidence', 0)) for a in positive_analyses) / total_analyses * 100 if positive_analyses else 0
                )
                trend_data['negative'].append(
                    sum(float(a.get('confidence', 0)) for a in negative_analyses) / total_analyses * 100 if negative_analyses else 0
                )
                trend_data['neutral'].append(
                    sum(float(a.get('confidence', 0)) for a in neutral_analyses) / total_analyses * 100 if neutral_analyses else 0
                )
                trend_data['confidence'].append(
                    sum(float(a.get('confidence', 0)) for a in period_analyses) / total_analyses * 100
                )
            else:
                trend_data['positive'].append(0)
                trend_data['negative'].append(0)
                trend_data['neutral'].append(0)
                trend_data['confidence'].append(0)
                
        return trend_data
    except Exception as e:
        print(f"Error in calculate_trend_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'labels': [],
            'positive': [],
            'negative': [],
            'neutral': [],
            'confidence': []
        }

@main_bp.route('/export')
@login_required
def export():
    return render_template('export.html')

@main_bp.route('/export/data', methods=['POST'])
@login_required
def export_data():
    try:
        data = request.json
        print(f"Export data request: {data}")  # Debug log
        
        # Get all analyses and filter by date if needed
        analyses = TweetAnalysis.get_all_by_user(current_user.id)
        
        # Filter by date range if 'recent' is selected
        if data['dataRange'] == 'recent':
            cutoff_date = datetime.now() - timedelta(days=30)
            analyses = [
                analysis for analysis in analyses
                if parser.parse(analysis.get('created_at', '')).replace(tzinfo=None) > cutoff_date
            ]
        
        print(f"Found {len(analyses)} analyses")  # Debug log
        
        # Prepare export data
        export_data = []
        for analysis in analyses:
            item = {}
            if data.get('includeScores', False):
                item['sentiment'] = analysis.get('sentiment', '')
                item['confidence'] = analysis.get('confidence', 0)
            if data.get('includeTimestamps', False):
                item['created_at'] = format_timestamp(analysis.get('created_at', ''))
            if data.get('includeContent', False):
                item['text'] = analysis.get('tweet_text', '')
            if data.get('includeWordCloud', False):
                word_freq = analysis.get('word_frequencies', {})
                if isinstance(word_freq, str):
                    try:
                        word_freq = json.loads(word_freq)
                    except:
                        word_freq = {}
                item['word_frequencies'] = word_freq
            export_data.append(item)
        
        print(f"Prepared {len(export_data)} items for export")  # Debug log
        return jsonify({'data': export_data})
    except Exception as e:
        print(f"Error in export_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/export/download', methods=['POST'])
@login_required
def export_download():
    try:
        data = request.json
        print(f"Export download request: {data}")  # Debug log
        
        # Get all analyses and filter by date if needed
        analyses = TweetAnalysis.get_all_by_user(current_user.id)
        
        # Filter by date range if 'recent' is selected
        if data['dataRange'] == 'recent':
            cutoff_date = datetime.now() - timedelta(days=30)
            analyses = [
                analysis for analysis in analyses
                if parser.parse(analysis.get('created_at', '')).replace(tzinfo=None) > cutoff_date
            ]
        
        print(f"Found {len(analyses)} analyses")  # Debug log
        
        # Prepare export data
        export_data = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        timeline_data = {}
        
        for analysis in analyses:
            item = {}
            if data.get('includeScores', False):
                sentiment = analysis.get('sentiment', '')
                item['sentiment'] = sentiment
                sentiment_counts[sentiment] += 1
                item['confidence'] = analysis.get('confidence', 0)
            if data.get('includeTimestamps', False):
                created_at = format_timestamp(analysis.get('created_at', ''))
                item['created_at'] = created_at
                date_key = created_at.split(' ')[0]  # Get just the date part
                if date_key not in timeline_data:
                    timeline_data[date_key] = {'positive': 0, 'negative': 0, 'neutral': 0}
                timeline_data[date_key][sentiment] += 1
            if data.get('includeContent', False):
                item['text'] = analysis.get('tweet_text', '')
            export_data.append(item)
        
        print(f"Prepared {len(export_data)} items for export")
        
        if data['format'] == 'csv':
            # Convert to DataFrame and export as CSV
            df = pd.DataFrame(export_data)
            output = StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            
            return send_file(
                BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name='sentiment-analysis-export.csv'
            )
        else:  # PDF
            # Create PDF using reportlab
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                rightMargin=72,
                leftMargin=72,
                topMargin=50,
                bottomMargin=50
            )
            
            # Create the story (content) for the PDF
            story = []
            styles = getSampleStyleSheet()
            
            # Add title page
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=32,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#6272a4'),  # Dracula theme purple
                leading=40
            )
            
            # Add subtitle style
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=20,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#44475a'),  # Dracula theme foreground
                leading=25
            )
            
            # Add section title style
            section_title_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=24,
                spaceBefore=30,
                spaceAfter=20,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#6272a4'),  # Dracula theme purple
                leading=30
            )
            
            # Add metadata style
            meta_style = ParagraphStyle(
                'MetaData',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=12,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#44475a'),  # Dracula theme foreground
                leading=20
            )
            
            # Title page
            story.append(Paragraph("Sentiment Analysis Report", title_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
            story.append(Paragraph(f"Data Range: {'Last 30 days' if data['dataRange'] == 'recent' else 'All time'}", meta_style))
            story.append(PageBreak())
            
            # Overview page
            story.append(Paragraph("Sentiment Distribution Overview", section_title_style))
            story.append(Spacer(1, 20))
            
            # Add summary section
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#44475a')
            )
            
            total_tweets = sum(sentiment_counts.values())
            summary_text = f"""
            Total Tweets Analyzed: {total_tweets}<br/>
            Positive Tweets: {sentiment_counts['positive']}<br/>
            Negative Tweets: {sentiment_counts['negative']}<br/>
            Neutral Tweets: {sentiment_counts['neutral']}
            """
            story.append(Paragraph(summary_text, summary_style))
            story.append(Spacer(1, 10))
            
            # Add sentiment distribution pie chart
            if sentiment_counts:
                drawing = Drawing(500, 300)  # Increased size
                pie = Pie()
                pie.x = 200  # Centered position
                pie.y = 50
                pie.width = 200  # Larger pie
                pie.height = 200
                
                # Data for pie chart
                pie_data = [sentiment_counts['positive'], sentiment_counts['negative'], sentiment_counts['neutral']]
                pie.data = pie_data
                
                # Calculate percentages for labels
                total = sum(pie_data)
                percentages = [round((count / total) * 100, 1) for count in pie_data]
                
                # More descriptive labels
                pie.labels = [
                    f'Positive ({pie_data[0]} tweets, {percentages[0]}%)',
                    f'Negative ({pie_data[1]} tweets, {percentages[1]}%)',
                    f'Neutral ({pie_data[2]} tweets, {percentages[2]}%)'
                ]
                
                # Colors matching your theme
                pie.slices.strokeWidth = 1
                pie.slices[0].fillColor = colors.HexColor('#50fa7b')  # Dracula green
                pie.slices[1].fillColor = colors.HexColor('#ff5555')  # Dracula red
                pie.slices[2].fillColor = colors.HexColor('#bd93f9')  # Dracula purple
                
                # Add percentage labels
                pie.sideLabels = False  # Don't show side labels
                pie.simpleLabels = False
                
                # Add legend with better positioning - below the chart
                legend = Legend()
                legend.x = 150  # Centered horizontally
                legend.y = 10   # Below the pie chart
                legend.dx = 8
                legend.dy = 8
                legend.fontName = 'Helvetica-Bold'
                legend.fontSize = 10
                legend.boxAnchor = 'w'
                legend.columnMaximum = 3  # Show legend items in one row
                legend.strokeWidth = 1
                legend.strokeColor = colors.HexColor('#44475a')
                legend.deltax = 150  # Space between legend items
                legend.deltay = 0
                legend.autoXPadding = 5
                legend.yGap = 0
                legend.dxTextSpace = 10
                legend.alignment = 'right'
                legend.dividerLines = 1|1|0
                legend.dividerOffsY = 4.5
                legend.subCols.minWidth = 50
                
                # More descriptive legend labels
                legend.colorNamePairs = [
                    (colors.HexColor('#50fa7b'), f'Positive: {pie_data[0]} tweets ({percentages[0]}%)'),
                    (colors.HexColor('#ff5555'), f'Negative: {pie_data[1]} tweets ({percentages[1]}%)'),
                    (colors.HexColor('#bd93f9'), f'Neutral: {pie_data[2]} tweets ({percentages[2]}%)')
                ]
                
                drawing.add(pie)
                drawing.add(legend)
                
                # Add chart title
                chart_title = ParagraphStyle(
                    'ChartTitle',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=1,
                    textColor=colors.HexColor('#44475a'),
                    spaceBefore=10,
                    spaceAfter=20
                )
                story.append(drawing)
                story.append(Spacer(1, 10))
                story.append(Paragraph(
                    "Distribution of Tweet Sentiments by Count and Percentage",
                    chart_title
                ))
                story.append(Spacer(1, 10))  # Reduced spacing
            
            # Timeline page
            story.append(Paragraph("Sentiment Timeline Analysis", section_title_style))
            story.append(Spacer(1, 20))
            
            # Add timeline chart if we have timeline data
            if timeline_data:
                drawing = Drawing(700, 250)
                chart = HorizontalLineChart()
                chart.x = 60
                chart.y = 50
                chart.height = 150
                chart.width = 550

                # Calculate confidence percentages for each date
                confidence_data = {}
                for date in sorted(timeline_data.keys()):
                    total_tweets = sum(timeline_data[date].values())
                    if total_tweets > 0:
                        for sentiment in ['positive', 'negative', 'neutral']:
                            if date not in confidence_data:
                                confidence_data[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
                            confidence_data[date][sentiment] = (timeline_data[date][sentiment] / total_tweets) * 100
                    else:
                        confidence_data[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
                
                # Update chart data with confidence percentages
                chart.data = [
                    [confidence_data[date]['positive'] for date in sorted(confidence_data.keys())],
                    [confidence_data[date]['negative'] for date in sorted(confidence_data.keys())],
                    [confidence_data[date]['neutral'] for date in sorted(confidence_data.keys())]
                ]

                # Configure category axis (simplified)
                chart.categoryAxis.categoryNames = [date for date in sorted(timeline_data.keys())]
                chart.categoryAxis.labels.angle = 30
                chart.categoryAxis.labels.fontName = 'Helvetica'
                chart.categoryAxis.labels.fontSize = 8
                chart.categoryAxis.visibleGrid = True
                chart.categoryAxis.gridStrokeColor = colors.HexColor('#44475a')
                chart.categoryAxis.gridStrokeWidth = 0.25

                # Configure value axis (simplified)
                chart.valueAxis.valueMin = 0
                chart.valueAxis.valueMax = 100
                chart.valueAxis.valueStep = 20
                chart.valueAxis.visibleGrid = True
                chart.valueAxis.gridStrokeColor = colors.HexColor('#44475a')
                chart.valueAxis.gridStrokeWidth = 0.25
                chart.valueAxis.labelTextFormat = '%d%%'
                chart.valueAxis.labels.fontSize = 8
                chart.valueAxis.labels.fontName = 'Helvetica'

                # Set colors and line styles
                chart.lines[0].strokeColor = colors.HexColor('#50fa7b')  # Positive
                chart.lines[1].strokeColor = colors.HexColor('#ff5555')  # Negative
                chart.lines[2].strokeColor = colors.HexColor('#bd93f9')  # Neutral

                # Configure line styles
                for i in range(3):
                    chart.lines[i].strokeWidth = 2

                # Add legend (simplified)
                legend = Legend()
                legend.x = 80
                legend.y = 220
                legend.fontName = 'Helvetica'
                legend.fontSize = 10
                legend.columnMaximum = 3
                legend.strokeWidth = 1
                legend.strokeColor = colors.HexColor('#44475a')
                legend.colorNamePairs = [
                    (colors.HexColor('#50fa7b'), 'Positive'),
                    (colors.HexColor('#ff5555'), 'Negative'),
                    (colors.HexColor('#bd93f9'), 'Neutral')
                ]

                drawing.add(chart)
                drawing.add(legend)

                # Add axis labels
                x_label = String(
                    chart.x + chart.width/2,
                    chart.y - 40,
                    "Date",
                    fontSize=10,
                    fillColor=colors.HexColor('#44475a'),
                    textAnchor='middle'
                )
                drawing.add(x_label)

                y_label = String(
                    chart.x - 45,
                    chart.y + chart.height/2,
                    "Confidence %",
                    fontSize=10,
                    fillColor=colors.HexColor('#44475a'),
                    textAnchor='middle',
                    angle=90
                )
                drawing.add(y_label)

                story.append(drawing)
                story.append(Spacer(1, 10))
                
                # Add chart description
                chart_desc_style = ParagraphStyle(
                    'ChartDesc',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=1,
                    textColor=colors.HexColor('#44475a'),
                    spaceBefore=10,
                    spaceAfter=10
                )
                story.append(Paragraph(
                    "Timeline showing the confidence percentage distribution for each sentiment category over time",
                    chart_desc_style
                ))
            
            # Add page break before the data table
            story.append(PageBreak())
            
            # Detailed data page
            story.append(Paragraph("Detailed Analysis Data", section_title_style))
            story.append(Spacer(1, 10))  # Reduced spacing
            story.append(Paragraph("Individual Tweet Analysis Results", subtitle_style))
            story.append(Spacer(1, 10))  # Reduced spacing
            
            # Prepare table data
            table_data = []
            headers = []
            
            if data.get('includeTimestamps', False):
                headers.append('Date')
            if data.get('includeScores', False):
                headers.extend(['Sentiment', 'Confidence'])
            if data.get('includeContent', False):
                headers.append('Content')
            
            table_data.append(headers)
            
            for item in export_data:
                row = []
                if data.get('includeTimestamps', False):
                    row.append(item.get('created_at', ''))
                if data.get('includeScores', False):
                    row.append(item.get('sentiment', ''))
                    row.append(f"{round(float(item.get('confidence', 0)) * 100)}%")
                if data.get('includeContent', False):
                    text = item.get('text', '')
                    # Wrap text at 100 characters
                    row.append(text[:100] + '...' if len(text) > 100 else text)
                table_data.append(row)
            
            # Create table with improved styling
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#282a36')),  # Dracula background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#f8f8f2')),  # Dracula foreground
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f2')),  # Light background for data
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#282a36')),  # Dark text for data
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#44475a')),  # Dracula comment color for grid
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f8f2'), colors.HexColor('#f1f1f1')]),  # Alternating rows
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ])
            
            # Create the table and set style
            table = Table(table_data, repeatRows=1)
            table.setStyle(table_style)
            
            # Add table to story
            story.append(table)
            
            # Build PDF
            doc.build(story)
            
            # Prepare response
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='sentiment-analysis-export.pdf'
            )
            
    except Exception as e:
        print(f"Error in export_download: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@main_bp.route('/chat')
@login_required
def chat_page():
    return render_template('main/chat.html')

@main_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        global gemini_model
        data = request.json
        user_message = data.get('message')
        request_type = data.get('type', 'general')
        batch_start = int(data.get('batch_start', 0))  # Get batch start index
        
        print(f"Chat request - Type: {request_type}, Message: {user_message}, Batch start: {batch_start}")
        
        if not user_message and request_type != 'detailed_analysis':
            print("No message provided")
            return jsonify({'error': 'No message provided'}), 400
            
        # Check if model is initialized
        if not gemini_model:
            print("Gemini model not initialized, attempting to reinitialize...")
            gemini_model = init_gemini()
            
        if not gemini_model:
            error_msg = "I apologize, but the AI assistant is currently unavailable. Please try again later."
            print("Failed to initialize Gemini model")
            return jsonify({
                'type': request_type,
                'response': error_msg if request_type == 'general' else None,
                'data': [{'comment': '', 'sentiment': '', 'confidence': '', 'reason': error_msg}] if request_type == 'detailed_analysis' else None
            }), 500
            
        # For detailed analysis request
        if request_type == 'detailed_analysis':
            print("Processing detailed analysis request")
            # Get all analyses for the user
            analyses = TweetAnalysis.get_all_by_user(current_user.id)
            
            if not analyses:
                print("No analyses found")
                return jsonify({
                    'type': 'detailed_analysis',
                    'data': [{'comment': '', 'sentiment': '', 'confidence': '', 'reason': 'No analyses found.'}]
                })
            
            print(f"Found {len(analyses)} analyses")
            
            # Process tweets in batches of 3 (optimized for rate limit)
            BATCH_SIZE = 3
            total_analyses = len(analyses)
            batch_end = min(batch_start + BATCH_SIZE, total_analyses)
            current_batch = analyses[batch_start:batch_end]
            
            # Prepare the analysis data for current batch
            analysis_table = []
            for analysis in current_batch:
                try:
                    # Get detailed explanation for this analysis
                    explanation = analyze_sentiment_details(gemini_model, analysis)
                    
                    analysis_table.append({
                        'comment': analysis.get('tweet_text', ''),
                        'sentiment': analysis.get('sentiment', ''),
                        'confidence': f"{float(analysis.get('confidence', 0)) * 100:.2f}%",
                        'reason': explanation
                    })
                except Exception as e:
                    print(f"Error analyzing tweet: {str(e)}")
                    analysis_table.append({
                        'comment': analysis.get('tweet_text', ''),
                        'sentiment': analysis.get('sentiment', ''),
                        'confidence': f"{float(analysis.get('confidence', 0)) * 100:.2f}%",
                        'reason': "Unable to analyze this tweet at the moment."
                    })
            
            # Include metadata about the batch processing
            response_data = {
                'type': 'detailed_analysis',
                'data': analysis_table,
                'metadata': {
                    'total_items': total_analyses,
                    'batch_start': batch_start,
                    'batch_end': batch_end,
                    'has_more': batch_end < total_analyses,
                    'remaining': total_analyses - batch_end
                }
            }
            
            print(f"Returning batch analysis data: {batch_start} to {batch_end}")
            return jsonify(response_data)
        
        # For regular chat messages
        print("Processing regular chat message")
        # Get all analyses for context
        analyses = TweetAnalysis.get_all_by_user(current_user.id)
        
        # Get response from chatbot
        response = get_chat_response(gemini_model, user_message, analyses)
        print(f"Chat response: {response}")
        
        return jsonify({'type': 'general', 'response': response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'type': request_type,
            'error': 'Failed to process request',
            'response': 'I apologize, but I encountered an error. Please try again.' if request_type == 'general' else None,
            'data': [{'comment': '', 'sentiment': '', 'confidence': '', 'reason': 'Failed to process analysis.'}] if request_type == 'detailed_analysis' else None
        }), 500 

@main_bp.route('/get_analyses', methods=['GET'])
@login_required
def get_analyses():
    try:
        # Get all analyses for the current user
        analyses = TweetAnalysis.get_all_by_user(current_user.id)
        
        if not analyses:
            return jsonify({
                'analyses': [],
                'message': 'No analyses found'
            })
        
        # Format the analyses for display
        formatted_analyses = []
        for analysis in analyses:
            formatted_analysis = {
                'text': analysis.get('tweet_text', ''),
                'sentiment': analysis.get('sentiment', ''),
                'score': float(analysis.get('confidence', 0)),
                'reason': analysis.get('reason', '')
            }
            formatted_analyses.append(formatted_analysis)
        
        return jsonify({
            'analyses': formatted_analyses
        })
        
    except Exception as e:
        print(f"Error in get_analyses: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to fetch analyses',
            'message': str(e)
        }), 500 

@main_bp.route('/profile')
@login_required
def profile():
    # Get user data
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'subscription_type': current_user.subscription_type,
        'bio': getattr(current_user, 'bio', ''),
        'profile_picture': getattr(current_user, 'profile_picture', None)
    }

    # Calculate membership duration
    join_date = getattr(current_user, 'created_at', None)
    if join_date is None:
        membership_duration = 0
    else:
        try:
            # Convert string to datetime if needed
            if isinstance(join_date, str):
                join_date = parser.parse(join_date)
            
            # Make both datetimes timezone-aware using UTC
            if join_date.tzinfo is None:
                join_date = join_date.replace(tzinfo=datetime.timezone.utc)
            
            current_time = datetime.now(datetime.timezone.utc)
            membership_duration = (current_time - join_date).days
        except Exception as e:
            print(f"Error calculating membership duration: {str(e)}")
            membership_duration = 0

    # Get all analyses for statistics
    analyses = TweetAnalysis.get_all_by_user(current_user.id)
    
    # Calculate sentiment statistics
    total_analyses = len(analyses) if analyses else 0
    sentiment_counts = {
        'positive': sum(1 for a in analyses if a.get('sentiment') == 'positive') if analyses else 0,
        'negative': sum(1 for a in analyses if a.get('sentiment') == 'negative') if analyses else 0,
        'neutral': sum(1 for a in analyses if a.get('sentiment') == 'neutral') if analyses else 0
    }

    return render_template('profile.html',
        username=user_data['username'],
        email=user_data['email'],
        subscription_type=user_data['subscription_type'],
        bio=user_data['bio'],
        profile_picture=user_data['profile_picture'],
        membership_duration=membership_duration,
        total_analyses=total_analyses,
        positive_count=sentiment_counts['positive'],
        negative_count=sentiment_counts['negative'],
        neutral_count=sentiment_counts['neutral']
    )

@main_bp.route('/api/update-bio', methods=['POST'])
@login_required
def update_bio():
    try:
        data = request.get_json()
        if not data or 'bio' not in data:
            return jsonify({'success': False, 'message': 'No bio provided'}), 400

        try:
            # Update bio in Supabase
            response = supabase.table('users').update({
                'bio': data['bio']
            }).eq('id', str(current_user.id)).execute()

            if not response.data:
                return jsonify({'success': False, 'message': 'Failed to update bio in database'}), 500

            return jsonify({'success': True, 'message': 'Bio updated successfully'})
        except Exception as e:
            print(f"Error updating bio in database: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to update bio in database'}), 500

    except Exception as e:
        print(f"Error updating bio: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/update-profile-picture', methods=['POST'])
@login_required
def update_profile_picture():
    try:
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Save file locally first
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        new_filename = f"{current_user.id}_{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to save file'}), 500

        # Update profile picture path in Supabase
        file_url = url_for('static', filename=f'images/{new_filename}', _external=True)
        try:
            response = supabase.table('users').update({
                'profile_picture': file_url
            }).eq('id', str(current_user.id)).execute()

            if not response.data:
                # Clean up the file if database update failed
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'success': False, 'message': 'Failed to update profile picture in database'}), 500

            return jsonify({
                'success': True,
                'message': 'Profile picture updated successfully',
                'url': file_url
            })
        except Exception as e:
            # Clean up the file if database update failed
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"Error updating profile picture in database: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to update profile picture in database'}), 500

    except Exception as e:
        print(f"Error updating profile picture: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('main/settings.html', 
                         user=current_user,
                         title='Settings') 