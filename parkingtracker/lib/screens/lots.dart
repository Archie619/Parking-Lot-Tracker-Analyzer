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

  // This will need to be changed to pull from backend or internal storage
  List<String> lotList = ['Engineering Lot 1', 'Engineering Lot 2', 'Rocket Stadium Lot 15'];
  
  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 227, 210, 248),
      body: ListView.separated( // Create list of lots to choose from using itemBuilder (which allows us to dynamically create it)
        itemBuilder: (BuildContext context, int index) {
          return Container(
            height: 60,
            color: Colors.lightBlue,
            child: Center(child: Text(lotList[index]))
            );
        },
        padding: const EdgeInsets.all(15), 
        separatorBuilder: (BuildContext context, int index) => const Divider(), 
        itemCount: lotList.length,
      ),
    );
  }
}