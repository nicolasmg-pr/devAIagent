import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/vessel_provider.dart';
import 'checklist_screen.dart';

class VesselRegistrationScreen extends StatefulWidget {
  const VesselRegistrationScreen({super.key});

  @override
  State<VesselRegistrationScreen> createState() => _VesselRegistrationScreenState();
}

class _VesselRegistrationScreenState extends State<VesselRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  String _type = 'Sailboat';
  double _length = 10.0;
  String _zone = 'A';
  int _passengers = 1;

  final List<String> _types = ['Sailboat', 'Motorboat', 'Yacht', 'Catamaran'];
  final List<String> _zones = ['A', 'B', 'C', 'Coastal'];

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<VesselProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Register Vessel'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              DropdownButtonFormField<String>(
                value: _type,
                decoration: const InputDecoration(labelText: 'Vessel Type'),
                items: _types.map((type) => DropdownMenuItem(value: type, child: Text(type))).toList(),
                onChanged: (value) => setState(() => _type = value!),
              ),
              const SizedBox(height: 16),
              Slider(
                value: _length,
                min: 5,
                max: 50,
                divisions: 45,
                label: _length.toStringAsFixed(1),
                onChanged: (value) => setState(() => _length = value),
              ),
              Text('Length: ${_length.toStringAsFixed(1)}m'),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _zone,
                decoration: const InputDecoration(labelText: 'Navigation Zone'),
                items: _zones.map((zone) => DropdownMenuItem(value: zone, child: Text(zone))).toList(),
                onChanged: (value) => setState(() => _zone = value!),
              ),
              const SizedBox(height: 16),
              TextFormField(
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Max Passengers'),
                initialValue: _passengers.toString(),
                onChanged: (value) => setState(() => _passengers = int.tryParse(value) ?? 1),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: provider.isLoading
                    ? null
                    : () async {
                        if (_formKey.currentState!.validate()) {
                          await provider.registerVessel(
                            type: _type,
                            length: _length,
                            navigationZone: _zone,
                            maxPassengers: _passengers,
                          );
                          if (provider.vessel != null) {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => ChecklistScreen(
                                  vessel: provider.vessel!,
                                ),
                              ),
                            );
                          }
                        }
                      },
                child: provider.isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Register & Generate Checklist'),
              ),
              if (provider.error != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Text(
                    provider.error!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}