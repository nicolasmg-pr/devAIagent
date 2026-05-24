import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../../../core/network/dio_client.dart';
import '../repositories/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final DioClient dioClient;

  AuthRepositoryImpl(this.dioClient);

  @override
  Future<Either<Failure, Map<String, dynamic>>> login(String email, String password) async {
    try {
      final response = await dioClient.post<Map<String, dynamic>>(
        '/api/v1/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      return Right(response);
    } catch (e) {
      return Left(AuthenticationFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> register({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      final response = await dioClient.post<Map<String, dynamic>>(
        '/api/v1/auth/register',
        data: {
          'full_name': name,
          'email': email,
          'password': password,
        },
      );

      return Right(response);
    } catch (e) {
      return Left(AuthenticationFailure(message: e.toString()));
    }
  }

  @override
  Future<void> logout() async {
    await dioClient.logout();
  }

  @override
  Future<bool> isLoggedIn() async {
    return await dioClient.hasAccessToken();
  }

  @override
  Future<String?> getAccessToken() async {
    return await dioClient.getAccessToken();
  }
}
