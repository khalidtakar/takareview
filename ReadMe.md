# TakaReview 🎯

TakaReview is a powerful web-based sentiment analysis dashboard designed specifically for content creators to understand and analyze audience reactions across social media platforms.

## 🌟 Features (MVP)

- **Multi-Platform Analysis**: Analyze comments from Twitter, YouTube, and Reddit
- **Sentiment Breakdown**: Get detailed percentage breakdowns of sentiment (positive, negative, neutral)
- **Visual Analytics**: Interactive visualization of sentiment data using hexagonal radar charts
- **Easy-to-Use Dashboard**: Clean and intuitive interface for quick sentiment insights

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Visualization**: Chart.js
- **ML Model**: CardiffNLP Twitter RoBERTa Base Sentiment Model
- **APIs**: Twitter, YouTube, Reddit

## 📦 Project Structure

takareview/
├── app/                      # Main application package
│   ├── __init__.py          # App initialization and configuration
│   ├── auth/                # Authentication module
│   │   ├── __init__.py     # Blueprint definition
│   │   ├── routes.py       # Login/register/logout routes
│   │   └── forms.py        # Login and registration forms
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── user.py         # User model definition
│   ├── static/             # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   ├── style.css   # Main styles
│   │   │   └── pricing.css # Pricing page styles
│   │   └── js/
│   │       └── main.js     # Main JavaScript file
│   └── templates/          # HTML templates
│       ├── auth/          # Auth-related templates
│       │   ├── login.html
│       │   └── register.html
│       ├── base.html      # Base template
│       └── pricing.html   # Pricing page
├── config.py              # Configuration settings
├── requirements.txt       # Project dependencies
└── run.py                # Application entry point

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for package management)

### Installation

1. Clone the repository

bash

git clone https://github.com/yourusername/takareview.git
cd takareview

2. Create and activate virtual environment

bash

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies

bash

pip install -r requirements.txt

4. Set up environment variables

bash

cp .env.example .env

Edit .env with your configuration

5. Initialize the database

bash

flask db init

flask db migrate

flask db upgrade

6. Run the application

bash

flask run


## 📝 API Documentation

The API documentation will be available at `/api/docs` when running the application locally.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CardiffNLP for the Twitter RoBERTa Base Sentiment Model
- Chart.js for the visualization library

# TakaReview MVP Roadmap

## Phase 1: Foundation (Week 1-2)
- [x] Project setup and repository initialization
- [ ] Development environment configuration
  - [ ] Flask setup
  - [ ] PostgreSQL installation
  - [ ] Basic project structure
- [ ] API keys acquisition (Twitter, YouTube, Reddit)
- [ ] Initial documentation

## Phase 2: Core Backend (Week 3-4)
- [ ] Flask REST API development
  - [ ] Comment fetching endpoints
  - [ ] Sentiment analysis integration
  - [ ] Basic CRUD operations
- [ ] Database schema design
- [ ] Twitter RoBERTa model integration
- [ ] Basic error handling

## Phase 3: Frontend MVP (Week 5-6)
- [ ] Basic dashboard layout
- [ ] Chart.js integration
- [ ] Sentiment visualization components
  - [ ] Hexagonal radar chart
  - [ ] Basic sentiment percentage display
- [ ] API integration with frontend

## Phase 4: Integration & Testing (Week 7-8)
- [ ] Social media API integration
  - [ ] Twitter implementation
  - [ ] YouTube implementation
  - [ ] Reddit implementation
- [ ] Error handling and rate limiting
- [ ] Basic unit tests
- [ ] UI/UX refinements

## MVP Success Criteria
- [ ] Functional sentiment analysis dashboard
- [ ] Support for at least two social media platforms
- [ ] Basic visualization of sentiment data
- [ ] Stable API performance
- [ ] Clean, intuitive user interface

## Post-MVP Considerations
- Enhanced visualization options
- User authentication
- Advanced analytics
- LLM-powered chatbot
- Premium features#   t a k a r e v i e w  
 #   t a k a r e v i e w  
 