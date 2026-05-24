import 'package:equatable/equatable.dart';

/// Category Entity
class CategoryEntity extends Equatable {
  final String id;
  final String name;
  final String color;
  final bool isSystem;

  const CategoryEntity({
    required this.id,
    required this.name,
    required this.color,
    this.isSystem = false,
  });

  factory CategoryEntity.fromJson(Map<String, dynamic> json) {
    return CategoryEntity(
      id: json['id'] as String,
      name: json['name'] as String,
      color: json['color'] as String,
      isSystem: json['is_system'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'color': color,
      'is_system': isSystem,
    };
  }

  CategoryEntity copyWith({
    String? id,
    String? name,
    String? color,
    bool? isSystem,
  }) {
    return CategoryEntity(
      id: id ?? this.id,
      name: name ?? this.name,
      color: color ?? this.color,
      isSystem: isSystem ?? this.isSystem,
    );
  }

  @override
  List<Object?> get props => [id, name, color, isSystem];
}
