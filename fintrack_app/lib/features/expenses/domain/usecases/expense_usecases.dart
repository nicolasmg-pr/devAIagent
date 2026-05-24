import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../repositories/expense_repository.dart';
import '../entities/expense_entity.dart';

class CreateExpenseUseCase {
  final ExpenseRepository _repository;

  CreateExpenseUseCase(this._repository);

  Future<Either<Failure, ExpenseEntity>> call({
    required double amount,
    required String date,
    required String categoryId,
    String? description,
  }) async {
    return await _repository.createExpense(
      amount: amount,
      date: date,
      categoryId: categoryId,
      description: description,
    );
  }
}

class GetExpensesUseCase {
  final ExpenseRepository _repository;

  GetExpensesUseCase(this._repository);

  Future<Either<Failure, ExpensesResponse>> call({
    int page = 1,
    int limit = 20,
    String? startDate,
    String? endDate,
    String? categoryId,
  }) async {
    return await _repository.getExpenses(
      page: page,
      limit: limit,
      startDate: startDate,
      endDate: endDate,
      categoryId: categoryId,
    );
  }
}

class GetExpenseByIdUseCase {
  final ExpenseRepository _repository;

  GetExpenseByIdUseCase(this._repository);

  Future<Either<Failure, ExpenseEntity>> call(String id) async {
    return await _repository.getExpenseById(id);
  }
}

class UpdateExpenseUseCase {
  final ExpenseRepository _repository;

  UpdateExpenseUseCase(this._repository);

  Future<Either<Failure, ExpenseEntity>> call({
    required String id,
    double? amount,
    String? date,
    String? categoryId,
    String? description,
  }) async {
    return await _repository.updateExpense(
      id: id,
      amount: amount,
      date: date,
      categoryId: categoryId,
      description: description,
    );
  }
}

class DeleteExpenseUseCase {
  final ExpenseRepository _repository;

  DeleteExpenseUseCase(this._repository);

  Future<Either<Failure, String>> call(String id) async {
    return await _repository.deleteExpense(id);
  }
}
