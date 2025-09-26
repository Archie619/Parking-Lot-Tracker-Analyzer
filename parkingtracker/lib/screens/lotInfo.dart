// Lot info widget that holds simplified map of chosen parking lot and how many current available spots left.

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:parkingtracker/lot.dart';
import 'package:parkingtracker/requests.dart';


// Stateful = Mutable
class LotsInfoScreen extends StatefulWidget {
  const LotsInfoScreen({super.key, required this.lot}); // Require chosen lot be sent to this widget to get info for specific lot

  final Lot lot; 

  @override
  State<LotsInfoScreen> createState() => _LotsInfoScreenState();
}

class _LotsInfoScreenState extends State<LotsInfoScreen> {

  late Lot currentLot; // Up-to-date lot var (this will be updated periodically, pulls in new available spots number - the following pulls in new map)
  final Requests requests = Requests(); // Create Requests object to call functions to get data
  late Timer timer; // Will be destroyed when widget is dismissed.

  // Initalize currentLot w sent data
  @override
  void initState() {
    super.initState();
    currentLot = widget.lot;
    updateLotMap();

    // Every 60 seconds, refresh data
    timer = Timer.periodic(const Duration(seconds: 30), (timer) => updateLotMap());
  }

  // Cancel timer
  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

   // For each lot, get data from backend on how many spots available & then update UI.
  Future<void> updateLotMap() async {
    final data = await requests.fetchLotMap(currentLot.lotName);

    if (data != null) {
      setState(() { // Updates UI
        // Update lot map
        currentLot.lotMap = data; 
      });
    }
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
        mainAxisSize: MainAxisSize.min, // shrink boxes to fit if needed
        children: [
          // display map here
          if (currentLot.lotMap != null) // if map is not null
            ...currentLot.lotMap!.map((row) { // loops through each list (row) [ [], [] ]
              return Row( // create a physical row widget on the UI, its children are the individual spots...
                children: row.map<Widget>((spot) { // loops through each individual spot, return a container widget for each spot to represent parking space
                  return Container(
                    width: 40,
                    height: 70,
                    margin: const EdgeInsets.all(4), // padding
                    color: spot['occupied'] ? Colors.red : Colors.green, // depending on individual spot occupancy
                  );
                }).toList() // convert all containers in row to list, return it.
              );
            }),

          // display spots available
          Text('${currentLot.availableSpots} spots available!'), // display # of spots taken
        ],
      ) 
    );
  }
}