import '../models/vessel.dart';
import '../services/api_service.dart';

class VesselRepository {
  final ApiService _apiService = ApiService();

  Future<Vessel> createVessel({
    required String type,
    required double length,
    required String navigationZone,
    required int maxPassengers,
  }) async {
    final response = await _apiService.post('/vessels', {
      'type': type,
      'length': length,
      'navigation_zone': navigationZone,
      'max_passengers': maxPassengers,
    });
    return Vessel.fromJson(response);
  }

  Future<Vessel> getVessel(String vesselId) async {
    final response = await _apiService.get('/vessels/$vesselId');
    return Vessel.fromJson(response);
  }
}