from .models import *

def user_quiz_analyses(request):
    user_data = request.session.get('user', {})
    if user_data:
        user_email = user_data.get('email')
        if user_email:
            attempts = QuizAttempt.objects.filter(user__email=user_email).order_by('-created_at')
            return {'user_quiz_attempts': attempts}
    return {'user_quiz_attempts': None}   