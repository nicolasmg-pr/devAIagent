import '../models/checklist.dart';
import '../services/api_service.dart';

class ChecklistRepository {
  final ApiService _apiService = ApiService();

  Future<Checklist> generateChecklist({
    required String vesselId,
    required String weatherConditions,
    required int passengerCount,
  }) async {
    final response = await _apiService.post('/checklists/generate', {
      'vessel_id': vesselId,
      'weather_conditions': weatherConditions,
      'passenger_count': passengerCount,
    });
    return Checklist.fromJson(response);
  }

  Future<Checklist> getChecklist(String checklistId) async {
    final response = await _apiService.get('/checklists/$checklistId');
    return Checklist.fromJson(response);
  }

  Future<Checklist> updateChecklistItem({
    required String checklistId,
    required String itemId,
    required bool isCompleted,
    String? customNotes,
  }) async {
    final response = await _apiService.patch('/checklists/$checklistId/items', [
      {
        'item_id': itemId,
        'is_completed': isCompleted,
        'custom_notes': customNotes,
      }
    ]);
    return Checklist.fromJson(response);
  }

  Future<Map<String, dynamic>> exportChecklist({
    required String checklistId,
    required String format,
    required bool includeTimestamp,
  }) async {
    return await _apiService.post('/checklists/$checklistId/export', {
      'format': format,
      'include_timestamp': includeTimestamp,
    });
  }
}