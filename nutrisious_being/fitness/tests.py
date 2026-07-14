from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, WeightLog, FoodLog, ExerciseLog, WaterLog
from .utils import calculate_bmi, calculate_bmr, calculate_tdee, calculate_targets

class FitnessCalculatorsTestCase(TestCase):
    def test_calculate_bmi(self):
        # BMI = weight / (height/100)^2
        # For 70kg, 175cm: 70 / (1.75^2) = 22.857 -> round to 22.9
        bmi, category = calculate_bmi(70, 175)
        self.assertEqual(bmi, 22.9)
        self.assertEqual(category, "Normal")
        
        # Test overweight
        bmi, category = calculate_bmi(85, 175)
        self.assertEqual(bmi, 27.8)
        self.assertEqual(category, "Overweight")

    def test_calculate_bmr(self):
        # Male BMR = 10 * W + 6.25 * H - 5 * A + 5
        # 10*70 + 6.25*175 - 5*25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75 -> 1674
        bmr = calculate_bmr('M', 70, 175, 25)
        self.assertEqual(bmr, 1674)
        
        # Female BMR = 10 * W + 6.25 * H - 5 * A - 161
        # 10*60 + 6.25*160 - 5*30 - 161 = 600 + 1000 - 150 - 161 = 1289
        bmr = calculate_bmr('F', 60, 160, 30)
        self.assertEqual(bmr, 1289)

    def test_calculate_tdee(self):
        # BMR 1500, Moderately Active (1.55) -> 1500 * 1.55 = 2325
        tdee = calculate_tdee(1500, 'MOD')
        self.assertEqual(tdee, 2325)

    def test_calculate_targets(self):
        # Maintain goal: target_calories = TDEE
        targets = calculate_targets(2000, 'MAINTAIN')
        self.assertEqual(targets['calories'], 2000)
        # Protein: 25% of 2000 = 500 kcal / 4 = 125g
        self.assertEqual(targets['protein'], 125)
        
        # Lose goal: target_calories = TDEE - 500
        targets = calculate_targets(2000, 'LOSE')
        self.assertEqual(targets['calories'], 1500)
        # Protein: 30% of 1500 = 450 kcal / 4 = 112.5 -> banker's rounding to 112g
        self.assertEqual(targets['protein'], 112)


class AccessControlTestCase(TestCase):
    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_redirects_unauthenticated(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
