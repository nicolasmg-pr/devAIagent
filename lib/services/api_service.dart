import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
    static const String baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://api.maritime-checklist.com/api/v1');

  Future<Map<String, dynamic>> post(String endpoint, Map<String, dynamic> body) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw ApiException(response.statusCode, jsonDecode(response.body)['message'] ?? 'Unknown error');
    }
  }

  Future<Map<String, dynamic>> get(String endpoint) async {
    final response = await http.get(Uri.parse('$baseUrl$endpoint'));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load data: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> patch(String endpoint, Map<String, dynamic> body) async {
    final response = await http.patch(
      Uri.parse('$baseUrl$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to update data: ${response.statusCode}');
    }
  }
}