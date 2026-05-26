import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/vessel.dart';
import '../models/checklist.dart';
import '../providers/checklist_provider.dart';

class ChecklistScreen extends StatefulWidget {
  final Vessel vessel;

  const ChecklistScreen({super.key, required this.vessel});

  @override
  State<ChecklistScreen> createState() => _ChecklistScreenState();
}

class _ChecklistScreenState extends State<ChecklistScreen> {
  String _weatherConditions = 'Fair';

  final List<String> _weatherOptions = ['Fair', 'Rough', 'Stormy'];

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ChecklistProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Pre-Sailing Checklist'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text('Vessel: ${widget.vessel.type} (${widget.vessel.length}m)'),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _weatherConditions,
              decoration: const InputDecoration(labelText: 'Weather Conditions'),
              items: _weatherOptions.map((w) => DropdownMenuItem(value: w, child: Text(w))).toList(),
              onChanged: (value) => setState(() => _weatherConditions = value!),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: provider.isLoading
                  ? null
                  : () {
                      provider.generateChecklist(
                        vesselId: widget.vessel.id,
                        weatherConditions: _weatherConditions,
                        passengerCount: widget.vessel.maxPassengers,
                      );
                    },
              child: provider.isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Generate Checklist'),
            ),
            if (provider.error != null)
              Padding(
                padding: const EdgeInsets.only(top: 16.0),
                child: Text(
                  provider.error!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            const SizedBox(height: 16),
            if (provider.checklist != null)
              Expanded(
                child: _buildChecklistList(provider.checklist!.items),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildChecklistList(List<ChecklistItem> items) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8.0),
          child: ListTile(
            leading: Checkbox(
              value: item.isCompleted,
              onChanged: (value) {
                context.read<ChecklistProvider>().updateItem(
                      item.id,
                      value!,
                      item.customNotes,
                    );
              },
            ),
            title: Text(item.description),
            subtitle: Text(item.section),
            trailing: IconButton(
              icon: const Icon(Icons.note),
              onPressed: () {
                // Show note dialog
              },
            ),
          ),
        );
      },
    );
  }
}