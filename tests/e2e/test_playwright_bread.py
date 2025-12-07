import pytest
import time
from playwright.sync_api import Page, expect


class TestCalculationsBREAD:
    """End-to-end tests for all BREAD operations on calculations."""

    @pytest.fixture(autouse=True)
    def setup_user_and_login(self, page: Page, fastapi_server: str):
        """Set up a test user and log in before each test."""
        self.base_url = fastapi_server.rstrip("/")
        
        # Register a test user
        self.test_user = {
            "first_name": "Test",
            "last_name": "User", 
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        # Navigate to register page and create user
        page.goto(f"{self.base_url}/register")
        page.fill("input[name='first_name']", self.test_user["first_name"])
        page.fill("input[name='last_name']", self.test_user["last_name"])
        page.fill("input[name='email']", self.test_user["email"])
        page.fill("input[name='username']", self.test_user["username"])
        page.fill("input[name='password']", self.test_user["password"])
        page.fill("input[name='confirm_password']", self.test_user["confirm_password"])
        page.click("button[type='submit']")
        
        # Navigate to login page and log in
        page.goto(f"{self.base_url}/login")
        page.fill("input[name='username']", self.test_user["username"])
        page.fill("input[name='password']", self.test_user["password"])
        page.click("button[type='submit']")
        
        # Wait for dashboard to load
        page.wait_for_url(f"{self.base_url}/dashboard")
        
    def test_add_calculation_positive_scenarios(self, page: Page):
        """Test creating calculations (positive scenarios)."""
        
        # Test addition
        page.select_option("#calcType", "addition")
        page.fill("#calcInputs", "5, 10, 15")
        page.click("button[type='submit']")
        
        # Wait for success message
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("#successMessage")).to_contain_text("Calculation created successfully")
        
        # Verify calculation appears in table
        expect(page.locator("tbody tr")).to_have_count(1)
        expect(page.locator("tbody tr").first).to_contain_text("addition")
        expect(page.locator("tbody tr").first).to_contain_text("5, 10, 15")
        expect(page.locator("tbody tr").first).to_contain_text("30")
        
        # Test subtraction
        page.select_option("#calcType", "subtraction")
        page.fill("#calcInputs", "20, 5, 3")
        page.click("button[type='submit']")
        
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("tbody tr")).to_have_count(2)
        
        # Test multiplication
        page.select_option("#calcType", "multiplication")
        page.fill("#calcInputs", "2, 3, 4")
        page.click("button[type='submit']")
        
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("tbody tr")).to_have_count(3)
        
        # Test division
        page.select_option("#calcType", "division")
        page.fill("#calcInputs", "100, 5, 2")
        page.click("button[type='submit']")
        
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("tbody tr")).to_have_count(4)

    def test_add_calculation_negative_scenarios(self, page: Page):
        """Test creating calculations with invalid inputs."""
        
        # Test with less than 2 numbers
        page.select_option("#calcType", "addition")
        page.fill("#calcInputs", "5")
        page.click("button[type='submit']")
        
        expect(page.locator("#errorAlert")).to_be_visible()
        expect(page.locator("#errorMessage")).to_contain_text("at least two valid numbers")
        
        # Test with non-numeric input
        page.fill("#calcInputs", "5, abc, 10")
        page.click("button[type='submit']")
        
        expect(page.locator("#errorAlert")).to_be_visible()
        
        # Test division by zero
        page.select_option("#calcType", "division")
        page.fill("#calcInputs", "10, 0")
        page.click("button[type='submit']")
        
        expect(page.locator("#errorAlert")).to_be_visible()
        expect(page.locator("#errorMessage")).to_contain_text("Cannot divide by zero")

    def test_browse_calculations(self, page: Page):
        """Test browsing/listing calculations."""
        
        # Create multiple calculations first
        calculations = [
            ("addition", "1, 2, 3"),
            ("subtraction", "10, 3"),
            ("multiplication", "4, 5"),
            ("division", "20, 4")
        ]
        
        for calc_type, inputs in calculations:
            page.select_option("#calcType", calc_type)
            page.fill("#calcInputs", inputs)
            page.click("button[type='submit']")
            page.wait_for_selector("#successAlert:not(.hidden)")
            time.sleep(0.5)  # Brief pause between calculations
        
        # Verify all calculations are displayed
        expect(page.locator("tbody tr")).to_have_count(4)
        
        # Verify table headers
        expect(page.locator("th")).to_contain_text(["Type", "Inputs", "Result", "Date", "Actions"])
        
        # Verify each calculation appears correctly
        rows = page.locator("tbody tr")
        expect(rows.nth(0)).to_contain_text("addition")
        expect(rows.nth(1)).to_contain_text("subtraction")  
        expect(rows.nth(2)).to_contain_text("multiplication")
        expect(rows.nth(3)).to_contain_text("division")

    def test_edit_calculation(self, page: Page):
        """Test editing existing calculations."""
        
        # Create a calculation first
        page.select_option("#calcType", "addition")
        page.fill("#calcInputs", "5, 10")
        page.click("button[type='submit']")
        page.wait_for_selector("#successAlert:not(.hidden)")
        
        # Click edit button
        page.click("button.edit-calc")
        
        # Verify edit modal opens
        expect(page.locator("#editModal")).not_to_have_class("hidden")
        
        # Verify form is pre-populated
        expect(page.locator("#editCalcType")).to_have_value("addition")
        expect(page.locator("#editCalcInputs")).to_have_value("5,10")
        
        # Modify the inputs
        page.fill("#editCalcInputs", "5, 10, 15, 20")
        page.click("#editCalculationForm button[type='submit']")
        
        # Verify success message
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("#successMessage")).to_contain_text("updated successfully")
        
        # Verify modal closes
        expect(page.locator("#editModal")).to_have_class("hidden")
        
        # Verify calculation is updated in table
        expect(page.locator("tbody tr").first).to_contain_text("5, 10, 15, 20")
        expect(page.locator("tbody tr").first).to_contain_text("50")  # New result

    def test_edit_calculation_validation(self, page: Page):
        """Test edit validation."""
        
        # Create a calculation first
        page.select_option("#calcType", "addition")
        page.fill("#calcInputs", "5, 10")
        page.click("button[type='submit']")
        page.wait_for_selector("#successAlert:not(.hidden)")
        
        # Click edit button
        page.click("button.edit-calc")
        
        # Test invalid inputs
        page.fill("#editCalcInputs", "5")  # Less than 2 numbers
        page.click("#editCalculationForm button[type='submit']")
        
        expect(page.locator("#errorAlert")).to_be_visible()
        expect(page.locator("#errorMessage")).to_contain_text("at least two valid numbers")

    def test_delete_calculation(self, page: Page):
        """Test deleting calculations."""
        
        # Create multiple calculations
        calculations = [("addition", "1, 2"), ("subtraction", "10, 3")]
        
        for calc_type, inputs in calculations:
            page.select_option("#calcType", calc_type)
            page.fill("#calcInputs", inputs)
            page.click("button[type='submit']")
            page.wait_for_selector("#successAlert:not(.hidden)")
            time.sleep(0.5)
        
        # Verify we have 2 calculations
        expect(page.locator("tbody tr")).to_have_count(2)
        
        # Mock the confirmation dialog to always return true
        page.evaluate("() => window.confirm = () => true")
        
        # Delete first calculation
        page.click("button.delete-calc")
        
        # Verify success message
        expect(page.locator("#successAlert")).to_be_visible()
        expect(page.locator("#successMessage")).to_contain_text("deleted successfully")
        
        # Verify calculation is removed
        expect(page.locator("tbody tr")).to_have_count(1)

    def test_read_specific_calculation(self, page: Page):
        """Test reading specific calculation details."""
        
        # Create a calculation
        page.select_option("#calcType", "multiplication")
        page.fill("#calcInputs", "3, 4, 5")
        page.click("button[type='submit']")
        page.wait_for_selector("#successAlert:not(.hidden)")
        
        # Verify calculation details are displayed in table
        calculation_row = page.locator("tbody tr").first
        expect(calculation_row).to_contain_text("multiplication")
        expect(calculation_row).to_contain_text("3, 4, 5")
        expect(calculation_row).to_contain_text("60")  # 3 * 4 * 5 = 60
        
        # Verify date is displayed
        expect(calculation_row.locator("td").nth(3)).not_to_be_empty()

    def test_unauthorized_access_redirects(self, page: Page):
        """Test that unauthorized access redirects to login."""
        
        # Clear localStorage to simulate logout
        page.evaluate("() => localStorage.clear()")
        
        # Try to access dashboard directly
        page.goto(f"{self.base_url}/dashboard")
        
        # Should be redirected to login page
        expect(page).to_have_url(f"{self.base_url}/login")

    def test_modal_cancel_functionality(self, page: Page):
        """Test edit modal cancel functionality."""
        
        # Create a calculation first
        page.select_option("#calcType", "addition")
        page.fill("#calcInputs", "5, 10")
        page.click("button[type='submit']")
        page.wait_for_selector("#successAlert:not(.hidden)")
        
        # Open edit modal
        page.click("button.edit-calc")
        expect(page.locator("#editModal")).not_to_have_class("hidden")
        
        # Test cancel button
        page.click("#cancelEdit")
        expect(page.locator("#editModal")).to_have_class("hidden")
        
        # Open modal again
        page.click("button.edit-calc")
        
        # Test clicking outside modal
        page.locator("#editModal").click()
        expect(page.locator("#editModal")).to_have_class("hidden")

    def test_logout_functionality(self, page: Page):
        """Test logout functionality."""
        
        # Mock the confirmation dialog to return true
        page.evaluate("() => window.confirm = () => true")
        
        # Click logout button
        page.click("#logoutBtn")
        
        # Should be redirected to login page
        expect(page).to_have_url(f"{self.base_url}/login")
        
        # Try to access dashboard - should redirect back to login
        page.goto(f"{self.base_url}/dashboard")
        expect(page).to_have_url(f"{self.base_url}/login")

    def test_empty_calculations_message(self, page: Page):
        """Test empty state message when no calculations exist."""
        
        # Should show empty state message
        expect(page.locator("tbody td")).to_contain_text("No calculations found")