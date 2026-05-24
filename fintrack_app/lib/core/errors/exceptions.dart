class AppException implements Exception {
  final String message;
  final int? statusCode;
  
  AppException({required this.message, this.statusCode});
  
  @override
  String toString() => 'AppException: $message (statusCode: $statusCode)';
}

class NetworkException extends AppException {
  NetworkException({required super.message, super.statusCode});
}

class AuthenticationException extends AppException {
  AuthenticationException({required super.message, super.statusCode});
}

class ServerException extends AppException {
  ServerException({required super.message, super.statusCode});
}

class CacheException extends AppException {
  CacheException({required super.message, super.statusCode});
}

class ValidationException extends AppException {
  ValidationException({required super.message, super.statusCode});
}

class NoDataException extends AppException {
  NoDataException({required super.message, super.statusCode});
}

class TimeoutException extends AppException {
  TimeoutException({required super.message, super.statusCode});
}
