class DateUtils {
  DateUtils._();

  static String formatCurrency(double amount, {String currency = 'USD'}) {
    return '${currency} ${amount.toStringAsFixed(2)}';
  }

  static String formatDate(DateTime date) {
    final months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    
    return '${date.day} de ${months[date.month - 1]} de ${date.year}';
  }

  static String formatDateShort(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  static String formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  static String formatDateTime(DateTime dateTime) {
    return '${formatDate(dateTime)} ${formatTime(dateTime)}';
  }

  static String getRelativeDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays == 0) {
      return 'Hoy';
    } else if (difference.inDays == 1) {
      return 'Ayer';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} días ago';
    } else if (difference.inDays < 30) {
      final weeks = (difference.inDays / 7).floor();
      return '$weeks semana${weeks > 1 ? 's' : ''} ago';
    } else {
      return formatDateShort(date);
    }
  }

  static DateTime getStartOfMonth(int year, int month) {
    return DateTime(year, month, 1);
  }

  static DateTime getEndOfMonth(int year, int month) {
    return DateTime(year, month + 1, 0, 23, 59, 59);
  }

  static String getMonthName(int month) {
    final months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return months[month - 1];
  }

  static String getMonthShortName(int month) {
    final months = [
      'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    ];
    return months[month - 1];
  }

  static String getCurrentMonthYear() {
    final now = DateTime.now();
    return '${getMonthName(now.month)} ${now.year}';
  }

  static String getPeriodString(int month, int year) {
    return '${year}-${month.toString().padLeft(2, '0')}';
  }
}
