import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import 'presentation/home/home_screen.dart';
import 'presentation/boats/add_boat_screen.dart';
import 'presentation/boats/my_boats_screen.dart';
import 'presentation/checklist/checklist_screen.dart';
import 'presentation/settings/settings_screen.dart';
import 'presentation/weather/weather_screen.dart';
import 'presentation/zone/zone_screen.dart';
import 'presentation/history/history_screen.dart';

void main() {
  runApp(const PreSailingApp());
}

class PreSailingApp extends StatelessWidget {
  const PreSailingApp({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = _buildTheme();
    
    return MultiProvider(
      providers: [],
      child: MaterialApp.router(
        title: 'Pre-Sailing Checklist',
        debugShowCheckedModeBanner: false,
        theme: theme,
        routerConfig: _router,
      ),
    );
  }

  ThemeData _buildTheme() {
    final textTheme = GoogleFonts.outfitTextTheme(
      ThemeData(
        primaryColor: const Color(0xFF1a365d),
        scaffoldBackgroundColor: Colors.white,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1a365d),
          primary: const Color(0xFF1a365d),
          surface: Colors.white,
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
          filled: true,
          fillColor: Colors.grey[50],
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1a365d),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8.0),
            ),
          ),
        ),
        textTheme: GoogleFonts.interTextTheme(const TextTheme()),
      ).copyWith(
        textTheme: GoogleFonts.outfitTextTheme(const TextTheme()),
      ),
    );
    return theme;
  }
}

final _router = GoRouter(
  initialLocation: '/home',
  routes: [
    GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/boats', builder: (context, state) => const MyBoatsScreen()),
    GoRoute(path: '/boats/add', builder: (context, state) => const AddBoatScreen()),
    GoRoute(path: '/checklist', builder: (context, state) => const ChecklistScreen()),
    GoRoute(path: '/weather', builder: (context, state) => const WeatherScreen()),
    GoRoute(path: '/zone', builder: (context, state) => const ZoneScreen()),
    GoRoute(path: '/history', builder: (context, state) => const HistoryScreen()),
    GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
  ],
);