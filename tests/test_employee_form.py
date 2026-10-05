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

    def test_fill_employee_form_details(self, page):

       emp_page = EmployeePage(page)
       emp_page.goto()
       emp_page.fill_employee_form("John Doe", "EMP-1090", "50000", "Junior QA", "Kerala")
       