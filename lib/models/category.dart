class Category {
  final String id;
  final String name;
  final String color;
  final bool isDefault;

  Category({
    required this.id,
    required this.name,
    required this.color,
    required this.isDefault,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'],
      color: json['color'],
      isDefault: json['isDefault'] ?? false,
    );
  }
}