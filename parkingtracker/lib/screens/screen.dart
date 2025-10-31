// Main widget that will hold our other widgets

import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/initialize.dart';
import 'package:parkingtracker/screens/lots.dart';
import 'package:parkingtracker/screens/parking_page.dart';

// Stateful = Mutable
class Screen extends StatefulWidget {
  const Screen({super.key});

  @override
  State<Screen> createState() => _ScreenState();
}

class _ScreenState extends State<Screen> {
  // Stateful logic here (things that change)

  int currentPageIndex = 0;
  
  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: NavigationBar( // Create bottom nav bar to switch the body of main screen
        backgroundColor: const Color.fromARGB(255, 86, 163, 227),
        onDestinationSelected: (int index) { // Called when icon is tapped - get WHICH icon which is index, and set current page to it.
          setState(() {
            currentPageIndex = index;
          });
        },
        indicatorColor: Colors.yellow,
        selectedIndex: currentPageIndex,
        destinations: const <Widget>[ // Define tabs in nav bar
          NavigationDestination(
            selectedIcon: Icon(Icons.map), 
            icon: Icon(Icons.map_outlined), 
            label: 'Lots',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.perm_data_setting), 
            icon: Icon(Icons.perm_data_setting_outlined), 
            label: 'Initialize',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.local_parking),
            icon: Icon(Icons.local_parking_outlined),
            label: 'Parking',
          ),
        ],
      ),
    body: <Widget>[ 
      LotsScreen(),
      InitializeScreen(),
      const ParkingPage(),
    ][currentPageIndex], // Selects current selected widget from list, passes to body ("changes" screen)
    );
  }
}