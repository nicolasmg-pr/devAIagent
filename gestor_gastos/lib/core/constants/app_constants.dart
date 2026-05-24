/// Constantes de la aplicación
class AppConstants {
  AppConstants._();

  // API Configuration
  static const String baseUrl = 'http://localhost:3000';
  static const String apiVersion = '/api/v1';
  static const String fullBaseUrl = '$baseUrl$apiVersion';

  // API Endpoints
  static const String authRegister = '/auth/register';
  static const String authLogin = '/auth/login';
  static const String expenses = '/expenses';
  static const String expensesStatistics = '/expenses/statistics';
  static const String budgets = '/budgets';
  static const String categories = '/categories';

  // Shared Preferences Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
  static const String userEmailKey = 'user_email';
  static const String userNameKey = 'user_name';
  static const String isLoggedKey = 'is_logged';

  // Date Format Patterns
  static const String dateFormatPattern = 'yyyy-MM-dd';
  static const String dateTimeFormatPattern = 'yyyy-MM-dd HH:mm:ss';
  static const String monthYearFormatPattern = 'MMMM yyyy';
  static const String shortDateFormatPattern = 'dd/MM/yyyy';

  // Pagination
  static const int defaultLimit = 20;
  static const int defaultPage = 1;

  // Budget Threshold
  static const double budgetWarningThreshold = 80.0;

  // Currency
  static const String currencySymbol = '\$';
  static const String currencyCode = 'USD';

  // Expense Categories (Default)
  static const List<String> defaultCategories = [
    'Alimentación',
    'Transporte',
    'Entretenimiento',
    'Salud',
    'Educación',
    'Hogar',
    'Ropa',
    'Servicios',
    'Otro',
  ];

  // Category Icons (Material Icons names)
  static const Map<String, String> categoryIcons = {
    'Alimentación': 'restaurant',
    'Transporte': 'directions_car',
    'Entretenimiento': 'theaters',
    'Salud': 'local_hospital',
    'Educación': 'school',
    'Hogar': 'home',
    'Ropa': 'checkroom',
    'Servicios': 'bolt',
    'Otro': 'category',
  };

  // Category Colors
  static const Map<String, Color> categoryColors = {
    'Alimentación': Color(0xFFFF9800),
    'Transporte': Color(0xFF2196F3),
    'Entretenimiento': Color(0xFF9C27B0),
    'Salud': Color(0xFF4CAF50),
    'Educación': Color(0xFF00BCD4),
    'Hogar': Color(0xFF795548),
    'Ropa': Color(0xFFE91E63),
    'Servicios': Color(0xFF607D8B),
    'Otro': Color(0xFF607D8B),
  };
}
