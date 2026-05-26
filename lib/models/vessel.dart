class Vessel {
  final String id;
  final String type;
  final double length;
  final String navigationZone;
  final int maxPassengers;
  final String ownerId;
  final DateTime createdAt;

  Vessel({
    required this.id,
    required this.type,
    required this.length,
    required this.navigationZone,
    required this.maxPassengers,
    required this.ownerId,
    required this.createdAt,
  });

  factory Vessel.fromJson(Map<String, dynamic> json) {
    return Vessel(
      id: json['id'] as String,
      type: json['type'] as String,
      length: (json['length'] as num).toDouble(),
      navigationZone: json['navigation_zone'] as String,
      maxPassengers: json['max_passengers'] as int,
      ownerId: json['owner_id'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'length': length,
      'navigation_zone': navigationZone,
      'max_passengers': maxPassengers,
    };
  }
}