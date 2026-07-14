from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ACTIVITY_CHOICES = [
        ('SED', 'Sedentary (Little or no exercise)'),
        ('LIG', 'Lightly Active (Exercise 1-3 days/week)'),
        ('MOD', 'Moderately Active (Exercise 3-5 days/week)'),
        ('ACT', 'Very Active (Exercise 6-7 days/week)'),
        ('EXT', 'Extra Active (Physical job or heavy exercise)'),
    ]
    
    GOAL_CHOICES = [
        ('LOSE', 'Lose Weight'),
        ('MAINTAIN', 'Maintain Weight'),
        ('GAIN', 'Gain Weight/Muscle'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm")
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Target weight in kg")
    activity_level = models.CharField(max_length=3, choices=ACTIVITY_CHOICES, default='SED')
    fitness_goal = models.CharField(max_length=8, choices=GOAL_CHOICES, default='MAINTAIN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.weight}kg on {self.date}"


class FoodLog(models.Model):
    MEAL_CHOICES = [
        ('BF', 'Breakfast'),
        ('LH', 'Lunch'),
        ('DN', 'Dinner'),
        ('SK', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    food_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, help_text="Protein in grams")
    carbs = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, help_text="Carbohydrates in grams")
    fats = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, help_text="Fats in grams")
    meal_type = models.CharField(max_length=2, choices=MEAL_CHOICES, default='BF')
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.user.username} - {self.food_name} ({self.calories} kcal) on {self.date}"


class ExerciseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_logs')
    activity_name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()
    calories_burned = models.PositiveIntegerField()
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.activity_name} ({self.calories_burned} kcal) on {self.date}"


class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_logs')
    amount_ml = models.PositiveIntegerField(help_text="Water amount in ml")
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.amount_ml}ml on {self.date}"
