import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../../../core/network/dio_client.dart';
import '../entities/expense_entity.dart';
import '../repositories/expense_repository.dart';

class ExpenseRepositoryImpl implements ExpenseRepository {
  final DioClient dioClient;

  ExpenseRepositoryImpl(this.dioClient);

  @override
  Future<Either<Failure, ExpenseEntity>> createExpense({
    required double amount,
    required String date,
    required String categoryId,
    String? description,
  }) async {
    try {
      final data = <String, dynamic>{
        'amount': amount,
        'date': date,
        'category_id': categoryId,
      };
      if (description != null && description.isNotEmpty) {
        data['description'] = description;
      }

      final response = await dioClient.post<Map<String, dynamic>>(
        '/api/v1/expenses',
        data: data,
      );
      return Right(ExpenseEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, ExpensesResponse>> getExpenses({
    int page = 1,
    int limit = 20,
    String? startDate,
    String? endDate,
    String? categoryId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;
      if (categoryId != null) queryParams['category_id'] = categoryId;

      final response = await dioClient.get<Map<String, dynamic>>(
        '/api/v1/expenses',
        queryParameters: queryParams,
      );
      return Right(ExpensesResponse.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, ExpenseEntity>> getExpenseById(String id) async {
    try {
      final response = await dioClient.get<Map<String, dynamic>>('/api/v1/expenses/$id');
      return Right(ExpenseEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, ExpenseEntity>> updateExpense({
    required String id,
    double? amount,
    String? date,
    String? categoryId,
    String? description,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (amount != null) data['amount'] = amount;
      if (date != null) data['date'] = date;
      if (categoryId != null) data['category_id'] = categoryId;
      if (description != null) data['description'] = description;

      final response = await dioClient.put<Map<String, dynamic>>(
        '/api/v1/expenses/$id',
        data: data,
      );
      return Right(ExpenseEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> deleteExpense(String id) async {
    try {
      await dioClient.delete('/api/v1/expenses/$id');
      return Right('Gasto eliminado exitosamente');
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
}
