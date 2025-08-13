from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import google.generativeai as genai
import asyncio
import time
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure database with support for Render/production and local development
# Prefer DATABASE_URL if provided (e.g., from a managed Postgres). Otherwise, use SQLite in the instance folder.
os.makedirs(app.instance_path, exist_ok=True)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # SQLAlchemy expects the 'postgresql://' scheme
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    sqlite_path = os.path.join(app.instance_path, 'code_review.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

# Initialize Gemini model with optimized settings
model = genai.GenerativeModel(
    'gemini-pro',
    generation_config=genai.types.GenerationConfig(
        temperature=0.1,
        max_output_tokens=800,
        top_p=0.8,
        top_k=20
    )
)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    reviews = db.relationship('CodeReview', backref='author', lazy=True)

# Code Review Model
class CodeReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    review_result = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Ensure tables exist when running under a WSGI server (e.g., Gunicorn on Render)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        recent_reviews = CodeReview.query.filter_by(user_id=current_user.id).order_by(CodeReview.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', reviews=recent_reviews)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('auth.html', mode='login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/review')
@login_required
def review_page():
    return render_template('review.html')

@app.route('/api/analyze-code', methods=['POST'])
@login_required
def analyze_code():
    try:
        start_time = time.time()
        data = request.get_json()
        code = data.get('code')
        language = data.get('language', 'python')
        title = data.get('title', 'Code Analysis')
        error_message = data.get('error', '')
        
        # Limit code length for faster processing
        if len(code) > 2000:
            code = code[:2000] + "... [truncated for faster analysis]"
        
        # Create comprehensive analysis prompt with enhanced error detection
        prompt = f"""Perform comprehensive analysis of this {language} code with detailed error detection:

```{language}
{code}
```

Error context: {error_message if error_message else 'No specific error reported'}

IMPORTANT: Focus heavily on debugging and error detection first. Provide detailed JSON analysis:

{{
    "error_detection": {{
        "has_errors": true/false,
        "error_summary": "Brief description of main errors found",
        "detailed_errors": [
            {{
                "error_type": "syntax/logic/runtime/semantic",
                "line_number": "Specific line number (e.g., 5)",
                "line_content": "Exact content of the problematic line",
                "column_position": "Character position in line if applicable",
                "error_description": "What exactly is wrong",
                "actual_error": "The specific error message or problem",
                "error_severity": "critical/high/medium/low",
                "why_it_happens": "Explanation of why this error occurs",
                "how_to_fix": "Step-by-step solution",
                "corrected_line": "Fixed version of the specific line",
                "corrected_code_snippet": "Fixed version of surrounding code context"
            }}
        ],
        "error_categories": {{
            "syntax_errors": ["Specific syntax problems with line numbers"],
            "logic_errors": ["Logical issues that cause wrong behavior"],
            "runtime_errors": ["Issues that would cause crashes"],
            "semantic_errors": ["Code that compiles but doesn't do what intended"]
        }}
    }},
    "debug_analysis": {{
        "overall_code_health": "healthy/has_issues/critical_issues",
        "debugging_priority": ["Most critical issues to fix first"],
        "fixed_code": "Complete corrected version of the code",
        "explanation_of_fixes": "Detailed explanation of all changes made",
        "testing_suggestions": ["How to test the fixed code"]
    }},
    "code_review": {{
        "overall_rating": 8,
        "code_quality": {{
            "rating": 7,
            "assessment": "Assessment after considering errors"
        }},
        "readability": {{
            "rating": 8,
            "assessment": "Readability assessment with specific rating"
        }},
        "maintainability": {{
            "rating": 7,
            "assessment": "Maintainability assessment with specific rating"
        }},
        "line_by_line_analysis": [
            {{
                "line_number": "Line number",
                "line_content": "Actual line content",
                "quality_score": "1-10 rating for this line",
                "issues": ["Specific issues with this line"],
                "suggestions": ["Improvements for this line"],
                "complexity_note": "Complexity impact of this line"
            }}
        ]
    }},
    "security_analysis": {{
        "vulnerabilities": ["Security issues found"],
        "recommendations": ["Security improvements"]
    }},
    "performance_analysis": {{
        "bottlenecks": ["Performance issues with line numbers"],
        "optimizations": ["Performance improvements with specific suggestions"],
        "time_complexity": {{
            "overall": "O(n), O(n²), etc.",
            "breakdown": [
                {{
                    "function_name": "function name",
                    "lines": "line range (e.g., 5-10)",
                    "complexity": "O(n)",
                    "explanation": "Why this complexity"
                }}
            ]
        }},
        "space_complexity": {{
            "overall": "O(1), O(n), etc.",
            "breakdown": [
                {{
                    "component": "data structure or variable",
                    "lines": "line range",
                    "complexity": "O(n)",
                    "explanation": "Memory usage explanation"
                }}
            ]
        }},
        "complexity_analysis": {{
            "best_case": "Best case scenario complexity",
            "average_case": "Average case complexity",
            "worst_case": "Worst case complexity",
            "scalability_notes": "How code scales with input size"
        }}
    }},
    "improvement_suggestions": {{
        "best_practices": ["Best practice recommendations"],
        "refactoring": ["Refactoring suggestions"],
        "modern_features": ["Modern language features to use"]
    }},
    "summary": {{
        "error_status": "error-free/has-errors/critical-errors",
        "main_issues": ["Top 3 most important issues"],
        "strengths": ["Code strengths"],
        "priority_fixes": ["Most important fixes in order"],
        "overall_score": 8
    }}
}}"""
        
        # Get AI analysis with timeout
        try:
            response = model.generate_content(
                prompt,
                request_options={'timeout': 15}  # 15 second timeout for comprehensive analysis
            )
            
            if not response.text:
                raise Exception("Empty response from AI")
                
            ai_response = response.text
            
        except Exception as ai_error:
            # Fallback comprehensive response if AI fails
            ai_response = f'''{{
                "error_detection": {{
                    "has_errors": false,
                    "error_summary": "Unable to perform detailed error analysis due to timeout",
                    "detailed_errors": [],
                    "error_categories": {{
                        "syntax_errors": ["Manual syntax check recommended"],
                        "logic_errors": ["Manual logic review needed"],
                        "runtime_errors": ["Test code execution thoroughly"],
                        "semantic_errors": ["Verify code behavior matches intent"]
                    }}
                }},
                "debug_analysis": {{
                    "overall_code_health": "unknown",
                    "debugging_priority": ["Manual debugging recommended"],
                    "fixed_code": "Original code - manual debugging required",
                    "explanation_of_fixes": "AI analysis timed out - manual review needed",
                    "testing_suggestions": ["Test all code paths", "Use debugger tools", "Add logging statements"]
                }},
                "code_review": {{
                    "overall_rating": 6,
                    "code_quality": {{
                        "rating": 6,
                        "assessment": "Basic {language} structure appears functional"
                    }},
                    "readability": {{
                        "rating": 6,
                        "assessment": "Code structure seems readable"
                    }},
                    "maintainability": {{
                        "rating": 6,
                        "assessment": "Standard maintainability practices recommended"
                    }}
                }},
                "security_analysis": {{
                    "vulnerabilities": ["Manual security review recommended"],
                    "recommendations": ["Follow security best practices", "Validate all inputs"]
                }},
                "performance_analysis": {{
                    "bottlenecks": ["Profile code for performance issues"],
                    "optimizations": ["Consider algorithmic improvements"],
                    "time_complexity": {{
                        "overall": "Analysis not available",
                        "breakdown": []
                    }},
                    "space_complexity": {{
                        "overall": "Analysis not available", 
                        "breakdown": []
                    }},
                    "complexity_analysis": {{
                        "best_case": "Manual analysis required",
                        "average_case": "Manual analysis required",
                        "worst_case": "Manual analysis required",
                        "scalability_notes": "Test with different input sizes"
                    }}
                }},
                "improvement_suggestions": {{
                    "best_practices": ["Follow {language} coding standards", "Add proper error handling"],
                    "refactoring": ["Consider code organization improvements"],
                    "modern_features": ["Use modern {language} features where appropriate"]
                }},
                "summary": {{
                    "error_status": "unknown",
                    "main_issues": ["Analysis timeout - manual review needed"],
                    "strengths": ["Code structure exists"],
                    "priority_fixes": ["Manual code review recommended"],
                    "overall_score": 6
                }}
            }}'''
        
        # Save analysis to database
        review = CodeReview(
            title=title,
            code=code,
            language=language,
            review_result=ai_response,
            user_id=current_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'analysis': ai_response,
            'review_id': review.id,
            'processing_time': processing_time
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Keep the old endpoint for backward compatibility
@app.route('/api/review-code', methods=['POST'])
@login_required
def review_code():
    # Redirect to the new comprehensive analysis
    return analyze_code()

@app.route('/api/debug-code', methods=['POST'])
@login_required
def debug_code():
    try:
        data = request.get_json()
        code = data.get('code')
        error_message = data.get('error', '')
        language = data.get('language', 'python')
        
        # Limit code for faster processing
        if len(code) > 1500:
            code = code[:1500] + "... [truncated]"
        
        prompt = f"""Quick debug for {language}:

```{language}
{code}
```

Error: {error_message}

JSON (be brief):
{{
    "issue_explanation": "Brief issue description",
    "fixed_code": "Key fixes only",
    "fix_explanation": "Short explanation",
    "prevention_tips": ["Top 2 tips"]
}}"""
        
        try:
            response = model.generate_content(
                prompt,
                request_options={'timeout': 8}
            )
            debug_result = response.text if response.text else "Debug analysis unavailable"
        except:
            debug_result = f'''{{
                "issue_explanation": "Unable to analyze due to timeout",
                "fixed_code": "Manual debugging required",
                "fix_explanation": "Please check syntax and logic manually",
                "prevention_tips": ["Use IDE debugging tools", "Add print statements for debugging"]
            }}'''
        
        return jsonify({
            'success': True,
            'debug_result': debug_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history')
@login_required
def history():
    reviews = CodeReview.query.filter_by(user_id=current_user.id).order_by(CodeReview.created_at.desc()).all()
    return render_template('history.html', reviews=reviews)

@app.route('/api/review/<int:review_id>')
@login_required
def get_review(review_id):
    review = CodeReview.query.filter_by(id=review_id, user_id=current_user.id).first()
    if review:
        return jsonify({
            'success': True,
            'review': {
                'id': review.id,
                'title': review.title,
                'code': review.code,
                'language': review.language,
                'result': review.review_result,
                'created_at': review.created_at.isoformat()
            }
        })
    return jsonify({'success': False, 'error': 'Review not found'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)