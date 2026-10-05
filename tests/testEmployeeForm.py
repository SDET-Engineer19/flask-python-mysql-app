from pageObjects.employeePage import EmployeePage


class TestEmployeeForm:

    def test_employee_form_fields(self, page):
      emp_page = EmployeePage(page)
      emp_page.goto()

      assert emp_page.emp_name_field.is_visible(), "Employee Name field is not visible"
      assert emp_page.emp_id_field.is_visible(), "Employee ID field is not visible"
      assert emp_page.salary_field.is_visible(), "Salary field is not visible"
      assert emp_page.designation_field.is_visible(), "Designation field is not visible"
      assert emp_page.city_field.is_visible(), "City field is not visible" 
      assert emp_page.submit_button.is_visible(), "Submit button is not visible" 
