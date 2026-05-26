class ChecklistItem {
  final String id;
  final String ruleCategory;
  final String description;
  final bool isCompleted;

  ChecklistItem({
    required this.id,
    required this.ruleCategory,
    required this.description,
    required this.isCompleted,
  });

  factory ChecklistItem.fromJson(Map<String, dynamic> json) {
    return ChecklistItem(
      id: json['id'] ?? '',
      ruleCategory: json['rule_category'] ?? '',
      description: json['description'] ?? '',
      isCompleted: json['is_completed'] ?? false,
    );
  }
}

class Checklist {
  final String id;
  final String vesselId;
  final String status;
  final List<ChecklistItem> items;

  Checklist({
    required this.id,
    required this.vesselId,
    required this.status,
    required this.items,
  });

  factory Checklist.fromJson(Map<String, dynamic> json) {
    final itemsJson = json['items'] as List<dynamic>? ?? [];
    final items = itemsJson.map((item) => ChecklistItem.fromJson(item)).toList();

    return Checklist(
      id: json['id'] ?? '',
      vesselId: json['vessel_ref'] != null ? (json['vessel_ref'] as Map<String, dynamic>)['id'] : '',
      status: json['status'] ?? 'pending',
      items: items,
    );
  }
}