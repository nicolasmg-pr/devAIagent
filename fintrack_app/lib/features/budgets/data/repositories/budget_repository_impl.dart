import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../../../core/network/dio_client.dart';
import '../entities/budget_entity.dart';
import '../repositories/budget_repository.dart';

class BudgetRepositoryImpl implements BudgetRepository {
  final DioClient dioClient;

  BudgetRepositoryImpl(this.dioClient);

  @override
  Future<Either<Failure, BudgetEntity>> createBudget({
    required String categoryId,
    required double amount,
    required int month,
    required int year,
  }) async {
    try {
      final response = await dioClient.post<Map<String, dynamic>>(
        '/api/v1/budgets',
        data: {
          'category_id': categoryId,
          'amount': amount,
          'month': month,
          'year': year,
        },
      );
      return Right(BudgetEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, BudgetEntity>> updateBudget({
    required String id,
    double? amount,
    int? month,
    int? year,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (amount != null) data['amount'] = amount;
      if (month != null) data['month'] = month;
      if (year != null) data['year'] = year;

      final response = await dioClient.put<Map<String, dynamic>>(
        '/api/v1/budgets/$id',
        data: data,
      );
      return Right(BudgetEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<BudgetEntity>>> getBudgets({
    int? month,
    int? year,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (month != null) queryParams['month'] = month;
      if (year != null) queryParams['year'] = year;

      final response = await dioClient.get<Map<String, dynamic>>(
        '/api/v1/budgets',
        queryParameters: queryParams,
      );

      final budgets = (response['budgets'] as List)
          .map((json) => BudgetEntity.fromJson(json as Map<String, dynamic>))
          .toList();
      return Right(budgets);
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> deleteBudget(String id) async {
    try {
      await dioClient.delete('/api/v1/budgets/$id');
      return Right('Presupuesto eliminado exitosamente');
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
}
