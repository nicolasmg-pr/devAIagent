import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../repositories/auth_repository.dart';

class RegisterUseCase {
  final AuthRepository _repository;

  RegisterUseCase(this._repository);

  Future<Either<Failure, Map<String, dynamic>>> call({
    required String name,
    required String email,
    required String password,
  }) async {
    return await _repository.register(
      name: name,
      email: email,
      password: password,
    );
  }
}
