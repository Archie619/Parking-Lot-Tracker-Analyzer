// Initialize widget that will allow user to add/initialize new lots

import 'package:flutter/material.dart';
import 'package:parkingtracker/requests.dart';

// Stateful = Mutable
class InitializeScreen extends StatefulWidget {
  const InitializeScreen({super.key});

  @override
  State<InitializeScreen> createState() => _InitializeScreenState();
}

class _InitializeScreenState extends State<InitializeScreen> {

  // Create text controllers to retrieve current values of text fields
  final lotNameController = TextEditingController();
  final rtspLinkController = TextEditingController();
  final passwordController = TextEditingController();

  final Requests requests = Requests(); // Create Requests object to call functions to get data

  bool protect = true; // whether or not to protect screen.

  @override
  void dispose() {
    lotNameController.dispose();
    rtspLinkController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void submitPassword() async {
    final password = passwordController.text;
    if (password == "123") {
      protect = false;
      setState(() {}); // refresh widget
    }
  }

  // Initialize lot function, called when button pressed - pull data from both text fields, then call initLot with data.
  void initializeLot() async {
    final lotName = lotNameController.text;
    final RTSPLink = rtspLinkController.text;

    if (lotName.isNotEmpty && RTSPLink.isNotEmpty) {
      final response = await requests.initLot(lotName, RTSPLink);
      if (response != null) {
        final status = response['status'];
        var message;
        if (status == 'success') {
          message = 'Successfully initialized lot!';
        } else {
          message = response['message'];
        }
        // Show popup giving status/message of response
        showDialog(
          context: context,
          barrierDismissible: true,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Text(status), // wrap strings in text widget to display them.
              content: Text(message),
              actions: <Widget>[
                TextButton(
                  child: const Text('Okay'),
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                )
              ]
            );
          }
        );
      }
    }
  }

  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Stack (
      children: [
        Scaffold(
          backgroundColor: const Color.fromARGB(255, 227, 210, 248),
          appBar: AppBar(
            backgroundColor: Color.fromARGB(255, 86, 163, 227),
            foregroundColor: Colors.white,
            title: Text('Initialize New Lot'),
          ),
          body:Padding(
            padding: const EdgeInsets.all(16.0), 
            child: Column (
            children: [
              TextField(
                controller: lotNameController,
                decoration: InputDecoration(labelText: 'Enter Lot Name', border: OutlineInputBorder()),
              ),
              SizedBox(height:15), // space out text fields
              TextField(
                controller: rtspLinkController,
                decoration: InputDecoration(labelText: 'Enter RTSP Link', border: OutlineInputBorder()),
              ),
              SizedBox(height:30),
              ElevatedButton(
                onPressed: initializeLot,
                child: Text("Initialize Lot"))
            ],
          )
        )
        ),
        if (protect) // if protect bool true -> overlay password protection
          Scaffold(
          backgroundColor: const Color.fromARGB(255, 255, 152, 134),
          appBar: AppBar(
            backgroundColor: Color.fromARGB(255, 86, 163, 227),
            foregroundColor: Colors.white,
            title: Text('Password Required'),
          ),
          body:Padding(
            padding: const EdgeInsets.all(16.0), 
            child: Column (
            children: [
              TextField(
                controller: passwordController,
                decoration: InputDecoration(labelText: 'Enter Password', border: OutlineInputBorder()),
              ),
              SizedBox(height:15), // space out text fields
              ElevatedButton(
                onPressed: submitPassword,
                child: Text("Submit"))
            ],
          )
        )
        )
      ],
    );
    
  }
}