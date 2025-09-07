// Lot info widget that holds simplified map of chosen parking lot and how many current available spots left.

import 'package:flutter/material.dart';
import 'package:parkingtracker/lot.dart';

// Stateful = Mutable
class LotsInfoScreen extends StatefulWidget {
  const LotsInfoScreen({super.key, required this.lot}); // Require chosen lot be sent to this widget to get info for specific lot

  final Lot lot; 

  @override
  State<LotsInfoScreen> createState() => _LotsInfoScreenState();
}

class _LotsInfoScreenState extends State<LotsInfoScreen> {

  late Lot currentLot; // Up-to-date lot var (this will be updated periodically)

  // Update lot info/map every min?

  // Initalize currentLot w sent data
  @override
  void initState() {
    super.initState();
    currentLot = widget.lot;
  }

  // Update current lot periodically
  @override
  void didUpdateWidget(covariant LotsInfoScreen oldWidget) {
    super.didUpdateWidget(oldWidget);

    // currentLot = new data

  }


  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 227, 210, 248),
      appBar: AppBar(
        backgroundColor: Color.fromARGB(255, 86, 163, 227),
        foregroundColor: Colors.white,
        title: Text(currentLot.lotName),
      ),
      body: Column (
        children: [
          Image.network(currentLot.mapPath), // display map
          Center(child: Text('${currentLot.spotsTaken}/${currentLot.totalSpots} spots taken!')), // display # of spots taken
        ],
      ) 
    );
  }
}