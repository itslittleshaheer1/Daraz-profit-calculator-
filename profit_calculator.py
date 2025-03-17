from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import requests

class ProfitCalculator(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background Image
        self.bg = Image(source="/storage/emulated/0/Pydroid3/myapps/download.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)

        # Main Container
        self.container = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint=(0.9, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self.container)

        # Steps for Input
        self.steps = [
            ("Enter Purchase Price per Product (PKR):", "purchase_price"),
            ("Enter Number of Products Purchased:", "products_purchased"),
            ("Enter Selling Price per Product (PKR):", "selling_price"),
            ("Enter Number of Products Sold:", "products_sold"),
            ("Enter Flyers Purchased:", "flyers_count"),
            ("Enter Flyers Purchase Cost (PKR):", "flyers_cost"),
            ("Enter Paper Purchased:", "paper_count"),
            ("Enter Paper Purchase Cost (PKR):", "paper_cost"),
            ("Is Shipping Free? (Yes/No):", "shipping_free"),
            ("Enter Free Shipping Amount (PKR) (if applicable):", "shipping_cost")
        ]

        self.current_step = 0
        self.values = {}

        # Step Label
        self.label = Label(text=self.steps[self.current_step][0], font_size=18, bold=True, color=(1, 0, 0, 1))
        self.container.add_widget(self.label)

        # Input Field (Rounded)
        self.input_field = TextInput(multiline=False, font_size=18, background_color=(1, 1, 1, 1), foreground_color=(1, 0, 0, 1), halign="center")
        self.input_field.background_normal = ''
        self.input_field.background_down = ''
        self.input_field.border = (15, 15, 15, 15)
        self.container.add_widget(self.input_field)

        # Next Button (Rounded)
        self.next_button = Button(text="Next", font_size=18, background_color=(0.2, 0.6, 1, 1))
        self.next_button.border = (15, 15, 15, 15)
        self.next_button.bind(on_press=self.next_step)
        self.container.add_widget(self.next_button)

        # Calculate Button (Initially Disabled)
        self.calculate_btn = Button(text="Calculate Profit", font_size=18, background_color=(0, 1, 0, 1))
        self.calculate_btn.border = (15, 15, 15, 15)
        self.calculate_btn.bind(on_press=self.calculate_profit)
        self.calculate_btn.disabled = True
        self.container.add_widget(self.calculate_btn)

        # Result Label
        self.result_label = Label(text="", font_size=20, bold=True, color=(1, 0, 0, 1))  # Red Text
        self.container.add_widget(self.result_label)

    def next_step(self, instance):
        field_name = self.steps[self.current_step][1]
        self.values[field_name] = self.input_field.text.strip()

        if field_name == "shipping_free":
            if self.values[field_name].lower() not in ["yes", "no"]:
                self.result_label.text = "Please enter Yes or No!"
                return

        # Special Case: Skip "Enter Shipping Cost" if user selects "No"
        if field_name == "shipping_free" and self.values[field_name].lower() == "no":
            self.current_step += 1  # Skip next question

        self.current_step += 1
        if self.current_step < len(self.steps):
            self.label.text = self.steps[self.current_step][0]
            self.input_field.text = ""
        else:
            self.next_button.disabled = True
            self.calculate_btn.disabled = False

    def fetch_daraz_fees(self):
        try:
            response = requests.get("https://api.daraz.com.pk/fees")  # Replace with actual API URL
            data = response.json()
            return data.get("commission_rate", 0.10), data.get("handling_fee", 0.0125), data.get("tax_rate", 0.05)
        except:
            return 0.10, 0.0125, 0.05  

    def calculate_profit(self, instance):
        try:
            purchase_price = float(self.values["purchase_price"])
            products_purchased = int(self.values["products_purchased"])
            selling_price = float(self.values["selling_price"])
            products_sold = int(self.values["products_sold"])

            flyers_cost = float(self.values["flyers_cost"])
            paper_cost = float(self.values["paper_cost"])

            shipping_free = self.values["shipping_free"].lower()
            shipping_cost = float(self.values["shipping_cost"]) if shipping_free == "yes" else 0

            commission_rate, handling_fee, tax_rate = self.fetch_daraz_fees()

            total_revenue = selling_price * products_sold
            total_purchase_cost = purchase_price * products_purchased
            total_shipping_cost = shipping_cost * products_sold

            total_commission = (selling_price * commission_rate) * products_sold
            total_handling_fee = (selling_price * handling_fee) * products_sold
            total_tax = (selling_price * tax_rate) * products_sold

            total_expenses = total_purchase_cost + flyers_cost + paper_cost + total_shipping_cost + total_commission + total_handling_fee + total_tax
            net_profit = total_revenue - total_expenses

            self.result_label.text = f"[b]Total Revenue:[/b] {total_revenue:.2f} PKR\n" \
                                     f"[b]Total Costs:[/b] {total_expenses:.2f} PKR\n" \
                                     f"[b]Net Profit:[/b] {net_profit:.2f} PKR"
        except Exception as e:
            self.result_label.text = f"Error: {str(e)}\nPlease enter valid numbers!"

class ProfitApp(App):
    def build(self):
        return ProfitCalculator()

if __name__ == "__main__":
    ProfitApp().run()