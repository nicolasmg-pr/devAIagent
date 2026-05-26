import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/checklist_provider.dart';
import '../models/checklist.dart';

class ChecklistResultScreen extends StatelessWidget {
  const ChecklistResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ChecklistProvider>();
    final Checklist? checklist = provider.checklist;

    if (checklist == null) {
      return const Scaffold(
        body: Center(child: Text('No checklist available')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Checklist Summary'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Generated: ${checklist.generatedAt}'),
            Text('Status: ${checklist.status}'),
            const SizedBox(height: 16),
            const Text('Completed Items:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView(
                children: checklist.items
                    .where((item) => item.isCompleted)
                    .map((item) => Text('- ${item.description}'))
                    .toList(),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      provider.exportChecklist('pdf');
                    },
                    child: const Text('Export PDF'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      provider.exportChecklist('text');
                    },
                    child: const Text('Export Text'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}