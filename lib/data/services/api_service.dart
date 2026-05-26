import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;
  final http.Client client;

  ApiService({required this.baseUrl, http.Client? client})
      : client = client ?? http.Client();

  Future<Map<String, dynamic>> getVessels() async {
    final response = await client.get(Uri.parse('$baseUrl/v1/vessels'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load vessels');
    }
  }

  Future<Map<String, dynamic>> createVessel(Map<String, dynamic> vessel) async {
    final response = await client.post(
      Uri.parse('$baseUrl/v1/vessels'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(vessel),
    );
    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to create vessel');
    }
  }

  Future<Map<String, dynamic>> generateChecklist(String vesselId) async {
    final response = await client.post(
      Uri.parse('$baseUrl/v1/checklists/generate'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'vessel_id': vesselId, 'protocol_version': '1.0'}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to generate checklist');
    }
  }

  Future<Map<String, dynamic>> getChecklist(String checklistId) async {
    final response = await client.get(Uri.parse('$baseUrl/v1/checklists/$checklistId'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load checklist');
    }
  }

  Future<Map<String, dynamic>> updateChecklistItem(String checklistId, String itemId, bool isCompleted) async {
    final response = await client.put(
      Uri.parse('$baseUrl/v1/checklists/$checklistId/items/$itemId'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'is_completed': isCompleted}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to update item');
    }
  }
}