import 'package:flutter/foundation.dart';
import 'models/vessel.dart';
import 'repositories/vessel_repository.dart';

class VesselProvider extends ChangeNotifier {
  final VesselRepository _repository = VesselRepository();
  Vessel? _vessel;
  bool _isLoading = false;
  String? _error;

  Vessel? get vessel => _vessel;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> registerVessel({
    required String type,
    required double length,
    required String navigationZone,
    required int maxPassengers,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final newVessel = await _repository.createVessel(
        type: type,
        length: length,
        navigationZone: navigationZone,
        maxPassengers: maxPassengers,
      );
      _vessel = newVessel;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}