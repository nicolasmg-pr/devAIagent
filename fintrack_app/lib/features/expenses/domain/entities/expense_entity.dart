import 'package:equatable/equatable.dart';

/// Expense Entity
class ExpenseEntity extends Equatable {
  final String id;
  final double amount;
  final String description;
  final DateTime date;
  final String categoryId;
  final DateTime createdAt;

  const ExpenseEntity({
    required this.id,
    required this.amount,
    this.description = '',
    required this.date,
    required this.categoryId,
    required this.createdAt,
  });

  factory ExpenseEntity.fromJson(Map<String, dynamic> json) {
    return ExpenseEntity(
      id: json['id'] as String,
      amount: (json['amount'] as num).toDouble(),
      description: json['description'] as String? ?? '',
      date: DateTime.parse(json['date'] as String),
      categoryId: json['category_id'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'amount': amount,
      'description': description,
      'date': date.toIso8601String(),
      'category_id': categoryId,
      'created_at': createdAt.toIso8601String(),
    };
  }

  ExpenseEntity copyWith({
    String? id,
    double? amount,
    String? description,
    DateTime? date,
    String? categoryId,
    DateTime? createdAt,
  }) {
    return ExpenseEntity(
      id: id ?? this.id,
      amount: amount ?? this.amount,
      description: description ?? this.description,
      date: date ?? this.date,
      categoryId: categoryId ?? this.categoryId,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [id, amount, description, date, categoryId];
}

/// Response paginado para expenses
class ExpensesResponse {
  final List<ExpenseEntity> expenses;
  final int total;
  final int page;
  final int limit;

  ExpensesResponse({
    required this.expenses,
    required this.total,
    required this.page,
    required this.limit,
  });

  factory ExpensesResponse.fromJson(Map<String, dynamic> json) {
    return ExpensesResponse(
      expenses: (json['expenses'] as List)
          .map((e) => ExpenseEntity.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int,
      page: json['page'] as int,
      limit: json['limit'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'expenses': expenses.map((e) => e.toJson()).toList(),
      'total': total,
      'page': page,
      'limit': limit,
    };
  }
}
