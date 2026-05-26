import '../models/vessel_model.dart';
import '../services/api_service.dart';
import 'dart:convert';

class VesselRepository {
  final ApiService apiService;

  VesselRepository({required this.apiService});

  Future<List<Vessel>> getVessels() async {
    try {
      final data = await apiService.getVessels();
      if (data is List) {
        return data.map((json) => Vessel.fromJson(json)).toList();
      } else if (data is Map<String, dynamic> && data.containsKey('data')) {
         return (data['data'] as List).map((json) => Vessel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      // Handle offline or network error
      return [];
    }
  }

  Future<Vessel> createVessel(Vessel vessel) async {
    final response = await apiService.createVessel(vessel.toJson());
    return Vessel.fromJson(response);
  }
}