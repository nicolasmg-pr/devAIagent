import 'package:equatable/equatable.dart';

/// Stat DTO para estadísticas
class StatDTO extends Equatable {
  final String categoryId;
  final String categoryName;
  final String color;
  final double amount;
  final double percentage;

  const StatDTO({
    required this.categoryId,
    required this.categoryName,
    required this.color,
    required this.amount,
    required this.percentage,
  });

  factory StatDTO.fromJson(Map<String, dynamic> json) {
    return StatDTO(
      categoryId: json['category_id'] as String,
      categoryName: json['category_name'] as String,
      color: json['color'] as String,
      amount: (json['amount'] as num).toDouble(),
      percentage: (json['percentage'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'category_name': categoryName,
      'color': color,
      'amount': amount,
      'percentage': percentage,
    };
  }

  @override
  List<Object?> get props => [categoryId, categoryName, color, amount, percentage];
}

/// Trend DTO para tendencias históricas
class TrendDTO extends Equatable {
  final String month;
  final double amount;

  const TrendDTO({
    required this.month,
    required this.amount,
  });

  factory TrendDTO.fromJson(Map<String, dynamic> json) {
    return TrendDTO(
      month: json['month'] as String,
      amount: (json['amount'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'month': month,
      'amount': amount,
    };
  }

  @override
  List<Object?> get props => [month, amount];
}

/// Response de estadísticas
class StatsResponse {
  final List<StatDTO> currentMonth;
  final List<TrendDTO> historicalTrends;

  StatsResponse({
    required this.currentMonth,
    required this.historicalTrends,
  });

  factory StatsResponse.fromJson(Map<String, dynamic> json) {
    return StatsResponse(
      currentMonth: (json['current_month'] as List)
          .map((e) => StatDTO.fromJson(e as Map<String, dynamic>))
          .toList(),
      historicalTrends: (json['historical_trends'] as List)
          .map((e) => TrendDTO.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'current_month': currentMonth.map((e) => e.toJson()).toList(),
      'historical_trends': historicalTrends.map((e) => e.toJson()).toList(),
    };
  }
}
