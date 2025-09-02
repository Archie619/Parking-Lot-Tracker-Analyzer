// Lots widget that will hold list of lots to choose from.

import 'package:flutter/material.dart';

// Stateful = Mutable
class LotsScreen extends StatefulWidget {
  const LotsScreen({super.key});

  @override
  State<LotsScreen> createState() => _LotsScreenState();
}

class _LotsScreenState extends State<LotsScreen> {
  // List of different lots to choose from go here. Info like Name & how many spots available needed.
  // Stateful logic here (things that change)
  
  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 227, 210, 248),
      body: Center(child: Text('Parking Lot List here')),
    );
  }
}