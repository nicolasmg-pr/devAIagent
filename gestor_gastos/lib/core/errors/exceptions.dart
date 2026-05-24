/// Excepciones para la capa de datos
import 'package:equatable/equatable.dart';

abstract class ServerException implements Exception {
  final String? message;
  final int? statusCode;

  const ServerException({this.message, this.statusCode});
}

class CacheException implements Exception {
  final String message;
  const CacheException(this.message);
}

class NetworkException implements Exception {
  final String message;
  const NetworkException(this.message);
}

class AuthenticationException implements ServerException {
  final int? statusCode;
  AuthenticationException({String? message, this.statusCode})
      : super(message: message ?? 'Error de autenticación', statusCode: statusCode);
}

class UnauthorizedException implements ServerException {
  final int? statusCode;
  UnauthorizedException({String? message, this.statusCode})
      : super(message: message ?? 'No autorizado', statusCode: statusCode);
}

class NotFoundException implements ServerException {
  final int? statusCode;
  NotFoundException({String? message, this.statusCode})
      : super(message: message ?? 'Recurso no encontrado', statusCode: statusCode);
}

class ValidationException implements ServerException {
  final Map<String, String>? errors;
  ValidationException({this.errors})
      : super(message: 'Error de validación');
}

class ServerExceptionGeneral implements ServerException {
  final int? statusCode;
  final String? message;
  ServerExceptionGeneral({this.statusCode, this.message});
}
