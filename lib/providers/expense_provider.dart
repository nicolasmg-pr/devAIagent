import 'package:flutter/foundation.dart';
import '../repositories/expense_repository.dart';
import '../models/expense.dart';

class ExpenseProvider with ChangeNotifier {
  final ExpenseRepository _repository = ExpenseRepository();
  List<Expense> _expenses = [];

  List<Expense> get expenses => _expenses;

  Future<void> fetchExpenses() async {
    try {
      _expenses = await _repository.getExpenses();
      notifyListeners();
    } catch (e) {
      // Handle error
    }
  }

  Future<void> addExpense(Expense expense) async {
    await _repository.addExpense(expense);
    await fetchExpenses();
  }

  Future<void> deleteExpense(String id) async {
    await _repository.deleteExpense(id);
    await fetchExpenses();
  }
}