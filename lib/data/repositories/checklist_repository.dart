import '../models/checklist_model.dart';
import '../services/api_service.dart';

class ChecklistRepository {
  final ApiService apiService;

  ChecklistRepository({required this.apiService});

  Future<String> generateChecklist(String vesselId) async {
    final data = await apiService.generateChecklist(vesselId);
    return data['checklist_id'];
  }

  Future<Checklist> getChecklist(String checklistId) async {
    final data = await apiService.getChecklist(checklistId);
    return Checklist.fromJson(data);
  }

  Future<void> updateItem(String checklistId, String itemId, bool isCompleted) async {
    await apiService.updateChecklistItem(checklistId, itemId, isCompleted);
  }
}