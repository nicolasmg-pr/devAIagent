/// Failures para Clean Architecture - Result pattern
import 'package:equatable/equatable.dart';

abstract class Failure extends Equatable {
  final String message;

  const Failure(this.message);

  @override
  List<Object> get props => [message];
}

// General Failures
class ServerFailure extends Failure {
  final int? statusCode;
  const ServerFailure({String message = 'Error en el servidor', this.statusCode})
      : super(message);
}

class CacheFailure extends Failure {
  const CacheFailure([String message = 'Error de caché']) : super(message);
}

class NetworkFailure extends Failure {
  const NetworkFailure([String message = 'Error de conexión a red']) : super(message);
}

class AuthenticationFailure extends Failure {
  const AuthenticationFailure([String message = 'Error de autenticación']) : super(message);
}

class ValidationFailure extends Failure {
  final Map<String, String>? fieldErrors;
  const ValidationFailure({String message = 'Error de validación', this.fieldErrors})
      : super(message);
}

class NotFoundFailure extends Failure {
  const NotFoundFailure([String message = 'Recurso no encontrado']) : super(message);
}

class UnknownFailure extends Failure {
  const UnknownFailure([String message = 'Error desconocido']) : super(message);
}
