import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../repositories/budget_repository.dart';
import '../entities/budget_entity.dart';

class CreateBudgetUseCase {
  final BudgetRepository _repository;

  CreateBudgetUseCase(this._repository);

  Future<Either<Failure, BudgetEntity>> call({
    required String categoryId,
    required double amount,
    required int month,
    required int year,
  }) async {
    return await _repository.createBudget(
      categoryId: categoryId,
      amount: amount,
      month: month,
      year: year,
    );
  }
}

class GetBudgetsUseCase {
  final BudgetRepository _repository;

  GetBudgetsUseCase(this._repository);

  Future<Either<Failure, List<BudgetEntity>>> call({
    int? month,
    int? year,
  }) async {
    return await _repository.getBudgets(
      month: month,
      year: year,
    );
  }
}

class UpdateBudgetUseCase {
  final BudgetRepository _repository;

  UpdateBudgetUseCase(this._repository);

  Future<Either<Failure, BudgetEntity>> call({
    required String id,
    double? amount,
    int? month,
    int? year,
  }) async {
    return await _repository.updateBudget(
      id: id,
      amount: amount,
      month: month,
      year: year,
    );
  }
}

class DeleteBudgetUseCase {
  final BudgetRepository _repository;

  DeleteBudgetUseCase(this._repository);

  Future<Either<Failure, String>> call(String id) async {
    return await _repository.deleteBudget(id);
  }
}
