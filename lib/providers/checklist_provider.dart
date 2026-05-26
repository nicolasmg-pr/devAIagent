import 'package:flutter/foundation.dart';
import 'models/checklist.dart';
import 'repositories/checklist_repository.dart';

class ChecklistProvider extends ChangeNotifier {
  final ChecklistRepository _repository = ChecklistRepository();
  Checklist? _checklist;
  bool _isLoading = false;
  String? _error;

  Checklist? get checklist => _checklist;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> generateChecklist({
    required String vesselId,
    required String weatherConditions,
    required int passengerCount,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final generated = await _repository.generateChecklist(
        vesselId: vesselId,
        weatherConditions: weatherConditions,
        passengerCount: passengerCount,
      );
      _checklist = generated;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateItem(String itemId, bool isCompleted, String? notes) async {
    if (_checklist == null) return;
    
    _isLoading = true;
    notifyListeners();

    try {
      final updated = await _repository.updateChecklistItem(
        checklistId: _checklist!.id,
        itemId: itemId,
        isCompleted: isCompleted,
        customNotes: notes,
      );
      _checklist = updated;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> exportChecklist(String format) async {
    if (_checklist == null) return;
    
    _isLoading = true;
    notifyListeners();

    try {
      final exportData = await _repository.exportChecklist(
        checklistId: _checklist!.id,
        format: format,
        includeTimestamp: true,
      );
      print('Exported data: $exportData');
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}