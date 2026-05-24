import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';

abstract class AuthRepository {
  Future<Either<Failure, Map<String, dynamic>>> login(String email, String password);
  Future<Either<Failure, Map<String, dynamic>>> register({
    required String name,
    required String email,
    required String password,
  });
  Future<void> logout();
  Future<bool> isLoggedIn();
  Future<String?> getAccessToken();
}
