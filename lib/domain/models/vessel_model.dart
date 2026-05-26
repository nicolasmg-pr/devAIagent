class Vessel {
  final String id;
  final String name;
  final double length;
  final int capacity;
  final String zone;
  final String propulsion;
  final DateTime createdAt;

  Vessel({
    required this.id,
    required this.name,
    required this.length,
    required this.capacity,
    required this.zone,
    required this.propulsion,
    required this.createdAt,
  });

  factory Vessel.fromJson(Map<String, dynamic> json) {
    return Vessel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      length: (json['length'] ?? 0).toDouble(),
      capacity: json['capacity'] ?? 0,
      zone: json['zone'] ?? '',
      propulsion: json['propulsion'] ?? '',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'length': length,
      'capacity': capacity,
      'zone': zone,
      'propulsion': propulsion,
    };
  }
}