from django.test import TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from users.models import *

class UserProfileTestCase(TestCase):

    def setUp(self):
        '''
        Create a user with empty profile
        '''
        self.user = User.objects.create_user(username='myTest', password='123456qwerty!')
        self.house = House.objects.create(created_by=self.user, rent=0, deposit=0)
        self.client = Client()

    def test_empty_profile(self):
        '''
        Check if the profile empty
        '''
        user = User.objects.get(username="myTest")
        profile = Profile.objects.get(user=user)
        self.assertEqual(user.username, 'myTest')
        self.assertEqual(profile.bio, '')

    def test_profile_page(self):
        '''
        Test Profile Page of the user rendered correctly
        '''
        self.client.login(username='myTest', password='123456qwerty!')
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        response = self.client.post(
            url, {
                'address': 'Test',
            })
        self.assertTrue(Profile.objects.filter(address='Test').exists())

    def test_house_user(self):
        '''
        Test House Object related with the user
        '''
        user = User.objects.get(username="myTest")
        house = House.objects.get(created_by=user)
        self.assertEqual(house.created_by.username, 'myTest')
        self.assertEqual(house.address, '')


class RenderTestCase(TestCase):
    def setUp(self):
        '''
        Set up Client
        '''
        self.client = Client()

    def test_index_page(self):
        '''
        Test Three main pages rendered correctly
        :return:
        '''
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

        url = reverse('analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis.html')

        url = reverse('explore')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explore.html')



class MySeleniumTests(StaticLiveServerTestCase):
    '''
    Automate Testing
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome('/Users/zwang199/chromedriver')
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_signup(self):
        '''
        Sign up test
        '''
        self.selenium.get('localhost:8000/accounts/signup/')
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('selenium_test_2')
        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys('qwerty!123456')
        password_input2 = self.selenium.find_element_by_name("password2")
        password_input2.send_keys('qwerty!123456')
        self.selenium.find_element_by_xpath("//button[text()='Sign up']").click()


    def test_login(self):
        '''
        Login test
        '''
        self.selenium.get('localhost:8000/accounts/login/')
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('selenium_test_2')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('qwerty!123456')
        self.selenium.find_element_by_xpath("//button[text()='Login']").click()
        self.selenium.implicitly_wait(20)

    def test_update_profile(self):
        '''
        Change Profile test
        '''
        self.selenium.get('localhost:8000/accounts/login/')
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('selenium_test_2')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('qwerty!123456')
        self.selenium.find_element_by_xpath("//button[text()='Login']").click()
        self.selenium.implicitly_wait(20)

        self.selenium.get('localhost:8000/accounts/home/')
        firstname_input = self.selenium.find_element_by_name("first_name")
        firstname_input.send_keys('test first')
        self.selenium.find_element_by_xpath("//button[text()='Save changes']").click()

        self.selenium.implicitly_wait(50)

        self.selenium.get('localhost:8000/accounts/home/')
        first_name = self.selenium.find_element_by_name("first_name")
        self.assertEqual(first_name.get_property('value'), "test first")
        self.selenium.quit()