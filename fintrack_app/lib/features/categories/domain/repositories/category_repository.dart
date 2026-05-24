import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../entities/category_entity.dart';

abstract class CategoryRepository {
  Future<Either<Failure, List<CategoryEntity>>> getCategories();
  Future<Either<Failure, CategoryEntity>> createCategory({
    required String name,
    required String color,
  });
  Future<Either<Failure, CategoryEntity>> updateCategory({
    required String id,
    String? name,
    String? color,
  });
  Future<Either<Failure, String>> deleteCategory(String id);
}
