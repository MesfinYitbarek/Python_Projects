import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ExpenseTracker:
    def __init__(self, db_file="expenses.db"):
        self.db_file = db_file
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Education', 'Travel',
            'Personal Care', 'Gifts & Donations', 'Other'
        ]
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month_year TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_expense(self, amount, category, description="", date=None, payment_method="Cash"):
        """Add a new expense"""
        if category not in self.categories:
            print(f"Invalid category! Available categories: {', '.join(self.categories)}")
            return False
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO expenses (amount, category, description, date, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, category, description, date, payment_method))
        
        conn.commit()
        conn.close()
        print(f"Expense of ${amount:.2f} added to '{category}' category!")
        return True
    
    def get_expenses_dataframe(self, start_date=None, end_date=None):
        """Get expenses as pandas DataFrame with optional date filtering"""
        conn = sqlite3.connect(self.db_file)
        
        query = "SELECT * FROM expenses"
        params = []
        
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            query += " WHERE date >= ?"
            params.append(start_date)
        elif end_date:
            query += " WHERE date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            df['year'] = df['date'].dt.year
            df['month_name'] = df['date'].dt.strftime('%B')
            df['day_name'] = df['date'].dt.day_name()
        
        return df
    
    def get_monthly_summary(self, year=None, month=None):
        """Get monthly summary of expenses"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = f"{year}-{month:02d}-01"
        end_date = (datetime(year, month, 1) + relativedelta(months=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        df = self.get_expenses_dataframe(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        summary = df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean'],
            'id': 'count'
        }).round(2)
        
        summary.columns = ['Total Amount', 'Transaction Count', 'Average Amount', 'Total Transactions']
        summary = summary.sort_values('Total Amount', ascending=False)
        
        return summary
    
    def set_budget(self, category, amount, month_year=None):
        """Set monthly budget for a category"""
        if category not in self.categories:
            print(f"Invalid category! Available categories: {', '.join(self.categories)}")
            return False
        
        if month_year is None:
            month_year = datetime.now().strftime('%Y-%m')
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check if budget already exists for this category and month
        cursor.execute('''
            SELECT id FROM budgets 
            WHERE category = ? AND month_year = ?
        ''', (category, month_year))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE budgets SET amount = ? 
                WHERE category = ? AND month_year = ?
            ''', (amount, category, month_year))
        else:
            cursor.execute('''
                INSERT INTO budgets (category, amount, month_year)
                VALUES (?, ?, ?)
            ''', (category, amount, month_year))
        
        conn.commit()
        conn.close()
        print(f"Budget for {category} set to ${amount:.2f} for {month_year}")
        return True
    
    def get_budget_analysis(self, month_year=None):
        """Analyze expenses against budgets"""
        if month_year is None:
            month_year = datetime.now().strftime('%Y-%m')
        
        # Get expenses for the month
        year, month = map(int, month_year.split('-'))
        expenses_summary = self.get_monthly_summary(year, month)
        
        if expenses_summary.empty:
            print("No expenses found for this month!")
            return pd.DataFrame()
        
        # Get budgets for the month
        conn = sqlite3.connect(self.db_file)
        budgets_df = pd.read_sql_query('''
            SELECT category, amount FROM budgets 
            WHERE month_year = ?
        ''', conn, params=[month_year])
        conn.close()
        
        if budgets_df.empty:
            print("No budgets set for this month!")
            return expenses_summary
        
        # Merge expenses with budgets
        analysis = expenses_summary.merge(budgets_df, on='category', how='left')
        analysis['Budget'] = analysis['amount']
        analysis['Amount Spent'] = analysis['Total Amount']
        analysis['Remaining Budget'] = analysis['Budget'] - analysis['Amount Spent']
        analysis['Budget Utilization (%)'] = (analysis['Amount Spent'] / analysis['Budget'] * 100).round(1)
        
        analysis = analysis[['Budget', 'Amount Spent', 'Remaining Budget', 'Budget Utilization (%)', 'Transaction Count']]
        return analysis
    
    def plot_spending_by_category(self, year=None, month=None):
        """Create visualization of spending by category"""
        summary = self.get_monthly_summary(year, month)
        
        if summary.empty:
            print("No data to visualize!")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Pie chart
        plt.subplot(2, 2, 1)
        plt.pie(summary['Total Amount'], labels=summary.index, autopct='%1.1f%%', startangle=90)
        plt.title('Spending Distribution by Category')
        
        # Bar chart
        plt.subplot(2, 2, 2)
        summary['Total Amount'].sort_values().plot(kind='barh')
        plt.title('Spending by Category')
        plt.xlabel('Amount ($)')
        
        # Time series of daily spending
        plt.subplot(2, 2, 3)
        df = self.get_expenses_dataframe()
        if not df.empty:
            daily_spending = df.groupby('date')['amount'].sum()
            daily_spending.plot()
            plt.title('Daily Spending Trend')
            plt.xlabel('Date')
            plt.ylabel('Amount ($)')
            plt.xticks(rotation=45)
        
        # Payment method analysis
        plt.subplot(2, 2, 4)
        payment_methods = df.groupby('payment_method')['amount'].sum()
        payment_methods.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Spending by Payment Method')
        
        plt.tight_layout()
        plt.show()
    
    def plot_budget_vs_actual(self, month_year=None):
        """Plot budget vs actual spending"""
        analysis = self.get_budget_analysis(month_year)
        
        if analysis.empty:
            print("No data for budget analysis!")
            return
        
        plt.figure(figsize=(14, 6))
        
        # Budget vs Actual
        plt.subplot(1, 2, 1)
        categories = analysis.index
        budget_values = analysis['Budget']
        actual_values = analysis['Amount Spent']
        
        x = np.arange(len(categories))
        width = 0.35
        
        plt.bar(x - width/2, budget_values, width, label='Budget', alpha=0.7)
        plt.bar(x + width/2, actual_values, width, label='Actual', alpha=0.7)
        
        plt.xlabel('Categories')
        plt.ylabel('Amount ($)')
        plt.title('Budget vs Actual Spending')
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        
        # Budget utilization
        plt.subplot(1, 2, 2)
        colors = ['green' if x <= 100 else 'red' for x in analysis['Budget Utilization (%)']]
        plt.bar(categories, analysis['Budget Utilization (%)'], color=colors, alpha=0.7)
        plt.axhline(y=100, color='red', linestyle='--', alpha=0.8)
        plt.xlabel('Categories')
        plt.ylabel('Utilization (%)')
        plt.title('Budget Utilization Percentage')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def get_spending_trends(self, months=6):
        """Analyze spending trends over time"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        df = self.get_expenses_dataframe(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if df.empty:
            print("No data for trend analysis!")
            return
        
        # Monthly trends
        monthly_trends = df.groupby('month').agg({
            'amount': ['sum', 'count'],
            'id': 'count'
        }).round(2)
        
        monthly_trends.columns = ['Total Amount', 'Transaction Count', 'Total Transactions']
        
        # Category trends
        category_monthly = pd.pivot_table(
            df, 
            values='amount', 
            index='month', 
            columns='category', 
            aggfunc='sum'
        ).fillna(0)
        
        return monthly_trends, category_monthly
    
    def export_to_excel(self, filename="expense_report.xlsx"):
        """Export expense data to Excel with multiple sheets"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Raw data
            df = self.get_expenses_dataframe()
            if not df.empty:
                df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Monthly summary
            summary = self.get_monthly_summary()
            if not summary.empty:
                summary.to_excel(writer, sheet_name='Monthly Summary')
            
            # Budget analysis
            budget_analysis = self.get_budget_analysis()
            if not budget_analysis.empty:
                budget_analysis.to_excel(writer, sheet_name='Budget Analysis')
            
            # Trends
            trends, category_trends = self.get_spending_trends()
            if not trends.empty:
                trends.to_excel(writer, sheet_name='Monthly Trends')
                category_trends.to_excel(writer, sheet_name='Category Trends')
        
        print(f"Data exported to {filename} successfully!")
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Expense ID {expense_id} deleted successfully!")
        else:
            print(f"Expense ID {expense_id} not found!")
        
        conn.close()

def main():
    tracker = ExpenseTracker()
    
    while True:
        print("\n=== Personal Expense Tracker ===")
        print("1. Add New Expense")
        print("2. View Monthly Summary")
        print("3. Set Monthly Budget")
        print("4. Budget vs Actual Analysis")
        print("5. View Spending Charts")
        print("6. Analyze Spending Trends")
        print("7. Export to Excel")
        print("8. View All Expenses")
        print("9. Delete Expense")
        print("10. Exit")
        
        choice = input("\nChoose an option (1-10): ").strip()
        
        if choice == '1':
            print("\nAdd New Expense:")
            amount = float(input("Amount: $"))
            print("\nAvailable Categories:")
            for i, category in enumerate(tracker.categories, 1):
                print(f"{i}. {category}")
            
            cat_choice = int(input("Select category (number): ")) - 1
            if 0 <= cat_choice < len(tracker.categories):
                category = tracker.categories[cat_choice]
                description = input("Description (optional): ")
                payment_method = input("Payment method (default: Cash): ") or "Cash"
                
                tracker.add_expense(amount, category, description, payment_method=payment_method)
            else:
                print("Invalid category selection!")
        
        elif choice == '2':
            year = input("Year (YYYY) or press enter for current year: ")
            month = input("Month (1-12) or press enter for current month: ")
            
            year = int(year) if year else None
            month = int(month) if month else None
            
            summary = tracker.get_monthly_summary(year, month)
            if not summary.empty:
                print("\nMonthly Expense Summary:")
                print("=" * 50)
                print(summary)
                print(f"\nTotal Spending: ${summary['Total Amount'].sum():.2f}")
            else:
                print("No expenses found for the specified period!")
        
        elif choice == '3':
            print("\nSet Monthly Budget:")
            print("Available Categories:")
            for i, category in enumerate(tracker.categories, 1):
                print(f"{i}. {category}")
            
            cat_choice = int(input("Select category (number): ")) - 1
            if 0 <= cat_choice < len(tracker.categories):
                category = tracker.categories[cat_choice]
                amount = float(input("Budget amount: $"))
                month_year = input("Month-Year (YYYY-MM) or press enter for current: ") or None
                
                tracker.set_budget(category, amount, month_year)
            else:
                print("Invalid category selection!")
        
        elif choice == '4':
            month_year = input("Month-Year (YYYY-MM) or press enter for current: ") or None
            analysis = tracker.get_budget_analysis(month_year)
            if not analysis.empty:
                print("\nBudget vs Actual Analysis:")
                print("=" * 60)
                print(analysis)
                tracker.plot_budget_vs_actual(month_year)
            else:
                print("No data available for analysis!")
        
        elif choice == '5':
            year = input("Year (YYYY) or press enter for current year: ")
            month = input("Month (1-12) or press enter for current month: ")
            
            year = int(year) if year else None
            month = int(month) if month else None
            
            tracker.plot_spending_by_category(year, month)
        
        elif choice == '6':
            months = int(input("Number of months to analyze (default 6): ") or 6)
            trends, category_trends = tracker.get_spending_trends(months)
            
            if not trends.empty:
                print("\nSpending Trends (Last {} months):".format(months))
                print("=" * 40)
                print(trends)
                
                # Plot trends
                plt.figure(figsize=(12, 8))
                trends['Total Amount'].plot(kind='line', marker='o')
                plt.title('Monthly Spending Trend')
                plt.xlabel('Month')
                plt.ylabel('Amount ($)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.show()
        
        elif choice == '7':
            filename = input("Export filename (default: expense_report.xlsx): ") or "expense_report.xlsx"
            tracker.export_to_excel(filename)
        
        elif choice == '8':
            df = tracker.get_expenses_dataframe()
            if not df.empty:
                print("\nAll Expenses:")
                print("=" * 80)
                # Display only recent expenses for readability
                recent_expenses = df.head(20)[['id', 'date', 'category', 'amount', 'description', 'payment_method']]
                print(recent_expenses.to_string(index=False))
                if len(df) > 20:
                    print(f"\n... and {len(df) - 20} more expenses")
            else:
                print("No expenses found!")
        
        elif choice == '9':
            expense_id = input("Enter expense ID to delete: ")
            if expense_id.isdigit():
                tracker.delete_expense(int(expense_id))
            else:
                print("Invalid expense ID!")
        
        elif choice == '10':
            print("Goodbye! Keep tracking your expenses!")
            break
        
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    # Install required packages first:
    # pip install pandas matplotlib seaborn python-dateutil openpyxl
    main()