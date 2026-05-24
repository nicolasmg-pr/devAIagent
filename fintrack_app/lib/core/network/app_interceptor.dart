import 'package:dio/dio.dart';
import 'dio_client.dart';
import '../errors/exceptions.dart';
import '../../shared/services/storage_service.dart';

class AppInterceptor extends Interceptor {
  final StorageService _storageService;
  
  AppInterceptor(this._storageService);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    try {
      final token = await _storageService.getString('access_token');
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    } catch (e) {
      // If token retrieval fails, continue without token
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.sendTimeout) {
      throw TimeoutException(message: 'La conexión ha terminado. Verifica tu conexión a internet.');
    }
    
    if (err.response?.statusCode == 401) {
      throw AuthenticationException(message: 'Sesión expirada. Inicia sesión nuevamente.');
    }
    
    if (err.response?.statusCode == 404) {
      throw AppException(message: 'El recurso solicitado no existe.');
    }
    
    if (err.response?.statusCode == 500) {
      throw ServerException(message: 'Error en el servidor. Intenta más tarde.');
    }
    
    final errorMessage = err.response?.data['message'] ?? err.response?.data['error'] ?? 'Error desconocido';
    throw AppException(message: errorMessage, statusCode: err.response?.statusCode);
    
    super.onError(err, handler);
  }
}
