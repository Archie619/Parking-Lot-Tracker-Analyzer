// Lot info widget that holds simplified map of chosen parking lot and how many current available spots left.

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:parkingtracker/lot.dart';
import 'package:parkingtracker/requests.dart';

// Stateful = Mutable
class LotsInfoScreen extends StatefulWidget {
  const LotsInfoScreen({
    super.key,
    required this.lot,
  }); // Require chosen lot be sent to this widget to get info for specific lot

  final Lot lot;

  @override
  State<LotsInfoScreen> createState() => _LotsInfoScreenState();
}

class _LotsInfoScreenState extends State<LotsInfoScreen> {
  // Up-to-date lot variable (this will be updated periodically, pulls in new available spots number - the following pulls in new map)
  late Lot currentLot;
  final Requests requests =
      Requests(); // Create Requests object to call functions to get data
  late Timer timer; // Will be destroyed when widget is dismissed.

  // Color palette
  static const Color _yellow = Color(0xFFFFE79B); // header strip
  static const Color _barBg = Color(0xFF8FD6FF); // app bar
  static const Color _title = Color(0xFF3F90F0); // title text
  static const Color _blue = Color(0xFF5BA8FF); // accents
  static const Color _cream = Color(0xFFFFFFDF); // background

  // Initalize currentLot with sent data
  @override
  void initState() {
    super.initState();
    currentLot = widget.lot;
    updateLotMap();

    // Every 60 seconds, refresh data
    timer = Timer.periodic(
      const Duration(seconds: 30),
      (timer) => updateLotMap(),
    );
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
      setState(() {
        // Update lot map
        currentLot.lotMap = data;
      });
    }
  }

  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _cream,
      appBar: AppBar(
        backgroundColor: _barBg,
        centerTitle: true,
        title: Text(
          currentLot.lotName,
          style: const TextStyle(
            fontFamily: 'Merriweather',
            fontSize: 26,
            fontWeight: FontWeight.w800,
            color: _title,
          ),
        ),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Yellow strip under the app bar
          Container(height: 8, color: _yellow),

          // Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Display map here (rows of colored boxes)
                  if (currentLot.lotMap != null)
                    Column(
                      children: currentLot.lotMap!.map<Widget>((row) {
                        return Row(
                          mainAxisAlignment: MainAxisAlignment.start,
                          children: (row as List).map<Widget>((spot) {
                            final occupied = (spot as Map)['occupied'] == true;
                            return Container(
                              width: 40,
                              height: 70,
                              margin: const EdgeInsets.all(4),
                              decoration: BoxDecoration(
                                color: occupied ? Colors.red : Colors.green,
                                borderRadius: BorderRadius.circular(6),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Colors.black12,
                                    blurRadius: 2,
                                    offset: Offset(0, 1),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        );
                      }).toList(),
                    )
                  else
                    const Text(
                      'Loading lot map…',
                      style: TextStyle(
                        fontFamily: 'Merriweather',
                        fontSize: 14,
                        color: _blue,
                      ),
                    ),

                  const SizedBox(height: 12),

                  // Display spots available
                  Text(
                    (currentLot.availableSpots != null)
                        ? '${currentLot.availableSpots} spots available!'
                        : 'Loading spots…',
                    style: const TextStyle(
                      fontFamily: 'Merriweather',
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: _blue,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
