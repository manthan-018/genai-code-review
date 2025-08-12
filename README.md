# 🤖 AI Code Review & Debug Tool

A comprehensive web application that leverages **Google Gemini AI** and **LangChain** to provide intelligent code review, debugging, and quality analysis with detailed error detection and complexity analysis.

![AI Code Review](https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple?style=for-the-badge)

## ✨ Features

### 🔍 **Comprehensive Code Analysis**
- **Debug-First Approach** - Identifies syntax, logic, runtime, and semantic errors
- **Line-by-Line Analysis** - Detailed quality assessment for each line of code
- **Error Location Mapping** - Exact line numbers and column positions for errors
- **Severity Classification** - Critical, High, Medium, Low error categorization

### 📊 **Advanced Complexity Analysis**
- **Time Complexity Analysis** - Big O notation with function-level breakdown
- **Space Complexity Analysis** - Memory usage analysis with component breakdown
- **Performance Scenarios** - Best, Average, and Worst case analysis
- **Scalability Insights** - How code performs with different input sizes

### 🎯 **Smart Code Review**
- **Quality Metrics** - Individual ratings for Code Quality, Readability, Maintainability
- **Star Rating System** - Visual 1-10 star ratings for all metrics
- **Security Analysis** - Vulnerability detection and security recommendations
- **Best Practices** - Industry standard recommendations and modern features

### 🛠️ **Intelligent Debugging**
- **Automatic Error Detection** - Finds and explains code issues
- **Fix Suggestions** - Step-by-step resolution instructions
- **Code Corrections** - Provides fixed versions of problematic code
- **Before/After Comparison** - Side-by-side original vs corrected code

### 🎨 **Modern User Experience**
- **Responsive Design** - Works perfectly on desktop and mobile
- **Interactive UI** - Animated components and smooth transitions
- **User Authentication** - Secure registration and login system
- **Review History** - Track and manage all your code reviews
- **Real-time Analysis** - Fast AI processing with progress indicators

## 🚀 **Tech Stack**

### **Backend**
- **Python 3.8+** - Core programming language
- **Flask 2.3+** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **SQLite** - Database storage

### **AI & Machine Learning**
- **Google Gemini AI** - Advanced code analysis
- **LangChain** - AI workflow management
- **Custom Prompts** - Optimized for code review tasks

### **Frontend**
- **HTML5** - Modern markup
- **CSS3** - Advanced styling with gradients and animations
- **JavaScript ES6+** - Interactive functionality
- **Font Awesome** - Icon library
- **Prism.js** - Syntax highlighting

### **Deployment**
- **Render** - Cloud platform deployment
- **Gunicorn** - WSGI HTTP Server
- **Environment Variables** - Secure configuration

## 📦 **Installation**

### **Prerequisites**
- Python 3.8 or higher
- Git
- Google Gemini API key

### **Setup Steps**

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-code-review.git
cd ai-code-review
```

2. **Create virtual environment:**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration:**
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_super_secret_key_here
```

5. **Run the application:**
```bash
python app.py
```

6. **Access the application:**
Open your browser and navigate to `http://localhost:5000`

## 🎯 **Usage Guide**

### **Getting Started**
1. **Register** - Create a new account with email and username
2. **Login** - Sign in to access the analysis features
3. **Dashboard** - View your analysis statistics and recent reviews

### **Code Analysis**
1. **Comprehensive Analysis** - Full debug + review + complexity analysis
2. **Quick Review** - Fast basic code review
3. **Error Input** - Optional error message for targeted debugging
4. **Language Selection** - Choose from 10+ programming languages

### **Understanding Results**
- **Error Detection** - Red sections show critical issues with fixes
- **Quality Metrics** - Star ratings for different code aspects
- **Complexity Analysis** - Time/Space complexity with visual breakdown
- **Line-by-Line** - Individual line quality assessment
- **Priority Fixes** - Ordered list of most important improvements

## 🌐 **Deployment**

### **Deploy to Render**

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Connect your GitHub repository
   - Choose "Web Service"

3. **Environment Variables:**
   Set these in Render dashboard:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   SECRET_KEY=your_secret_key
   ```

4. **Deploy:**
   - Render will automatically use `render.yaml` configuration
   - Build and deployment will start automatically

### **Environment Variables**
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `SECRET_KEY` - Flask secret key for sessions (generate a secure random string)

## 📚 **API Documentation**

### **Endpoints**

#### **Authentication**
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

#### **Code Analysis**
- `POST /api/analyze-code` - Comprehensive code analysis
- `POST /api/review-code` - Quick code review
- `POST /api/debug-code` - Code debugging

#### **Data Retrieval**
- `GET /api/review/<id>` - Get specific review details
- `GET /history` - User's review history

### **Request Format**
```json
{
    "code": "your_code_here",
    "language": "python",
    "title": "My Code Review",
    "error": "optional_error_message"
}
```

### **Response Format**
```json
{
    "success": true,
    "analysis": "detailed_analysis_json",
    "review_id": 123,
    "processing_time": 3.2
}
```

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit your changes:**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### **Development Guidelines**
- Follow PEP 8 for Python code
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Issues** - Report bugs or request features via [GitHub Issues](https://github.com/yourusername/ai-code-review/issues)
- **Discussions** - Join community discussions
- **Documentation** - Check the wiki for detailed guides

## 🙏 **Acknowledgments**

- **Google Gemini AI** - For powerful code analysis capabilities
- **LangChain** - For AI workflow management
- **Flask Community** - For the excellent web framework
- **Open Source Contributors** - For various libraries and tools used

---

**Made with ❤️ by [Your Name]**

*Star ⭐ this repository if you find it helpful!*