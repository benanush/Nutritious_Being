from django.contrib import admin
from .models import UserProfile, WeightLog, FoodLog, ExerciseLog, WaterLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'age', 'height', 'current_weight', 'target_weight', 'activity_level', 'fitness_goal')
    search_fields = ('user__username', 'user__email')

@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)

@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_name', 'calories', 'protein', 'carbs', 'fats', 'meal_type', 'date')
    list_filter = ('date', 'meal_type', 'user')
    search_fields = ('food_name', 'user__username')

@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_name', 'duration_minutes', 'calories_burned', 'date')
    list_filter = ('date', 'user')
    search_fields = ('activity_name', 'user__username')

@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_ml', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
