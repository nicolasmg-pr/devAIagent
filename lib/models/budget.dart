class Budget {
  final String id;
  final String categoryId;
  final double monthlyLimit;
  final int alertThreshold;

  Budget({
    required this.id,
    required this.categoryId,
    required this.monthlyLimit,
    required this.alertThreshold,
  });

  factory Budget.fromJson(Map<String, dynamic> json) {
    return Budget(
      id: json['id'],
      categoryId: json['categoryId'],
      monthlyLimit: double.parse(json['monthlyLimit'].toString()),
      alertThreshold: json['alertThreshold'],
    );
  }
}