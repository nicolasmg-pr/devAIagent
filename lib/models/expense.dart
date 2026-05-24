class Expense {
  final String id;
  final double amount;
  final String date;
  final String description;
  final String categoryId;

  Expense({
    required this.id,
    required this.amount,
    required this.date,
    required this.description,
    required this.categoryId,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'],
      amount: double.parse(json['amount'].toString()),
      date: json['date'],
      description: json['description'],
      categoryId: json['categoryId'],
    );
  }
}