import 'package:flutter/material.dart';
import 'dart:async';

class ParkingPage extends StatefulWidget {
  const ParkingPage({super.key});

  @override
  State<ParkingPage> createState() => _ParkingPageState();
}

class _ParkingPageState extends State<ParkingPage> {
  List<String> lotData = [];
  bool isLoading = false;

  DateTime? _lastUpdated;

  // Example function to load data
  Future<void> _loadLotData() async {
    setState(() {
      isLoading = true;
    });

    await Future.delayed(const Duration(seconds: 2)); // Simulate API delay

    setState(() {
      lotData = ["Lot A: 25 spots", "Lot B: Full", "Lot C: 10 spots"];
      isLoading = false;
      _lastUpdated = DateTime.now(); // update last updated time here
    });
  }

  @override
  void initState() {
    super.initState();
    _loadLotData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Parking Lot Status'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLotData, // reloads when pressed
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // 🕒 Last Updated Time display
                if (_lastUpdated != null)
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Text(
                      "Last updated: ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}",
                      style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                    ),
                  ),
                Expanded(
                  child: ListView.builder(
                    itemCount: lotData.length,
                    itemBuilder: (context, index) {
                      return ListTile(title: Text(lotData[index]));
                    },
                  ),
                ),
              ],
            ),
    );
  }
}
