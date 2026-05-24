import 'package:dio/dio.dart';
import '../network/dio_client.dart';
import '../network/app_interceptor.dart';
import '../constants/app_constants.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  static ApiService get instance => _instance;
  
  late final Dio _dio;
  final StorageService _storageService = StorageService.instance;
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal() {
    _dio = DioClient().dio;
    _dio.interceptors.add(AppInterceptor(_storageService));
  }
  
  // Auth Endpoints
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dio.post(
        '/api/v1/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        await _storageService.saveAccessToken(data['access_token']);
        await _storageService.saveRefreshToken(data['refresh_token']);
        return data;
      }
      
      throw Exception('Error en la autenticación');
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error de conexión');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/auth/register',
        data: {
          'name': name,
          'email': email,
          'password': password,
        },
      );
      
      if (response.statusCode == 201) {
        return response.data;
      }
      
      throw Exception('Error en el registro');
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error de conexión');
      }
      rethrow;
    }
  }
  
  // Expenses Endpoints
  Future<Map<String, dynamic>> createExpense({
    required String categoryId,
    required double amount,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/expenses',
        data: {
          'category_id': categoryId,
          'amount': amount,
          'description': description,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al crear el gasto');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getExpenses({
    int page = 1,
    int limit = AppConstants.defaultPageSize,
    String? search,
    String? categoryId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParameters = {
        'page': page,
        'limit': limit,
      };
      
      if (search != null && search.isNotEmpty) {
        queryParameters['search'] = search;
      }
      if (categoryId != null && categoryId.isNotEmpty) {
        queryParameters['category_id'] = categoryId;
      }
      if (startDate != null) {
        queryParameters['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParameters['end_date'] = endDate.toIso8601String();
      }
      
      final response = await _dio.get(
        '/api/v1/expenses',
        queryParameters: queryParameters,
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener gastos');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getExpenseById(String id) async {
    try {
      final response = await _dio.get('/api/v1/expenses/$id');
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener el gasto');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> updateExpense({
    required String id,
    required String categoryId,
    required double amount,
    String? description,
  }) async {
    try {
      final response = await _dio.put(
        '/api/v1/expenses/$id',
        data: {
          'category_id': categoryId,
          'amount': amount,
          'description': description,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al actualizar el gasto');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> deleteExpense(String id) async {
    try {
      final response = await _dio.delete('/api/v1/expenses/$id');
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al eliminar el gasto');
      }
      rethrow;
    }
  }
  
  // Categories Endpoints
  Future<List<dynamic>> getCategories() async {
    try {
      final response = await _dio.get('/api/v1/categories');
      return List<dynamic>.from(response.data['data']);
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener categorías');
      }
      rethrow;
    }
  }
  
  // Statistics Endpoints
  Future<Map<String, dynamic>> getMonthlyStatistics({
    required int month,
    required int year,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/statistics/monthly',
        queryParameters: {
          'month': month,
          'year': year,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener estadísticas');
      }
      rethrow;
    }
  }
  
  // Budgets Endpoints
  Future<Map<String, dynamic>> createBudget({
    required String categoryId,
    required double monthlyLimit,
    required String periodStart,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/budgets',
        data: {
          'category_id': categoryId,
          'monthly_limit': monthlyLimit,
          'period_start': periodStart,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al crear presupuesto');
      }
      rethrow;
    }
  }
  
  Future<List<dynamic>> getBudgets() async {
    try {
      final response = await _dio.get('/api/v1/budgets');
      return List<dynamic>.from(response.data['data']);
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener presupuestos');
      }
      rethrow;
    }
  }
  
  // Alerts Endpoints
  Future<Map<String, dynamic>> getAlertPreferences() async {
    try {
      final response = await _dio.get('/api/v1/alerts/preferences');
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al obtener preferencias de alerta');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> updateAlertPreferences({
    required int thresholdPercentage,
    required bool isEnabled,
  }) async {
    try {
      final response = await _dio.put(
        '/api/v1/alerts/preferences',
        data: {
          'threshold_percentage': thresholdPercentage,
          'is_enabled': isEnabled,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al actualizar preferencias de alerta');
      }
      rethrow;
    }
  }
  
  // Export Endpoints
  Future<Map<String, dynamic>> exportToCsv({
    required int month,
    required int year,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/export/csv',
        data: {
          'month': month,
          'year': year,
        },
      );
      
      return response.data;
    } catch (e) {
      if (e is DioException) {
        throw Exception(e.response?.data['message'] ?? 'Error al iniciar exportación');
      }
      rethrow;
    }
  }
}
