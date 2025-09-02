// Initialize widget that will allow user to add/initialize new lots

import 'package:flutter/material.dart';

// Stateful = Mutable
class InitializeScreen extends StatefulWidget {
  const InitializeScreen({super.key});

  @override
  State<InitializeScreen> createState() => _InitializeScreenState();
}

class _InitializeScreenState extends State<InitializeScreen> {
  // List of different lots to choose from go here. Info like Name & how many spots available needed.
  // Stateful logic here (things that change)
  
  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 199, 199, 199),
      body: Center(child: Text('Initialize lots here')),
    );
  }
}