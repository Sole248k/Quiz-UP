from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import requests
from .models import *
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from functools import wraps
from django.db.models import Count
import google.generativeai as genai
import pdfplumber
import re


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDsOk50xy6RsxkzOgllv5FYTFcLxM04iHY')

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)

def mainpage(request):
    user_data = request.session.get('user', None)
    return render(request, 'quiz_up_app/mainpage.html', {'user':user_data})

def generatedquiz(request):
    # Assuming user_data is available in session, fetch the current user's questions
    user_data = request.session.get('user', None)
    if user_data:
        try:
            # Fetch random 30 questions associated with the current user
            questions = Question.objects.filter(document__user__email=user_data['email']).order_by('?')[:30]
            context = {
                'questions': questions
            }
            if not questions:  # If no questions are found
                context['error'] = 'No questions found in database.'
            
            return render(request, 'quiz_up_app/generatedquiz.html', context)
        except Exception as e:
            print(f"Error fetching questions: {e}")
            # Handle error, possibly redirect or show an error message
            return render(request, 'quiz_up_app/generatedquiz.html', {'error': 'Error fetching questions.'})
    else:
        # Handle case where user_data is not found in session
        return render(request, 'quiz_up_app/generatedquiz.html', {'error': 'User data not found.'})

def signin(request):
    if request.method == "GET":
        identifier = request.GET.get('identifier')
        passw = request.GET.get('password')
        now = datetime.now()
        hour = now.hour
        greeting = 'Good Morning' if 5 <= hour < 12 else ('Good afternoon' if 12 <= hour < 18 else 'Good Evening')
        try:
            user = Users.objects.get(Q(email=identifier) | Q(username=identifier), password=passw)
            request.session['user'] = {
                    'username': user.username,
                    'email': user.email,
                    'password' : user.password,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                }
            return redirect ('dragfile')
        except Users.DoesNotExist as e:
            print("Wala yung user")
            return render(request, 'quiz_up_app/signin.html')
    else:
        return render(request, 'quiz_up_app/signin.html')
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST or None)
        if form.is_valid():
            user = form.save()
            # Extract the password and confirm password from the POST data
            password = request.POST.get('password')
            confirmpass = request.POST.get('confirmpassword')

            # Check if the passwords match
            if password == confirmpass:
                # Print user details for debugging
                print(f"New user created: {user.username}, {user.email}")

                request.session['user'] = {
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'username': user.username,
                    'email': user.email,
                }

                return redirect('landing')
            else:
                # Print error message for debugging
                print("Passwords do not match.")
                return render(request, 'quiz_up_app/signup.html')

        else:
            # Print form errors for debugging
            print("Form is invalid:", form.errors)
            return render(request, 'quiz_up_app/signup.html')

    else:
        return render(request, 'quiz_up_app/signup.html')
    
def dragfile(request):
    user_data = request.session.get('user', None)
    if request.method == 'POST':
        uploaded_file = request.FILES.get('dropzone-file')  # Safely access the file
        
        if uploaded_file:  # Proceed only if a file was uploaded
            print(f"File '{uploaded_file.name}' was uploaded successfully.")
            
            # Process the uploaded file
            with pdfplumber.open(uploaded_file) as pdf:
                text_content = ""
                for page in pdf.pages:
                    text_content += page.extract_text()
            
            print("Text content extracted from the PDF successfully.")

            # Generate questions based on the extracted text
            genai.configure(api_key='AIzaSyDsOk50xy6RsxkzOgllv5FYTFcLxM04iHY')  # Configure your AI model
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

            # Construct prompt for generating questions
            prompt = f"Generate 30 multiple-choice numbered 1-30 questions with 4 options and the correct answer based on this text: {text_content}\n\nEach question should be formatted as follows:\n1. Question text?\n   a) Option A\n   b) Option B\n   c) Option C\n   d) Option D\n**Answer: correct option in capital letter (A,B,C,D)\n"            
            response = model.generate_content(prompt)

            # Debugging: Inspect the response object
            print("AI-generated response object:", response.__dict__)

            # Extract the actual generated text from the response
            if hasattr(response, '_result'):
                try:
                    response_text = response._result.candidates[0].content.parts[0].text
                    print("Extracted text from the AI response:", response_text)
                except (AttributeError, IndexError) as e:
                    print("Error extracting text from the AI response:", e)
                    return render(request, 'quiz_up_app/dragfile.html', {'error': 'Error extracting text from AI response.'})
            else:
                print("The response object does not have a '_result' attribute.")
                return render(request, 'quiz_up_app/dragfile.html', {'error': 'Error in AI response.'})

            print("AI-generated response received successfully.")
            questions_data = parse_gemini_response(response_text)

            # Create a Document instance for the uploaded file
            if user_data:  # Assuming user data is correctly populated in session
                try:
                    user_instance = Users.objects.get(email=user_data['email'])  # Fetch the user instance
                    document = Document.objects.create(
                        user=user_instance,  # Assign the user instance here
                        title=uploaded_file.name,
                        file=uploaded_file,
                    )
                    print(f"Document '{uploaded_file.name}' created.")

                    # Create Question instances associated with the Document
                    for i, question_data in enumerate(questions_data, start=1):
                        try:
                            Question.objects.create(
                                document=document,
                                question_text=question_data['question'],
                                option1=question_data['choices'][0],
                                option2=question_data['choices'][1],
                                option3=question_data['choices'][2],
                                option4=question_data['choices'][3],
                                correct_answer=question_data['answer'],
                            )
                            print(f"Question {i} created: {question_data['question']}")
                        except Exception as e:
                            print(f"Error creating Question {i}: {e}")
                            continue

                    print("All questions were created successfully.")
                    return redirect('generatedquiz')
                except Users.DoesNotExist:
                    print("User not found.")
                    return render(request, 'quiz_up_app/dragfile.html', {'error': 'User not found.'})
            else:
                print("User data not found in session.")
                return render(request, 'quiz_up_app/dragfile.html', {'error': 'User data not found.'})

        else:
            print("No file was uploaded.")

    print("Rendering the dragfile.html template.")
    return render(request, 'quiz_up_app/dragfile.html', {'user': user_data})

def parse_gemini_response(response_text):
    questions = []
    # Split the response into question blocks based on the numbering pattern
    question_blocks = re.split(r'\n*(\d+)\.\s+', response_text)[1:]  # Use capturing group to retain question numbers

    # Iterate through the blocks in pairs (question number, question content)
    for i in range(0, len(question_blocks), 2):
        try:
            question_number = question_blocks[i].strip()
            question_content = question_blocks[i+1].strip()

            # Extract the question and answer parts
            question_match = re.match(r'^(.*?)(?:\n\s*[a-d]\)\s.*?){4}\s*\*\*Answer:\s*(.*?)\*\*', question_content, re.S)
            if not question_match:
                print(f"Skipping block due to missing or malformed content: {question_content}")
                continue

            question_text = question_match.group(1).strip()
            answer_text = question_match.group(2).strip()

            # Extract choices from the block
            choices = re.findall(r'\n\s*([a-d])\)\s+(.*?)(?=\n\s*[a-d]\)|\*\*Answer:|$)', question_content, re.S)

            if len(choices) != 4:
                print(f"Skipping question {question_number} due to incorrect number of choices: {choices}")
                continue

            questions.append({
                'question': question_text,
                'choices': [choice[1].strip() for choice in choices],  # Extract only the choice text
                'answer': answer_text,
            })

        except Exception as e:
            print(f"Error parsing block: {question_content}\nException: {e}")
            continue

    return questions

def quiz_results(request):
    if request.method == 'POST':
        user_answers = {}
        correct_answers = {}
        score = 0
        
        # Retrieve user's answers from POST data
        for key, value in request.POST.items():
            if key.startswith('question') and not key.endswith('_id'):
                question_id = request.POST.get(f'{key}_id')
                user_answers[question_id] = value.upper()  # Convert user answer to uppercase for consistency
        
        # Retrieve correct answers from the database and convert keys to strings
        try:
            questions = Question.objects.filter(id__in=user_answers.keys())
            for question in questions:
                correct_answer = question.correct_answer.strip()  # Ensure correct answer is stripped and in correct format
                correct_answers[str(question.id)] = correct_answer  # Convert question ID to string for consistency
                print(f"Question {question.id}: Correct Answer - {correct_answer}")  # Print correct answer for debugging
        except Question.DoesNotExist:
            return render(request, 'quiz_up_app/generatedquiz.html', {'error': 'Questions not found.'})
        
        # Debugging prints for keys
        print("User Answer Keys:", user_answers.keys())
        print("Correct Answer Keys:", correct_answers.keys())
        
        # Calculate score and print comparisons
        for question_id, user_answer in user_answers.items():
            if question_id in correct_answers:
                correct_answer = correct_answers[question_id].strip()  # Get the correct answer and strip whitespace
                print(f"Question {question_id}: User Answer - {user_answer}, Correct Answer - {correct_answer}")  # Print comparison
                if user_answer == correct_answer:
                    score += 1
            else:
                print(f"Question {question_id}: Correct answer not found in correct_answers dictionary.")
        
        # Prepare context for results
        questions = []
        for question_id, user_answer in user_answers.items():
            question = get_object_or_404(Question, id=question_id)
            questions.append({
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': correct_answers.get(question_id),  # Use correct_answers dict here
            })

        # Save user answers to the session for analysis
        request.session['user_answers'] = user_answers
        
        context = {
            'questions': questions,
            'score': score,
        }
        
        return render(request, 'quiz_up_app/quiz_results.html', context)
    
    # Handle GET request or other cases
    return redirect('generatedquiz')

def get_correct_answer(correct_answer_str):
    try:
        # Attempt to split and extract the correct answer
        correct_answer = correct_answer_str.split(') ', 1)[1].strip()
    except IndexError:
        # Handle cases where splitting fails (e.g., incorrect format in the database)
        correct_answer = "Error: Correct answer format incorrect"
    return correct_answer

def quiz_analysis(request):
    user_data = request.session.get('user', {})
    if not user_data:
        return redirect('signin')  # Redirect to signin if user is not logged in

    user = get_object_or_404(Users, email=user_data['email'])
    user_answers = request.session.get('user_answers', {})

    if not user_answers:
        return render(request, 'quiz_up_app/quiz_analysis.html', {'error': 'No quiz data found.'})

    document_scores = {}

    for question_id, user_answer in user_answers.items():
        question = get_object_or_404(Question, id=question_id)
        document_id = question.document.id

        if document_id not in document_scores:
            document_scores[document_id] = {'correct': 0, 'total': 0, 'document': question.document}
        
        document_scores[document_id]['total'] += 1
        
        if question.correct_answer == user_answer:
            document_scores[document_id]['correct'] += 1

    analysis = []
    total_correct = 0
    total_questions = 0

    current_analyses = []

    for doc_id, data in document_scores.items():
        correct = data['correct']
        total = data['total']
        percentage = round((correct / total) * 100, 2)
        feedback = "Great job! Just review to maintain your knowledge." if percentage >= 75 else "Focus on reviewing this document to improve your knowledge."

        # Save the analysis for each document
        document_analysis = QuizAnalysis.objects.create(
            user=user,
            document=data['document'],
            correct=correct,
            total=total,
            percentage=percentage,
            feedback=feedback
        )

        total_correct += correct
        total_questions += total

        analysis.append({
            'document_title': data['document'].title,
            'correct': correct,
            'total': total,
            'percentage': percentage,
            'feedback': feedback
        })

        # Add the current analysis to the list to associate with the quiz attempt later
        current_analyses.append(document_analysis)

    # Calculate overall performance for the entire quiz
    overall_percentage = round((total_correct / total_questions) * 100, 2)
    overall_feedback = "Excellent overall performance!" if overall_percentage >= 75 else "Consider reviewing the topics to improve your overall performance."

    # Save the overall quiz attempt
    quiz_attempt = QuizAttempt.objects.create(
        user=user,
        title=f"Practice Quiz #{QuizAttempt.objects.filter(user=user).count() + 1}",
        correct=total_correct,
        total=total_questions,
        percentage=overall_percentage,
        feedback=overall_feedback
    )

    # Associate only the current analysis records with the quiz attempt
    quiz_attempt.documents.set(current_analyses)

    context = {
        'analysis': analysis,
        'overall_percentage': overall_percentage,
        'overall_feedback': overall_feedback
    }

    return render(request, 'quiz_up_app/quiz_analysis.html', context)

def quiz_attempt_detail(request, attempt_id):
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    document_analyses = quiz_attempt.documents.all().distinct()  # Ensure uniqueness

    context = {
        'quiz_attempt': quiz_attempt,
        'document_analyses': document_analyses
    }

    return render(request, 'quiz_up_app/quiz_attempt_detail.html', context)