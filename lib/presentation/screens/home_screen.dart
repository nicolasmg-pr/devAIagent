import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../data/repositories/vessel_repository.dart';
import '../../data/services/api_service.dart';
import '../../domain/models/vessel_model.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late VesselRepository _repository;
  List<Vessel> _vessels = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _repository = VesselRepository(
      apiService: ApiService(baseUrl: 'http://api.marinecheck.local'),
    );
    _loadVessels();
  }

  Future<void> _loadVessels() async {
    try {
      final vessels = await _repository.getVessels();
      setState(() {
        _vessels = vessels;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MarineCheck Pro'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadVessels,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _vessels.isEmpty
              ? const Center(child: Text('No hay embarcaciones registradas'))
              : ListView.builder(
                  itemCount: _vessels.length,
                  itemBuilder: (context, index) {
                    final vessel = _vessels[index];
                    return Card(
                      margin: const EdgeInsets.all(8),
                      child: ListTile(
                        leading: const Icon(Icons.directions_boat),
                        title: Text(vessel.name),
                        subtitle: Text(
                          '${vessel.length}m | Capacidad: ${vessel.capacity}',
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          // Navigate to checklist or details
                        },
                      ),
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context).pushNamed('/vessel');
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}