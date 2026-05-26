import 'package:flutter/material.dart';
import 'presentation/screens/home_screen.dart';
import 'presentation/screens/vessel_form_screen.dart';
import 'presentation/screens/checklist_screen.dart';

void main() {
  runApp(const MarineCheckProApp());
}

class MarineCheckProApp extends StatelessWidget {
  const MarineCheckProApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MarineCheck Pro',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        colorScheme: ColorScheme.fromSwatch(
          primarySwatch: Colors.blue,
          accentColor: Colors.orange,
        ).copyWith(
          secondary: Colors.orange,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          elevation: 4,
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/vessel': (context) => const VesselFormScreen(),
        '/checklist': (context) => const ChecklistScreen(),
      },
    );
  }
}