// Lots widget that will hold list of lots to choose from.

import 'package:flutter/material.dart';
import 'package:parkingtracker/lot.dart';
import 'package:parkingtracker/screens/lotInfo.dart';
import 'package:parkingtracker/screens/screen.dart';

// Stateful = Mutable
class LotsScreen extends StatefulWidget {
  const LotsScreen({super.key});

  @override
  State<LotsScreen> createState() => _LotsScreenState();
}

class _LotsScreenState extends State<LotsScreen> {
  // List of different lots to choose from go here. Info like Name & how many spots available needed.
  // Stateful logic here (things that change)

  // This will need to be changed to pull from backend or internal storage

  List<Lot> lots = [
    Lot('Engineering Lot 1', 1, 70, 100, 'https://i.ibb.co/7dKrFp0T/simplified-Lot.png'),
    Lot('Engineering Lot 2', 2, 30, 70, 'https://i.ibb.co/7dKrFp0T/simplified-Lot.png'),
    Lot('Rocket Stadium Lot 15', 3, 100, 150, 'https://i.ibb.co/7dKrFp0T/simplified-Lot.png'),
  ];
  
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