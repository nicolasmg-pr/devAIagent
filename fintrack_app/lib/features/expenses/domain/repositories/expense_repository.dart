import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../entities/expense_entity.dart';

abstract class ExpenseRepository {
  Future<Either<Failure, ExpenseEntity>> createExpense({
    required double amount,
    required String date,
    required String categoryId,
    String? description,
  });
  Future<Either<Failure, ExpensesResponse>> getExpenses({
    int page = 1,
    int limit = 20,
    String? startDate,
    String? endDate,
    String? categoryId,
  });
  Future<Either<Failure, ExpenseEntity>> getExpenseById(String id);
  Future<Either<Failure, ExpenseEntity>> updateExpense({
    required String id,
    double? amount,
    String? date,
    String? categoryId,
    String? description,
  });
  Future<Either<Failure, String>> deleteExpense(String id);
}
