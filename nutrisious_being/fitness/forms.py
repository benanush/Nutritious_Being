from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, WeightLog, FoodLog, ExerciseLog, WaterLog
from django.utils import timezone

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    age = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'placeholder': 'Age'}))
    height = forms.DecimalField(max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Height (cm)'}))
    current_weight = forms.DecimalField(max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Current Weight (kg)'}))
    target_weight = forms.DecimalField(max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Target Weight (kg)'}))
    activity_level = forms.ChoiceField(choices=UserProfile.ACTIVITY_CHOICES, initial='SED')
    fitness_goal = forms.ChoiceField(choices=UserProfile.GOAL_CHOICES, initial='MAINTAIN')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.create(
                user=user,
                gender=self.cleaned_data['gender'],
                age=self.cleaned_data['age'],
                height=self.cleaned_data['height'],
                current_weight=self.cleaned_data['current_weight'],
                target_weight=self.cleaned_data['target_weight'],
                activity_level=self.cleaned_data['activity_level'],
                fitness_goal=self.cleaned_data['fitness_goal']
            )
            # Create an initial weight log
            WeightLog.objects.create(
                user=user,
                weight=self.cleaned_data['current_weight'],
                date=timezone.localdate()
            )
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'age', 'height', 'current_weight', 'target_weight', 'activity_level', 'fitness_goal']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'current_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'target_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'activity_level': forms.Select(attrs={'class': 'form-control'}),
            'fitness_goal': forms.Select(attrs={'class': 'form-control'}),
        }


class FoodLogForm(forms.ModelForm):
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    class Meta:
        model = FoodLog
        fields = ['food_name', 'calories', 'protein', 'carbs', 'fats', 'meal_type', 'date']
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Oatmeal'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 250'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 40'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }


class ExerciseLogForm(forms.ModelForm):
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    class Meta:
        model = ExerciseLog
        fields = ['activity_name', 'duration_minutes', 'calories_burned', 'date']
        widgets = {
            'activity_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Running'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 30'}),
            'calories_burned': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 300'}),
        }


class WaterLogForm(forms.ModelForm):
    class Meta:
        model = WaterLog
        fields = ['amount_ml']
        widgets = {
            'amount_ml': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 250'}),
        }


class WeightLogForm(forms.ModelForm):
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    class Meta:
        model = WeightLog
        fields = ['weight', 'date']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g., 75.5'}),
        }
