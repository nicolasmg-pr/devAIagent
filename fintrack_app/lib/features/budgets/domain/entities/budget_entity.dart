import 'package:equatable/equatable.dart';

/// Budget Entity
class BudgetEntity extends Equatable {
  final String id;
  final String categoryId;
  final double amount;
  final int month;
  final int year;

  const BudgetEntity({
    required this.id,
    required this.categoryId,
    required this.amount,
    required this.month,
    required this.year,
  });

  factory BudgetEntity.fromJson(Map<String, dynamic> json) {
    return BudgetEntity(
      id: json['id'] as String,
      categoryId: json['category_id'] as String,
      amount: (json['amount'] as num).toDouble(),
      month: json['month'] as int,
      year: json['year'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'category_id': categoryId,
      'amount': amount,
      'month': month,
      'year': year,
    };
  }

  BudgetEntity copyWith({
    String? id,
    String? categoryId,
    double? amount,
    int? month,
    int? year,
  }) {
    return BudgetEntity(
      id: id ?? this.id,
      categoryId: categoryId ?? this.categoryId,
      amount: amount ?? this.amount,
      month: month ?? this.month,
      year: year ?? this.year,
    );
  }

  @override
  List<Object?> get props => [id, categoryId, amount, month, year];
}
