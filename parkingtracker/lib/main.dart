import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/screen.dart';

void main() {
  runApp(MyApp()); // Start execution of app
}

// Stateless = no dynamic data
class MyApp extends StatelessWidget {
  const MyApp({super.key});

// Build method called anytime Flutter rebuilds UI, returns MaterialApp widget
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Parking Lot Tracker",
      home: Screen(), // Default to Screen (Main widget that will hold our other widgets)
    );
  }
}