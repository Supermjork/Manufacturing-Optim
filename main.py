from analyzer import SupplyChainAnalyzer

data_path = "data/supply_chain_data.csv"

my_analyzer = SupplyChainAnalyzer(data_path)

my_analyzer.analyze_logistics()

my_analyzer.analyze_product_performance()

my_analyzer.analyze_supplier_performance()

my_analyzer.generate_recommendations()

my_analyzer.get_risk_assessment()

my_analyzer.visualize_data()

report = my_analyzer.generate_summary_report()

print(report)
