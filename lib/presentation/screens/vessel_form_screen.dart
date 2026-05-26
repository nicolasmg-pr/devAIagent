import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../data/repositories/vessel_repository.dart';
import '../../data/services/api_service.dart';
import '../../domain/models/vessel_model.dart';

class VesselFormScreen extends StatefulWidget {
  const VesselFormScreen({Key? key}) : super(key: key);

  @override
  State<VesselFormScreen> createState() => _VesselFormScreenState();
}

class _VesselFormScreenState extends State<VesselFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _lengthController = TextEditingController();
  final _capacityController = TextEditingController();
  String? _selectedZone;
  String? _selectedPropulsion;
  late VesselRepository _repository;

  @override
  void initState() {
    super.initState();
    _repository = VesselRepository(
      apiService: ApiService(baseUrl: 'http://api.marinecheck.local'),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _lengthController.dispose();
    _capacityController.dispose();
    super.dispose();
  }

  Future<void> _saveVessel() async {
    if (_formKey.currentState!.validate()) {
      final vessel = Vessel(
        id: '', // Assuming server generates ID
        name: _nameController.text,
        length: double.parse(_lengthController.text),
        capacity: int.parse(_capacityController.text),
        zone: _selectedZone ?? 'coastal',
        propulsion: _selectedPropulsion ?? 'diesel',
        createdAt: DateTime.now(),
      );

      try {
        await _repository.createVessel(vessel);
        if (mounted) {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Embarcación guardada correctamente')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Error al guardar')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva Embarcación')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (v) => v?.isEmpty ?? true ? 'Requerido' : null,
              ),
              TextFormField(
                controller: _lengthController,
                decoration: const InputDecoration(labelText: 'Eslora (m)'),
                keyboardType: TextInputType.number,
                validator: (v) => double.tryParse(v ?? '') == null ? 'Inválido' : null,
              ),
              TextFormField(
                controller: _capacityController,
                decoration: const InputDecoration(labelText: 'Capacidad (plazas)'),
                keyboardType: TextInputType.number,
                validator: (v) => int.tryParse(v ?? '') == null ? 'Inválido' : null,
              ),
              const SizedBox(height: 20),
              DropdownButtonFormField<String>(
                value: _selectedZone,
                decoration: const InputDecoration(labelText: 'Zona de Operación'),
                items: ['coastal', 'offshore', 'inland']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (v) => setState(() => _selectedZone = v),
              ),
              DropdownButtonFormField<String>(
                value: _selectedPropulsion,
                decoration: const InputDecoration(labelText: 'Propulsión'),
                items: ['diesel', 'gasoline', 'electric']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (v) => setState(() => _selectedPropulsion = v),
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: _saveVessel,
                child: const Text('Guardar'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}