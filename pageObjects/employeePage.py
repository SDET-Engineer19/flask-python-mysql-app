

import os

from playwright.sync_api import Page


class EmployeePage:

    def __init__(self, page: Page):
         self.page = page
         self.url = os.getenv('FLASK_URL', 'http://localhost:5000')

    def goto(self):
        """Navigate to employee form"""
        print(f"Navigating to: {self.url}/")
        self.page.goto(f"{self.url}/")
        self.page.wait_for_load_state("networkidle")

    @property
    def emp_name_field(self):
        return self.page.locator('input[name="employee_name"]')

   # employee_id,salary,designation,city

    @property
    def emp_id_field(self):
        return self.page.locator('input[name="employee_id"]')

    @property
    def salary_field(self):
        return self.page.locator('input[name="salary"]')

    @property
    def designation_field(self):
        return self.page.locator('input[name="designation"]')

    @property
    def city_field(self):
        return self.page.locator('input[name="city"]')

    @property
    def submit_button(self):
        return self.page.locator('button[type="submit"]')

    
    @property
    def employee_table(self):
        return self.page.locator('table tbody tr')


    def fill_employee_form(self, employee_name,employee_id, salary, designation, city):
        """Fill the employee form with provided data"""
        self.emp_name_field.fill(employee_name)
        self.emp_id_field.fill(employee_id)
        self.salary_field.fill(salary)
        self.designation_field.fill(designation)
        self.city_field.fill(city)
        self.submit_button.click()
        self.page.wait_for_load_state("networkidle")

    def clear_employee_form(self):
        """Clear the employee form fields"""
        self.emp_name_field.clear()
        self.emp_id_field.clear()
        self.salary_field.clear()
        self.designation_field.clear()
        self.city_field.clear()


    def get_page_title(self) -> str:
        """Get page title"""
        return self.page.title()
