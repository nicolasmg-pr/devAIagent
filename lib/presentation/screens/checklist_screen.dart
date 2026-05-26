import 'package:flutter/material.dart';
import '../../data/repositories/checklist_repository.dart';
import '../../data/services/api_service.dart';
import '../../domain/models/checklist_model.dart';

class ChecklistScreen extends StatefulWidget {
  const ChecklistScreen({Key? key}) : super(key: key);

  @override
  State<ChecklistScreen> createState() => _ChecklistScreenState();
}

class _ChecklistScreenState extends State<ChecklistScreen> {
  late ChecklistRepository _repository;
  Checklist? _checklist;
  String? _checklistId;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _repository = ChecklistRepository(
      apiService: ApiService(baseUrl: 'http://api.marinecheck.local'),
    );
    _initChecklist();
  }

  Future<void> _initChecklist() async {
    setState(() => _isLoading = true);
    // Simulating a hardcoded ID for demo purposes or passed argument
    _checklistId = 'demo-checklist-id'; 
    try {
      final data = await _repository.getChecklist(_checklistId!);
      setState(() {
        _checklist = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleItem(ChecklistItem item) async {
    final newState = !item.isCompleted;
    try {
      await _repository.updateItem(_checklistId!, item.id, newState);
      setState(() {
        final index = _checklist!.items.indexWhere((i) => i.id == item.id);
        if (index != -1) {
          _checklist!.items[index] = ChecklistItem(
            id: item.id,
            ruleCategory: item.ruleCategory,
            description: item.description,
            isCompleted: newState,
          );
        }
      });
    } catch (e) {
      // Handle error
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Lista de Verificación')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _checklist == null
              ? const Center(child: Text('No se pudo cargar la lista'))
              : ListView.builder(
                  itemCount: _checklist!.items.length,
                  itemBuilder: (context, index) {
                    final item = _checklist!.items[index];
                    return ListTile(
                      leading: Checkbox(
                        value: item.isCompleted,
                        onChanged: (_) => _toggleItem(item),
                      ),
                      title: Text(item.description),
                      subtitle: Text(item.ruleCategory),
                    );
                  },
                ),
    );
  }
}