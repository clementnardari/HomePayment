from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)

class HomeLoan:
    def __init__(self, principal, down_payment, annual_interest_rate, loan_term, annual_property_tax, annual_home_insurance, annual_hoa_fees):
        self.principal = principal - down_payment
        self.down_payment = down_payment
        self.annual_interest_rate = annual_interest_rate
        self.loan_term = loan_term
        self.annual_property_tax = annual_property_tax
        self.annual_home_insurance = annual_home_insurance
        self.annual_hoa_fees = annual_hoa_fees

    def calculate_monthly_interest_rate(self):
        return self.annual_interest_rate / 12 / 100

    def calculate_monthly_property_tax(self):
        return self.annual_property_tax / 12

    def calculate_monthly_home_insurance(self):
        return self.annual_home_insurance / 12

    def calculate_monthly_hoa_fees(self):
        return self.annual_hoa_fees / 12

    def calculate_monthly_mortgage_payment(self):
        monthly_interest_rate = self.calculate_monthly_interest_rate()
        term_in_months = self.loan_term * 12
        if monthly_interest_rate == 0:
            return self.principal / term_in_months
        else:
            return self.principal * monthly_interest_rate * (1 + monthly_interest_rate)**term_in_months / ((1 + monthly_interest_rate)**term_in_months - 1)

    def calculate_total_monthly_payment(self):
        monthly_property_tax = self.calculate_monthly_property_tax()
        monthly_home_insurance = self.calculate_monthly_home_insurance()
        monthly_hoa_fees = self.calculate_monthly_hoa_fees()
        monthly_mortgage_payment = self.calculate_monthly_mortgage_payment()

        return monthly_mortgage_payment + monthly_property_tax + monthly_home_insurance + monthly_hoa_fees

    def plot_balance_and_cumulative_interest(self):
        fig, ax = plt.subplots()
        
        years = list(range(1, self.loan_term + 1))
        remaining_balance = []
        cumulative_interest_paid = []
        monthly_interest_rate = self.calculate_monthly_interest_rate()
        term_in_months = self.loan_term * 12
        monthly_mortgage_payment = self.calculate_monthly_mortgage_payment()

        for year in years:
            remaining_balance_year = self.principal * ((1 + monthly_interest_rate)**(term_in_months) - (1 + monthly_interest_rate)**(year * 12)) / ((1 + monthly_interest_rate)**term_in_months - 1)
            remaining_balance.append(remaining_balance_year)

            interest_paid_year = (monthly_mortgage_payment * year * 12) - (self.principal - remaining_balance_year)
            cumulative_interest_paid.append(interest_paid_year)

        ax.plot(years, remaining_balance, label="Remaining Balance")
        ax.plot(years, cumulative_interest_paid, label="Cumulative Interest Paid")
        ax.set_xlabel("Years")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Remaining Loan Balance and Cumulative Interest Paid Over Time")
        ax.legend()
        ax.grid()

        return fig

    def plot_yearly_interest(self):
        fig, ax = plt.subplots()

        years = list(range(1, self.loan_term + 1))
        cumulative_interest_paid = []
        yearly_interest_paid = []
        yearly_mortgage_payment = []
        monthly_interest_rate = self.calculate_monthly_interest_rate()
        term_in_months = self.loan_term * 12
        monthly_mortgage_payment = self.calculate_monthly_mortgage_payment()

        for year in years:
            remaining_balance_year = self.principal * ((1 + monthly_interest_rate)**(term_in_months) - (1 + monthly_interest_rate)**(year * 12)) / ((1 + monthly_interest_rate)**term_in_months - 1)
            interest_paid_year = (monthly_mortgage_payment * year * 12) - (self.principal - remaining_balance_year)
            cumulative_interest_paid.append(interest_paid_year)
            yearly_mortgage_payment.append(monthly_mortgage_payment*12)
            if year == 1:
                yearly_interest_paid.append(interest_paid_year)
            else:
                yearly_interest_paid.append(interest_paid_year - cumulative_interest_paid[year - 2])

        ax.plot(years, yearly_interest_paid, label="Yearly Interest Paid")
        ax.plot(years, yearly_mortgage_payment, label="Yearly Paid")
        ax.set_xlabel("Years")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Yearly Interest Paid Over Time")
        ax.legend()
        ax.grid()

        return fig

@app.route('/', methods=['GET', 'POST'])
def loan_form():
    if request.method == 'POST':
        principal = float(request.form['principal'])
        down_payment = float(request.form['down_payment'])
        annual_interest_rate = float(request.form['annual_interest_rate'])
        loan_term = int(request.form['loan_term'])
        annual_property_tax = float(request.form['annual_property_tax'])
        annual_home_insurance = float(request.form['annual_home_insurance'])
        annual_hoa_fees = float(request.form['annual_hoa_fees'])

        loan = HomeLoan(principal, down_payment, annual_interest_rate, loan_term, annual_property_tax, annual_home_insurance, annual_hoa_fees)
        total_monthly_payment = loan.calculate_total_monthly_payment()

        plot1, plot2 = loan.plot_balance_and_cumulative_interest(), loan.plot_yearly_interest()

        # Save your plots with unique names
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        plot1_path = f"static/plot1_{timestamp}.png"
        plot2_path = f"static/plot2_{timestamp}.png"
        plot1.savefig(plot1_path)
        plot2.savefig(plot2_path)

        # Close the plot figures
        plt.close(plot1)
        plt.close(plot2)

        return render_template('loan_form.html', total_monthly_payment=total_monthly_payment, plot1_path=plot1_path, plot2_path=plot2_path)

    return render_template('loan_form.html', total_monthly_payment=None, plot1_path=None, plot2_path=None)

if __name__ == '__main__':
    app.run(debug=True)