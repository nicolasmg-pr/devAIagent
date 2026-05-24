import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../../../core/network/dio_client.dart';
import '../entities/category_entity.dart';
import '../repositories/category_repository.dart';

class CategoryRepositoryImpl implements CategoryRepository {
  final DioClient dioClient;

  CategoryRepositoryImpl(this.dioClient);

  @override
  Future<Either<Failure, List<CategoryEntity>>> getCategories() async {
    try {
      final response = await dioClient.get<Map<String, dynamic>>('/api/v1/categories');
      final categories = (response['categories'] as List)
          .map((json) => CategoryEntity.fromJson(json as Map<String, dynamic>))
          .toList();
      return Right(categories);
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, CategoryEntity>> createCategory({
    required String name,
    required String color,
  }) async {
    try {
      final response = await dioClient.post<Map<String, dynamic>>(
        '/api/v1/categories',
        data: {
          'name': name,
          'color': color,
        },
      );
      return Right(CategoryEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, CategoryEntity>> updateCategory({
    required String id,
    String? name,
    String? color,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (name != null) data['name'] = name;
      if (color != null) data['color'] = color;

      final response = await dioClient.put<Map<String, dynamic>>(
        '/api/v1/categories/$id',
        data: data,
      );
      return Right(CategoryEntity.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> deleteCategory(String id) async {
    try {
      await dioClient.delete('/api/v1/categories/$id');
      return Right('Categoria eliminada exitosamente');
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
}
