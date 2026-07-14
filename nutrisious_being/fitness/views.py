from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile, WeightLog, FoodLog, ExerciseLog, WaterLog
from .forms import UserRegistrationForm, UserProfileForm, FoodLogForm, ExerciseLogForm, WaterLogForm, WeightLogForm
from .utils import calculate_bmi, calculate_bmr, calculate_tdee, calculate_targets

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Nutrisious Being, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please check the form fields.")
    else:
        form = UserRegistrationForm()
    return render(request, 'fitness/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'fitness/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    user = request.user
    
    # Try to fetch user profile, create one with default values if not exists
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Fallback profile setup if user is created through django-admin command without profile
        profile = UserProfile.objects.create(
            user=user,
            gender='M',
            age=25,
            height=175.0,
            current_weight=70.0,
            target_weight=70.0,
            activity_level='SED',
            fitness_goal='MAINTAIN'
        )
        WeightLog.objects.get_or_create(user=user, weight=70.0, date=timezone.localdate())

    today = timezone.localdate()
    
    # 1. Health Calculations
    bmi, bmi_category = calculate_bmi(profile.current_weight, profile.height)
    bmr = calculate_bmr(profile.gender, profile.current_weight, profile.height, profile.age)
    tdee = calculate_tdee(bmr, profile.activity_level)
    targets = calculate_targets(tdee, profile.fitness_goal)
    
    # 2. Daily Consumed Nutrition
    today_foods = FoodLog.objects.filter(user=user, date=today)
    today_calories = today_foods.aggregate(Sum('calories'))['calories__sum'] or 0
    today_protein = today_foods.aggregate(Sum('protein'))['protein__sum'] or 0
    today_carbs = today_foods.aggregate(Sum('carbs'))['carbs__sum'] or 0
    today_fats = today_foods.aggregate(Sum('fats'))['fats__sum'] or 0
    
    # 3. Daily Exercises Burned
    today_exercises = ExerciseLog.objects.filter(user=user, date=today)
    today_burned = today_exercises.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    
    # 4. Daily Water Consumed
    today_water_sum = WaterLog.objects.filter(user=user, date=today).aggregate(Sum('amount_ml'))['amount_ml__sum'] or 0
    
    # 5. Remaining Calorie Budget
    # Remaining = Target Calories - Consumed + Burned
    remaining_calories = targets['calories'] - today_calories + today_burned
    
    # Calorie Progress Percentage
    calorie_progress_pct = 0
    if targets['calories'] > 0:
        calorie_progress_pct = min(round((today_calories / targets['calories']) * 100), 100)
        
    # Macro Percentages for Progress Rings
    protein_progress_pct = min(round((float(today_protein) / targets['protein']) * 100), 100) if targets['protein'] > 0 else 0
    carbs_progress_pct = min(round((float(today_carbs) / targets['carbs']) * 100), 100) if targets['carbs'] > 0 else 0
    fats_progress_pct = min(round((float(today_fats) / targets['fats']) * 100), 100) if targets['fats'] > 0 else 0
    
    # Water Progress Percentage (Daily target standard: 2500ml)
    water_target = 2500
    water_progress_pct = min(round((today_water_sum / water_target) * 100), 100)

    # 6. Weight History (for chart display, last 7 logs chronologically)
    weight_logs = WeightLog.objects.filter(user=user).order_by('date')[:7]
    weight_dates = [log.date.strftime('%m-%d') for log in weight_logs]
    weight_values = [float(log.weight) for log in weight_logs]

    # Quick log forms
    water_form = WaterLogForm()
    weight_form = WeightLogForm()

    context = {
        'profile': profile,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'bmr': bmr,
        'tdee': tdee,
        'targets': targets,
        'today_calories': today_calories,
        'today_protein': today_protein,
        'today_carbs': today_carbs,
        'today_fats': today_fats,
        'today_burned': today_burned,
        'today_water_sum': today_water_sum,
        'water_target': water_target,
        'remaining_calories': remaining_calories,
        'calorie_progress_pct': calorie_progress_pct,
        'protein_progress_pct': protein_progress_pct,
        'carbs_progress_pct': carbs_progress_pct,
        'fats_progress_pct': fats_progress_pct,
        'water_progress_pct': water_progress_pct,
        'weight_dates': weight_dates,
        'weight_values': weight_values,
        'water_form': water_form,
        'weight_form': weight_form,
    }
    return render(request, 'fitness/dashboard.html', context)


@login_required
def food_log_view(request):
    user = request.user
    today = timezone.localdate()
    
    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.user = user
            food_item.save()
            messages.success(request, f"Logged {food_item.food_name} successfully!")
            return redirect('food_log')
    else:
        form = FoodLogForm()
        
    # Get all logs grouped by today vs past logs
    today_logs = FoodLog.objects.filter(user=user, date=today)
    past_logs = FoodLog.objects.filter(user=user).exclude(date=today)[:30]
    
    # Summarize nutrition totals
    today_calories = today_logs.aggregate(Sum('calories'))['calories__sum'] or 0
    today_protein = today_logs.aggregate(Sum('protein'))['protein__sum'] or 0
    today_carbs = today_logs.aggregate(Sum('carbs'))['carbs__sum'] or 0
    today_fats = today_logs.aggregate(Sum('fats'))['fats__sum'] or 0

    return render(request, 'fitness/food_log.html', {
        'form': form,
        'today_logs': today_logs,
        'past_logs': past_logs,
        'today_calories': today_calories,
        'today_protein': today_protein,
        'today_carbs': today_carbs,
        'today_fats': today_fats,
    })


@login_required
def delete_food_view(request, pk):
    food_log = get_object_or_404(FoodLog, pk=pk, user=request.user)
    name = food_log.food_name
    food_log.delete()
    messages.info(request, f"Removed food log: {name}")
    return redirect('food_log')


@login_required
def exercise_log_view(request):
    user = request.user
    today = timezone.localdate()
    
    if request.method == 'POST':
        form = ExerciseLogForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = user
            exercise.save()
            messages.success(request, f"Logged exercise: {exercise.activity_name}!")
            return redirect('exercise_log')
    else:
        form = ExerciseLogForm()
        
    today_logs = ExerciseLog.objects.filter(user=user, date=today)
    past_logs = ExerciseLog.objects.filter(user=user).exclude(date=today)[:30]
    
    today_burned = today_logs.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    today_duration = today_logs.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0

    return render(request, 'fitness/exercise_log.html', {
        'form': form,
        'today_logs': today_logs,
        'past_logs': past_logs,
        'today_burned': today_burned,
        'today_duration': today_duration,
    })


@login_required
def delete_exercise_view(request, pk):
    exercise = get_object_or_404(ExerciseLog, pk=pk, user=request.user)
    name = exercise.activity_name
    exercise.delete()
    messages.info(request, f"Removed exercise log: {name}")
    return redirect('exercise_log')


@login_required
def quick_add_water_view(request):
    if request.method == 'POST':
        user = request.user
        amount = int(request.POST.get('amount_ml', 250))
        # Log the water for today
        WaterLog.objects.create(user=user, amount_ml=amount, date=timezone.localdate())
        messages.success(request, f"Added {amount}ml of water!")
    return redirect('dashboard')


@login_required
def weight_log_view(request):
    user = request.user
    if request.method == 'POST':
        form = WeightLogForm(request.POST)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.user = user
            new_log.save()
            
            # Check if this is the newest weight log and update user profile current_weight if so
            latest_log = WeightLog.objects.filter(user=user).order_by('-date', '-id').first()
            if latest_log and latest_log == new_log:
                profile = user.profile
                profile.current_weight = new_log.weight
                profile.save()
                
            messages.success(request, f"Logged weight: {new_log.weight} kg!")
            return redirect('dashboard')
    return redirect('dashboard')


@login_required
def delete_weight_view(request, pk):
    weight_log = get_object_or_404(WeightLog, pk=pk, user=request.user)
    weight_val = weight_log.weight
    weight_log.delete()
    
    # Update profile weight to the next latest log
    latest_log = WeightLog.objects.filter(user=request.user).order_by('-date', '-id').first()
    if latest_log:
        profile = request.user.profile
        profile.current_weight = latest_log.weight
        profile.save()
        
    messages.info(request, f"Deleted weight log: {weight_val} kg")
    return redirect('dashboard')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            updated_profile = form.save()
            
            # Add a weight log for today if it doesn't already exist or if current_weight changed
            today = timezone.localdate()
            existing_log = WeightLog.objects.filter(user=user, date=today).first()
            if existing_log:
                existing_log.weight = updated_profile.current_weight
                existing_log.save()
            else:
                WeightLog.objects.create(user=user, weight=updated_profile.current_weight, date=today)
                
            messages.success(request, "Fitness profile updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update profile. Please verify your fields.")
    else:
        form = UserProfileForm(instance=profile)
        
    # Get all weight history for showing in a table inside profile tab
    weight_history = WeightLog.objects.filter(user=user).order_by('-date')[:30]
    
    return render(request, 'fitness/profile.html', {
        'form': form,
        'weight_history': weight_history
    })
