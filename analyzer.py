import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

class SupplyChainAnalyzer:
    def __init__(self, data):
        """Initialize with supply chain dataset"""
        self.data = pd.read_csv(data)
        self.product_metrics = None
        self.supplier_metrics = None
        self.logistics_metrics = None

    def analyze_product_performance(self):
        """Analyze product category and SKU performance"""
        self.product_metrics = {
            'category_performance': self.data.groupby('Product type').agg({
                'Revenue generated': 'sum',
                'Number of products sold': 'sum',
                'Stock levels': 'mean',
                'Defect rates': 'mean'
            }).round(2),

            'top_revenue_products': self.data.nlargest(10, 'Revenue generated')[
                ['SKU', 'Product type', 'Revenue generated', 'Number of products sold']
            ],

            'stock_alerts': self.data[self.data['Stock levels'] < 20][
                ['SKU', 'Product type', 'Stock levels', 'Lead times']
            ]
        }

    def analyze_supplier_performance(self):
        """Analyze supplier performance metrics"""
        self.supplier_metrics = {
            'supplier_performance': self.data.groupby('Supplier name').agg({
                'Lead time': 'mean',
                'Manufacturing costs': 'mean',
                'Defect rates': 'mean',
                'Production volumes': 'sum'
            }).round(2),

            'supplier_locations': self.data.groupby(['Supplier name', 'Location']).size().reset_index(
                name='shipment_count'
            ),

            'quality_issues': self.data[self.data['Inspection results'] == 'Fail'][
                ['Supplier name', 'SKU', 'Defect rates']
            ]
        }

    def analyze_logistics(self):
        """Analyze logistics and shipping performance"""
        self.logistics_metrics = {
            'carrier_performance': self.data.groupby('Shipping carriers').agg({
                'Shipping times': 'mean',
                'Shipping costs': 'mean',
                'Number of products sold': 'count'
            }).round(2),

            'transport_cost_analysis': self.data.groupby(['Transportation modes', 'Routes']).agg({
                'Costs': 'mean',
                'Shipping times': 'mean'
            }).round(2),

            'route_efficiency': self.data.groupby('Routes').agg({
                'Shipping times': ['mean', 'min', 'max'],
                'Costs': 'mean'
            }).round(2)
        }

    def get_risk_assessment(self):
        """Assess supply chain risks"""
        risk_factors = pd.DataFrame({
            'SKU': self.data['SKU'],
            'Stock_Risk': self.data['Stock levels'] < 20,
            'Lead_Time_Risk': self.data['Lead time'] > 20,
            'Quality_Risk': self.data['Defect rates'] > 3,
            'Cost_Risk': self.data['Manufacturing costs'] > self.data['Manufacturing costs'].mean()
        })

        risk_factors['Total_Risk_Score'] = (
            risk_factors[['Stock_Risk', 'Lead_Time_Risk', 'Quality_Risk', 'Cost_Risk']]
            .sum(axis=1)
        )

        return risk_factors[risk_factors['Total_Risk_Score'] >= 2]

    def generate_recommendations(self):
        """Generate actionable recommendations"""
        recommendations = []

        # Inventory recommendations
        low_stock = self.data[self.data['Stock levels'] < 20]
        if not low_stock.empty:
            recommendations.append({
                'area': 'Inventory',
                'issue': f'Low stock alerts for {len(low_stock)} SKUs',
                'action': 'Reorder stocks for affected SKUs',
                'priority': 'High'
            })

        # Quality recommendations
        quality_issues = self.data[self.data['Inspection results'] == 'Fail']
        if not quality_issues.empty:
            recommendations.append({
                'area': 'Quality',
                'issue': f'Quality failures in {len(quality_issues)} shipments',
                'action': 'Review supplier quality control processes',
                'priority': 'High'
            })

        # Logistics recommendations
        high_cost_routes = self.data[self.data['Costs'] > self.data['Costs'].mean() + self.data['Costs'].std()]
        if not high_cost_routes.empty:
            recommendations.append({
                'area': 'Logistics',
                'issue': f'High shipping costs on {len(high_cost_routes)} routes',
                'action': 'Evaluate alternative shipping routes or carriers',
                'priority': 'Medium'
            })

        return recommendations

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        summary = {
            'overall_metrics': {
                'Total Revenue': self.data['Revenue generated'].sum(),
                'Total Units Sold': self.data['Number of products sold'].sum(),
                'Average Defect Rate': self.data['Defect rates'].mean(),
                'Average Lead Time': self.data['Lead time'].mean()
            },
            'Product Performance': self.product_metrics if self.product_metrics else None,
            'Supplier Performance': self.supplier_metrics if self.supplier_metrics else None,
            'Logistics Performance': self.logistics_metrics if self.logistics_metrics else None
        }

        return summary

    def export_report_to_pdf(self, report, file_name='summary_report.pdf'):
        """Export the summary report to a PDF file"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Supply Chain Summary Report", ln=True, align='C')
        pdf.ln(10)

        # Write overall metrics
        for key, value in report['overall_metrics'].items():
            pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)

        # Add additional sections if needed
        pdf.ln(10)
        pdf.output(file_name)
        print(f"Report saved to {file_name}")


    def visualize_data(self):
        """Generate visual insights"""
        self.plot_category_performance()
        self.plot_stock_levels()
        self.plot_shipping_cost_density()
        self.plot_shipping_cost_distribution()

    def plot_shipping_costs(self):
        """Scatter plot of shipping costs vs. shipping times"""
        plt.figure(figsize=(8, 6))
        sns.scatterplot(
            data=self.data,
            x='Shipping times',
            y='Shipping costs',
            hue='Transportation modes',
            palette="deep"
        )
        plt.title("Shipping Costs vs. Times by Transportation Mode")
        plt.xlabel("Shipping Times (days)")
        plt.ylabel("Shipping Costs")
        plt.legend(title="Transportation Mode")
        plt.tight_layout()
        plt.show()

    def plot_category_performance(self):
        """Bar chart for revenue generated by product categories"""
        category_data = self.data.groupby('Product type')['Revenue generated'].sum()
        category_data = category_data.sort_values(ascending=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(x=category_data.index, y=category_data.values, palette="viridis")
        plt.title("Revenue by Product Category")
        plt.xlabel("Product Type")
        plt.ylabel("Revenue Generated")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_stock_levels(self):
        """Box plot for stock levels across product categories"""
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.data, x='Product type', y='Stock levels', palette="coolwarm")
        plt.title("Stock Levels by Product Category")
        plt.xlabel("Product Type")
        plt.ylabel("Stock Levels")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_shipping_cost_distribution(self):
        """Box plot of shipping costs by transportation mode"""
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.data, x='Transportation modes', y='Shipping costs', palette="Set3")
        plt.title("Shipping Costs by Transportation Mode")
        plt.xlabel("Transportation Mode")
        plt.ylabel("Shipping Costs")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_shipping_cost_density(self):
        """Density plot of shipping costs by transportation mode"""
        plt.figure(figsize=(10, 6))
        sns.kdeplot(
            data=self.data,
            x='Shipping costs',
            hue='Transportation modes',
            fill=True,
            palette="muted",
            alpha=0.5
        )
        plt.title("Density of Shipping Costs by Transportation Mode")
        plt.xlabel("Shipping Costs")
        plt.ylabel("Density")
        plt.tight_layout()
        plt.show()

