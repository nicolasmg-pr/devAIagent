import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../entities/budget_entity.dart';

abstract class BudgetRepository {
  Future<Either<Failure, BudgetEntity>> createBudget({
    required String categoryId,
    required double amount,
    required int month,
    required int year,
  });
  Future<Either<Failure, BudgetEntity>> updateBudget({
    required String id,
    double? amount,
    int? month,
    int? year,
  });
  Future<Either<Failure, List<BudgetEntity>>> getBudgets({
    int? month,
    int? year,
  });
  Future<Either<Failure, String>> deleteBudget(String id);
}
