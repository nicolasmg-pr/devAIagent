/// Cliente Dio configurado para la aplicación
import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import '../../constants/app_constants.dart';
import '../services/storage_service.dart';
import 'app_interceptor.dart';

class DioClient {
  static late DioClient _instance;
  late Dio _dio;
  late StorageService _storageService;

  factory DioClient() {
    return _instance;
  }

  factory DioClient.init({StorageService? storageService}) {
    _instance = DioClient._internal(storageService: storageService ?? StorageService());
    return _instance;
  }

  DioClient._internal({StorageService? storageService}) {
    _storageService = storageService ?? StorageService();
    
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.fullBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      responseType: ResponseType.json,
    ));

    // Interceptors
    _dio.interceptors.add(AuthInterceptor(_storageService));
    _dio.interceptors.add(PrettyDioLogger(
      requestHeader: true,
      requestBody: true,
      responseHeader: false,
      error: true,
      compact: true,
    ));
  }

  Dio get dio => _dio;

  // Auth Endpoints
  Future<dynamic> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final response = await _dio.post(
      AppConstants.authRegister,
      data: {
        'email': email,
        'password': password,
        'full_name': fullName,
      },
    );
    return response.data;
  }

  Future<dynamic> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      AppConstants.authLogin,
      data: {
        'email': email,
        'password': password,
      },
    );
    return response.data;
  }

  // Expenses Endpoints
  Future<dynamic> createExpense({
    required String categoryId,
    required double amount,
    required String expenseDate,
    String? description,
  }) async {
    final response = await _dio.post(
      AppConstants.expenses,
      data: {
        'categoryId': categoryId,
        'amount': amount,
        'expenseDate': expenseDate,
        if (description != null) 'description': description,
      },
    );
    return response.data;
  }

  Future<dynamic> getExpenses({
    int page = 1,
    int limit = 20,
    String? startDate,
    String? endDate,
    String? categoryId,
  }) async {
    final response = await _dio.get(
      AppConstants.expenses,
      queryParameters: {
        'page': page,
        'limit': limit,
        if (startDate != null) 'startDate': startDate,
        if (endDate != null) 'endDate': endDate,
        if (categoryId != null) 'categoryId': categoryId,
      },
    );
    return response.data;
  }

  Future<dynamic> getExpenseById(String id) async {
    final response = await _dio.get('${AppConstants.expenses}/$id');
    return response.data;
  }

  Future<dynamic> updateExpense({
    required String id,
    required double amount,
    required String expenseDate,
    required String categoryId,
    String? description,
  }) async {
    final response = await _dio.put(
      '${AppConstants.expenses}/$id',
      data: {
        'amount': amount,
        'expenseDate': expenseDate,
        'categoryId': categoryId,
        if (description != null) 'description': description,
      },
    );
    return response.data;
  }

  Future<dynamic> deleteExpense(String id) async {
    final response = await _dio.delete('${AppConstants.expenses}/$id');
    return response.data;
  }

  Future<dynamic> getStatistics({
    String? period,
  }) async {
    final response = await _dio.get(
      AppConstants.expensesStatistics,
      queryParameters: {
        if (period != null) 'period': period,
      },
    );
    return response.data;
  }

  // Budgets Endpoints
  Future<dynamic> createBudget({
    required String categoryId,
    required double limitAmount,
    double thresholdPercentage = 80.0,
  }) async {
    final response = await _dio.post(
      AppConstants.budgets,
      data: {
        'categoryId': categoryId,
        'limitAmount': limitAmount,
        'thresholdPercentage': thresholdPercentage,
      },
    );
    return response.data;
  }

  Future<dynamic> getBudgets() async {
    final response = await _dio.get(AppConstants.budgets);
    return response.data;
  }

  Future<dynamic> updateBudget({
    required String id,
    required double limitAmount,
    double thresholdPercentage = 80.0,
  }) async {
    final response = await _dio.put(
      '${AppConstants.budgets}/$id',
      data: {
        'limitAmount': limitAmount,
        'thresholdPercentage': thresholdPercentage,
      },
    );
    return response.data;
  }

  // Categories Endpoints
  Future<dynamic> createCategory({
    required String name,
    String? iconUrl,
  }) async {
    final response = await _dio.post(
      AppConstants.categories,
      data: {
        'name': name,
        if (iconUrl != null) 'iconUrl': iconUrl,
      },
    );
    return response.data;
  }

  Future<dynamic> deleteCategory(String id) async {
    final response = await _dio.delete('${AppConstants.categories}/$id');
    return response.data;
  }
}
