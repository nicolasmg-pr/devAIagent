import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../repositories/category_repository.dart';
import '../entities/category_entity.dart';

class GetCategoriesUseCase {
  final CategoryRepository _repository;

  GetCategoriesUseCase(this._repository);

  Future<Either<Failure, List<CategoryEntity>>> call() async {
    return await _repository.getCategories();
  }
}

class CreateCategoryUseCase {
  final CategoryRepository _repository;

  CreateCategoryUseCase(this._repository);

  Future<Either<Failure, CategoryEntity>> call({
    required String name,
    required String color,
  }) async {
    return await _repository.createCategory(
      name: name,
      color: color,
    );
  }
}

class UpdateCategoryUseCase {
  final CategoryRepository _repository;

  UpdateCategoryUseCase(this._repository);

  Future<Either<Failure, CategoryEntity>> call({
    required String id,
    String? name,
    String? color,
  }) async {
    return await _repository.updateCategory(
      id: id,
      name: name,
      color: color,
    );
  }
}

class DeleteCategoryUseCase {
  final CategoryRepository _repository;

  DeleteCategoryUseCase(this._repository);

  Future<Either<Failure, String>> call(String id) async {
    return await _repository.deleteCategory(id);
  }
}
