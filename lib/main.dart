import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/vessel_provider.dart';
import 'providers/checklist_provider.dart';
import 'screens/vessel_registration_screen.dart';

void main() {
  runApp(const MaritimeChecklistApp());
}

class MaritimeChecklistApp extends StatelessWidget {
  const MaritimeChecklistApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => VesselProvider()),
        ChangeNotifierProvider(create: (_) => ChecklistProvider()),
      ],
      child: MaterialApp(
        title: 'Maritime Pre-Sailing Checklist',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          brightness: Brightness.light,
          useMaterial3: true,
        ),
        home: const VesselRegistrationScreen(),
      ),
    );
  }
}