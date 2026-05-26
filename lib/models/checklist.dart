class ChecklistItem {
  final String id;
  final String section;
  final String description;
  bool isCompleted;
  String? customNotes;
  final String ruleTriggerId;

  ChecklistItem({
    required this.id,
    required this.section,
    required this.description,
    required this.isCompleted,
    this.customNotes,
    required this.ruleTriggerId,
  });

  factory ChecklistItem.fromJson(Map<String, dynamic> json) {
    return ChecklistItem(
      id: json['id'] as String,
      section: json['section'] as String,
      description: json['description'] as String,
      isCompleted: json['is_completed'] as bool,
      customNotes: json['custom_notes'] as String?,
      ruleTriggerId: json['rule_trigger_id'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'section': section,
      'description': description,
      'is_completed': isCompleted,
      'custom_notes': customNotes,
      'rule_trigger_id': ruleTriggerId,
    };
  }
}

class Checklist {
  final String id;
  final String vesselId;
  final DateTime generatedAt;
  final String status;
  final String? exportReference;
  final List<ChecklistItem> items;

  Checklist({
    required this.id,
    required this.vesselId,
    required this.generatedAt,
    required this.status,
    this.exportReference,
    required this.items,
  });

  factory Checklist.fromJson(Map<String, dynamic> json) {
    final itemsJson = json['items'] as List;
    final items = itemsJson.map((item) => ChecklistItem.fromJson(item)).toList();

    return Checklist(
      id: json['id'] as String,
      vesselId: json['vessel_id'] as String,
      generatedAt: DateTime.parse(json['generated_at'] as String),
      status: json['status'] as String,
      exportReference: json['export_reference'] as String?,
      items: items,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'vessel_id': vesselId,
      'generated_at': generatedAt.toIso8601String(),
      'status': status,
      'export_reference': exportReference,
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}