import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/expense.dart';

class ExpenseRepository {
  static const String baseUrl = 'https://api.example.com/api/v1';

  Future<List<Expense>> getExpenses() async {
    final response = await http.get(
      Uri.parse('$baseUrl/expenses'),
      headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${_token ?? ''}',
    },
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> jsonList = data['data'];
      return jsonList.map((json) => Expense.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load expenses');
    }
  }

  Future<void> addExpense(Expense expense) async {
    final response = await http.post(
      Uri.parse('$baseUrl/expenses'),
      headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${_token ?? ''}',
    },
      body: jsonEncode({
        'categoryId': expense.categoryId,
        'amount': expense.amount,
        'date': expense.date,
        'description': expense.description,
      }),
    );
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to add expense');
    }
  }

  Future<void> deleteExpense(String id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/expenses/$id'),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to delete expense');
    }
  }
}