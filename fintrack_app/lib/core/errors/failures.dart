abstract class Failure {
  final String message;
  
  Failure(this.message);
}

class NetworkFailure extends Failure {
  NetworkFailure({required super.message});
}

class AuthenticationFailure extends Failure {
  AuthenticationFailure({required super.message});
}

class ServerFailure extends Failure {
  ServerFailure({required super.message});
}

class CacheFailure extends Failure {
  CacheFailure({required super.message});
}

class ValidationFailure extends Failure {
  ValidationFailure({required super.message});
}

class TimeoutFailure extends Failure {
  TimeoutFailure({required super.message});
}
