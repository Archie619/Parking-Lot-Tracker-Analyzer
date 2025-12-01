import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/screen.dart';

// Color Palette
const yellow = Color(0xFFFFE79B); // Bottom nav + header strip background
const blue = Color(0xFF5BA8FF); // Icons/labels/accent
const barBg = Color(0xFFA7E7FF); // App bar background
const cream = Color(0xFFFFFFDF); // Page background

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp()); // Start execution of app
}

// Stateless = no dynamic data
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // Creates the app shell (theme and home screen)
  @override
  Widget build(BuildContext context) {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: blue,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: cream,
      fontFamily: 'Merriweather',
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(),
      ),
    );

    final themed = base.copyWith(
      appBarTheme: base.appBarTheme.copyWith(
        centerTitle: true,
        backgroundColor: barBg,
        foregroundColor: Colors.black87,
        titleTextStyle: const TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w800, // Bolded app title
          color: Colors.black87,
          fontFamily: 'Merriweather',
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: yellow,
        indicatorColor: blue,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: selected ? Colors.white : blue,
            fontFamily: 'Merriweather',
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(size: 24, color: selected ? Colors.white : blue);
        }),
      ),
    );

    return MaterialApp(
      title: 'Parking Lot Tracker',
      theme: themed,
      home: const Screen(), // Main tabs (Lots/Initialize)
    );
  }
}
