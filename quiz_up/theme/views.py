from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def change_theme(request):
    if request.method == 'POST':
        if 'is_dark_theme' in request.session:
            request.session['is_dark_theme'] = not request.session['is_dark_theme']
        else:
            request.session['is_dark_theme'] = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return JsonResponse({'status': 'failed'}, status=400)
