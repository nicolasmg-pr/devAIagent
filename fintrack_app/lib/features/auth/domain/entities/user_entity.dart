import 'package:equatable/equatable.dart';

/// User Entity for Auth feature
class UserEntity extends Equatable {
  final String id;
  final String email;
  final String fullName;
  final DateTime createdAt;

  const UserEntity({
    required this.id,
    required this.email,
    this.fullName = '',
    required this.createdAt,
  });

  factory UserEntity.fromJson(Map<String, dynamic> json) {
    return UserEntity(
      id: json['id'] as String,
      email: json['email'] as String,
      fullName: json['full_name'] as String? ?? '',
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'created_at': createdAt.toIso8601String(),
    };
  }

  UserEntity copyWith({
    String? id,
    String? email,
    String? fullName,
    DateTime? createdAt,
  }) {
    return UserEntity(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [id, email, fullName];
}
