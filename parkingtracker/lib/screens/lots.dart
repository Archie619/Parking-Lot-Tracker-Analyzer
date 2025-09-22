// Lots widget that will hold list of lots to choose from.

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:parkingtracker/lot.dart';
import 'package:parkingtracker/requests.dart';
import 'package:parkingtracker/screens/lotInfo.dart';

// Stateful = Mutable
class LotsScreen extends StatefulWidget {
  const LotsScreen({super.key});

  @override
  State<LotsScreen> createState() => _LotsScreenState();
}

class _LotsScreenState extends State<LotsScreen> {

  // Initialize Lot objects with names
  List<Lot> lots = [
    Lot(lotName: 'Engineering Lot 1'),
    Lot(lotName: 'Engineering Lot 2'),
    Lot(lotName: 'Rocket Stadium Lot 15'),
  ];

  final Requests requests = Requests(); // Create Requests object to call functions to get data
  late Timer timer; // Will be destroyed when widget is dismissed.

  // Initial state of widget: get lot data for each info, and then update periodically from there.
  @override
  void initState() {
    super.initState();
    updateLotData();

    // Every 60 seconds, refresh data
    timer = Timer.periodic(const Duration(minutes: 1), (timer) => updateLotData());
  }
  
  // Cancel timer
  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

  // For each lot, get data from backend on how many spots available & then update UI.
  Future<void> updateLotData() async {
    for (Lot lot in lots) { 
      final data = await requests.fetchLotInfo(lot.lotName);

      if (data != null) {
        setState(() { // Updates UI
          // Update lot data
          lot.availableSpots = data['available_spots'];
          lot.totalSpots = data['total_spots'];
        });
      }
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
        title: Text('Available Parking Lots'),
      ),
      body: ListView.separated( // Create list of lots to choose from using itemBuilder (which allows us to dynamically create it)
        itemBuilder: (BuildContext context, int index) {
          return InkWell( // Allows us to recognize taps on specific containers (lots)
            onTap: () {
              Navigator.push( // Push new lotsInfoScreen to front and give current info on it.
                context,
                MaterialPageRoute<void>(
                  builder: (context) => LotsInfoScreen(lot: lots[index]),
                  ),
              );
            },
            child: Container(
            padding: EdgeInsets.only(left: 15.0, right: 25.0), // pad both left/right of container
            height: 60,
            decoration: BoxDecoration(
              color: Colors.greenAccent,
              border: Border.all(
                color: Colors.black, 
                width: 4,
              )
            ),
            child: 
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween, // put max space between children
                children: [
                  Text(lots[index].lotName), // show lot name
                  Text('${lots[index].availableSpots} spots left!'), // show # of spots left
                ],
              ),
            ),
          );
            
        },
        padding: const EdgeInsets.all(15), 
        separatorBuilder: (BuildContext context, int index) => const Divider(), 
        itemCount: lots.length,
      ),
    );
  }
}