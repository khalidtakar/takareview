# TakaReview 🎯

TakaReview is a powerful web-based sentiment analysis dashboard designed specifically for content creators to understand and analyze audience reactions across social media platforms.

## 🌟 Features

- **Multi-Platform Analysis**: Analyze comments from Twitter, YouTube, and Reddit
- **Dual AI Analysis**:
  - RoBERTa model for precise sentiment classification
  - Google's Gemini AI for in-depth sentiment insights and recommendations
- **Comprehensive Sentiment Analysis**:
  - Detailed percentage breakdowns (positive, negative, neutral)
  - Common words grouped by sentiment type
  - Sentiment trends over time
  - Engagement metrics and patterns
- **Rich Data Visualization**:
  - Interactive radar graphs for sentiment distribution
  - Pie charts for sentiment proportions
  - Trend graphs for temporal analysis
  - Word clouds for common phrases
- **Export Capabilities**:
  - Download analyses as CSV for data processing
  - Export reports as PDF for presentations
  - Save visualizations as high-quality images
  - Batch export functionality
- **User-Friendly Dashboard**:
  - Clean and intuitive interface
  - Real-time sentiment updates
  - Customizable date ranges
  - Filtering and sorting options
- **Profile Management**:
  - Customizable user profiles with bio
  - Profile picture upload
  - Analysis history tracking
  - Saved reports section
- **Premium Features**:
  - Advanced analytics with deeper insights
  - Extended data retention
  - Priority processing
  - Custom report templates
- **Theme Customization**:
  - Dark/Light mode toggle
  - Responsive design for all devices
  - Customizable dashboard layout
- **Security & Privacy**:
  - OAuth authentication
  - Secure data storage
  - User data encryption
  - Rate limiting protection

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (via Supabase)
- **Visualization**: Chart.js
- **ML Model**: CardiffNLP Twitter RoBERTa Base Sentiment Model
- **APIs**: Twitter, YouTube, Reddit
- **Storage**: Supabase Storage for profile pictures

## 📦 Project Structure

```
takareview/
├── app/                    # Main application package
│   ├── __init__.py        # App initialization
│   ├── analyse/           # Analysis module
│   │   └── sentiment.py   # Sentiment analysis logic
│   ├── auth/             # Authentication module
│   │   ├── __init__.py
│   │   └── routes.py     # Auth routes
│   ├── chatbot.py        # Chatbot functionality
│   ├── database.py       # Database operations
│   ├── forms.py          # Form definitions
│   ├── models/           # Database models
│   │   └── user.py       # User model
│   ├── routes/           # Route modules
│   │   ├── __init__.py
│   │   └── main.py       # Main routes
│   ├── static/           # Static assets
│   │   ├── css/         # Stylesheets
│   │   ├── js/          # JavaScript files
│   │   └── img/         # Images
│   ├── templates/        # HTML templates
│   │   ├── main/        # Main templates
│   │   └── auth/        # Auth templates
│   └── utils/           # Utility functions
├── config.py             # Configuration
├── requirements.txt      # Dependencies
└── run.py               # Entry point
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (via Supabase)
- Node.js (for package management)
- Modern web browser (Chrome, Firefox, or Edge recommended)
- Git

### Installation

1. Clone the repository

```bash
git clone https://github.com/khalidtakar/takareview.git
cd takareview
```

2. Create and activate virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate # On Unix/MacOS
```

3. Install required dependencies:

```bash
# Core dependencies
pip install numpy==1.24.3
pip install torch==2.0.1
pip install transformers==4.28.1

# Flask and extensions
pip install flask==2.0.1
pip install flask-login==0.6.2
pip install flask-wtf==1.1.1
pip install flask-sqlalchemy==3.0.2
pip install flask-migrate==4.0.4

# Database and storage
pip install supabase==1.0.3
pip install psycopg2-binary==2.9.6
pip install python-dotenv==1.0.0

# Date handling and utilities
pip install python-dateutil==2.8.2

# OAuth and API dependencies
pip install requests-oauthlib==1.3.1
pip install tweepy==4.12.1

# ML and analysis
pip install pandas==1.5.3
pip install scikit-learn==1.2.2
```

4. Set up environment variables in .env file:

```env
# Supabase Configuration
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
DATABASE_URL=<your-database-connection-string>

# Flask Configuration
SECRET_KEY=<your-secret-key>
FLASK_APP=run.py
FLASK_ENV=development

# OAuth Configuration
TWITTER_CLIENT_ID=<your-twitter-client-id>
TWITTER_CLIENT_SECRET=<your-twitter-client-secret>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>

# AI/ML Configuration
GEMINI_API_KEY=<your-gemini-api-key>
```

> ⚠️ **IMPORTANT**:
>
> - Never commit the actual API keys or secrets to version control
> - Replace the placeholders above with your actual credentials in your local .env file
> - Keep your .env file in your .gitignore

5. Initialize the database:

```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:

```bash
python run.py
```

The application will be available at http://127.0.0.1:5000

### First-time Setup

1. Register a new account using email or OAuth
2. Complete your profile setup
3. Connect your Twitter account to start analyzing sentiment

### Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed with correct versions
2. Verify your .env file contains all required variables
3. Check if the virtual environment is activated
4. Clear browser cache if facing frontend issues
5. Ensure Supabase is accessible and credentials are correct

## 📝 API Documentation

The API documentation will be available at `/api/docs` when running the application locally.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CardiffNLP for the Twitter RoBERTa Base Sentiment Model
- Chart.js for the visualization library
- Supabase for database and storage solutions

# TakaReview MVP Roadmap

## Phase 1: Foundation (Week 1-2)

- [x] Project setup and repository initialization
- [x] Development environment configuration
- [x] Flask setup
- [x] PostgreSQL installation
- [x] Basic project structure
- [x] Initial documentation

## Phase 2: Core Backend (Week 3-4)

- [x] Flask REST API development
- [x] Comment fetching endpoints
- [x] Sentiment analysis integration
- [x] Basic CRUD operations
- [x] Database schema design
- [x] Twitter RoBERTa model integration
- [x] Basic error handling

## Phase 3: Frontend MVP (Week 5-6)

- [x] Basic dashboard layout
- [x] Chart.js integration
- [x] Sentiment visualization components
- [x] Triangular radar chart
- [x] Basic sentiment percentage display
- [x] API integration with frontend

## Phase 4: Integration & Testing (Week 7-8)

- [x] Error handling and rate limiting
- [ ] Basic unit tests
- [x] UI/UX refinements

## MVP Success Criteria

- [x] Functional sentiment analysis dashboard
- [x] Basic visualization of sentiment data
- [x] Stable API performance
- [x] Clean, intuitive user interface

## Post-MVP Considerations

- Enhanced visualization options
- User authentication
- Advanced analytics
- LLM-powered chatbot
- Premium features
